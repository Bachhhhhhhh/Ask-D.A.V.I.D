"""Private, bounded Goal 7 outbox-to-AOSS indexing entry point.

This module is intentionally a deployment-boundary adapter, not an agent tool.
It uses only ECS task-role credentials, the workflow OAuth secret injected by
ECS, one fixed Unity Catalog outbox, and one Terraform-approved AOSS index.
No credential, endpoint, or arbitrary SQL is exposed to agents.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .contracts import ChunkRecord
from .embedding import CANONICAL_EMBEDDING_CONFIG

_INDEX_NAME_RE = r"^[a-z][a-z0-9_-]{2,62}$"
_IDENTIFIER_RE = r"^[a-z][a-z0-9_]{2,62}$"
_MAX_ROWS = 100
_SQL_TIMEOUT = "30s"
_QUERY_TEXT = "supporting evidence for the synthetic technical guide"
_LOGGER = logging.getLogger(__name__)


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _json_request(
    url: str,
    *,
    method: str = "GET",
    headers: Mapping[str, str] | None = None,
    payload: Mapping[str, Any] | None = None,
    timeout: int = 30,
) -> tuple[int, Any]:
    body = None
    request_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        request_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
            raw = response.read()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raw = error.read()
        try:
            decoded: Any = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            decoded = raw.decode("utf-8", errors="replace")
        return error.code, decoded


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _safe_identifier(value: str, name: str) -> str:
    import re

    if not re.fullmatch(_IDENTIFIER_RE, value):
        raise RuntimeError(f"invalid {name}")
    return value


def _safe_index(value: str) -> str:
    import re

    if not re.fullmatch(_INDEX_NAME_RE, value):
        raise RuntimeError("invalid Goal 7 index name")
    return value


@dataclass(frozen=True, slots=True)
class DatabricksSqlClient:
    host: str
    warehouse_id: str
    client_id: str
    client_secret: str

    @classmethod
    def from_environment(cls) -> DatabricksSqlClient:
        secret = json.loads(_required("DATABRICKS_OAUTH_SECRET"))
        if not isinstance(secret, dict):
            raise RuntimeError("DATABRICKS_OAUTH_SECRET must be a JSON object")
        host = _required("DATABRICKS_WORKSPACE_HOST").rstrip("/")
        parsed_host = urllib.parse.urlsplit(host)
        if parsed_host.scheme != "https" or not parsed_host.netloc:
            raise RuntimeError("Databricks workspace host must be HTTPS")
        return cls(
            host=host,
            warehouse_id=_required("DATABRICKS_WAREHOUSE_ID"),
            client_id=str(secret["client_id"]),
            client_secret=str(secret["client_secret"]),
        )

    def _token(self) -> str:
        token_url = f"{self.host}/oidc/v1/token"
        basic = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        form = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": "all-apis"})
        request = urllib.request.Request(
            token_url,
            data=form.encode(),
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
                payload = json.loads(response.read())
        except (urllib.error.HTTPError, urllib.error.URLError) as error:
            raise RuntimeError("Databricks OAuth token request failed") from error
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Databricks OAuth response did not contain an access token")
        return token

    @staticmethod
    def _statement_detail(payload: Any) -> str:
        """Return bounded, non-secret response shape/error details."""

        if not isinstance(payload, dict):
            return f"payload_type={type(payload).__name__}"
        details: list[str] = []
        status = payload.get("status")
        if isinstance(status, dict):
            state = status.get("state")
            if isinstance(state, str):
                details.append(f"state={state}")
        error = payload.get("error")
        if isinstance(error, dict):
            for key in ("error_code", "message", "type"):
                value = error.get(key)
                if isinstance(value, str) and value:
                    details.append(f"{key}={value[:200]}")
        elif isinstance(error, str) and error:
            details.append(f"error={error[:200]}")
        result = payload.get("result")
        if isinstance(result, dict) and "data_array" in result:
            data_array = result.get("data_array")
            if isinstance(data_array, list):
                details.append(f"result_rows={len(data_array)}")
                if data_array and isinstance(data_array[0], list):
                    details.append(f"result_columns={len(data_array[0])}")
            else:
                details.append(f"data_array_type={type(data_array).__name__}")
        manifest = payload.get("manifest")
        if isinstance(manifest, dict):
            schema = manifest.get("schema")
            if isinstance(schema, dict) and isinstance(schema.get("columns"), list):
                columns = schema["columns"]
                names = [
                    str(column.get("name"))
                    for column in columns[:8]
                    if isinstance(column, dict) and column.get("name") is not None
                ]
                if names:
                    details.append(f"columns={','.join(names)}")
        return "; ".join(details)[:500] or "no response detail"

    def statement(self, sql: str) -> list[dict[str, Any]]:
        token = self._token()
        headers = {"Authorization": f"Bearer {token}"}
        status, payload = _json_request(
            f"{self.host}/api/2.0/sql/statements",
            method="POST",
            headers=headers,
            payload={
                "warehouse_id": self.warehouse_id,
                "statement": sql,
                "wait_timeout": _SQL_TIMEOUT,
                "disposition": "INLINE",
            },
        )
        if status >= 300 or not isinstance(payload, dict):
            detail = self._statement_detail(payload)
            _LOGGER.error(
                "Databricks SQL statement submission failed: status=%s; %s",
                status,
                detail,
            )
            raise RuntimeError(
                f"Databricks SQL statement submission failed: HTTP {status}; {detail}"
            )
        statement_id = payload.get("statement_id")
        status_payload = payload.get("status")
        state = status_payload.get("state") if isinstance(status_payload, dict) else None
        while state in {"PENDING", "RUNNING"}:
            if not isinstance(statement_id, str):
                raise RuntimeError("Databricks SQL response omitted statement ID")
            time.sleep(1)
            status, payload = _json_request(
                f"{self.host}/api/2.0/sql/statements/{statement_id}",
                headers=headers,
            )
            if status >= 300 or not isinstance(payload, dict):
                detail = self._statement_detail(payload)
                _LOGGER.error(
                    "Databricks SQL statement polling failed: status=%s; %s",
                    status,
                    detail,
                )
                raise RuntimeError(
                    f"Databricks SQL statement polling failed: HTTP {status}; {detail}"
                )
            status_payload = payload.get("status")
            state = status_payload.get("state") if isinstance(status_payload, dict) else None
        if state != "SUCCEEDED":
            detail = self._statement_detail(payload)
            _LOGGER.error(
                "Databricks SQL statement did not succeed: statement_id=%s; %s",
                statement_id,
                detail,
            )
            raise RuntimeError(f"Databricks SQL statement did not succeed: state={state}; {detail}")
        result = payload.get("result", {})
        manifest = payload.get("manifest", {})
        if not isinstance(result, dict) or not isinstance(manifest, dict):
            detail = self._statement_detail(payload)
            _LOGGER.error("Databricks SQL result shape invalid: %s", detail)
            raise RuntimeError(f"Databricks SQL result shape invalid: {detail}")
        schema = manifest.get("schema")
        columns = schema.get("columns", []) if isinstance(schema, dict) else []
        if not isinstance(columns, list):
            detail = self._statement_detail(payload)
            _LOGGER.error("Databricks SQL schema shape invalid: %s", detail)
            raise RuntimeError(f"Databricks SQL schema shape invalid: {detail}")
        if not all(isinstance(column, dict) and "name" in column for column in columns):
            detail = self._statement_detail(payload)
            _LOGGER.error("Databricks SQL schema columns invalid: %s", detail)
            raise RuntimeError(f"Databricks SQL schema columns invalid: {detail}")
        names = [str(column["name"]) for column in columns]
        data_array = result.get("data_array", [])
        if not isinstance(data_array, list):
            detail = self._statement_detail(payload)
            _LOGGER.error("Databricks SQL data array shape invalid: %s", detail)
            raise RuntimeError(f"Databricks SQL data array shape invalid: {detail}")
        return [dict(zip(names, row, strict=False)) for row in data_array]

    def read_outbox(self, catalog: str, collection: str, index: str) -> list[ChunkRecord]:
        catalog = _safe_identifier(catalog, "catalog name")
        index = _safe_index(index)
        sql = (
            "SELECT chunk_id, document_id, title, content, source_uri, allowed_roles, "
            "embedding_model_id, embedding "
            f"FROM {catalog}.green_sm_ai.goal7_vector_index_outbox "
            f"WHERE target_collection = {_sql_string(collection)} "
            f"AND target_index = {_sql_string(index)} "
            "ORDER BY chunk_id LIMIT 100"
        )
        records: list[ChunkRecord] = []
        for row in self.statement(sql):
            roles = row.get("allowed_roles", [])
            vector = row.get("embedding", [])
            if isinstance(roles, str):
                roles = json.loads(roles)
            if isinstance(vector, str):
                vector = json.loads(vector)
            if not isinstance(roles, list) or not isinstance(vector, list):
                raise RuntimeError("Goal 7 outbox row has invalid array fields")
            record = ChunkRecord(
                chunk_id=str(row["chunk_id"]),
                document_id=str(row["document_id"]),
                title=str(row["title"]),
                content=str(row["content"]),
                source_uri=str(row["source_uri"]),
                allowed_roles=tuple(str(role) for role in roles),
                embedding_model_id=str(row["embedding_model_id"]),
                embedding=tuple(float(value) for value in vector),
            )
            if record.embedding_model_id != CANONICAL_EMBEDDING_CONFIG.model_id:
                raise RuntimeError("Goal 7 outbox model mismatch")
            CANONICAL_EMBEDDING_CONFIG.validate(record.embedding)
            records.append(record)
        if not records:
            raise RuntimeError("Goal 7 outbox returned no chunks")
        return records[:_MAX_ROWS]

    def query_embedding(self, model_id: str, query_text: str) -> tuple[float, ...]:
        sql = (
            "SELECT CAST(ai_query("
            f"{_sql_string(model_id)}, {_sql_string(query_text)}"
            ") AS ARRAY<FLOAT>) AS embedding"
        )
        rows = self.statement(sql)
        if len(rows) != 1:
            _LOGGER.error(
                "Databricks query embedding shape invalid: row_count=%s",
                len(rows),
            )
            raise RuntimeError(
                f"Databricks query embedding response was invalid: row_count={len(rows)}"
            )
        value = rows[0].get("embedding")
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                _LOGGER.error(
                    "Databricks query embedding shape invalid: embedding_type=str, "
                    "json_parse_failed=true"
                )
                raise RuntimeError(
                    "Databricks query embedding response was invalid: embedding string is not JSON"
                ) from error
        if not isinstance(value, list):
            _LOGGER.error(
                "Databricks query embedding shape invalid: embedding_type=%s, is_null=%s",
                type(value).__name__,
                value is None,
            )
            raise RuntimeError(
                "Databricks query embedding response was invalid: "
                f"embedding_type={type(value).__name__}"
            )
        try:
            vector = tuple(float(item) for item in value)
        except (TypeError, ValueError) as error:
            _LOGGER.error("Databricks query embedding shape invalid: non_numeric_value=true")
            raise RuntimeError(
                "Databricks query embedding response was invalid: embedding is not numeric"
            ) from error
        CANONICAL_EMBEDDING_CONFIG.validate(vector)
        return vector


@dataclass(frozen=True, slots=True)
class AwsCredentials:
    access_key: str
    secret_key: str
    token: str


class AossClient:
    def __init__(self, endpoint: str, region: str) -> None:
        parsed = urllib.parse.urlsplit(endpoint.rstrip("/"))
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError("Goal 7 AOSS endpoint must be HTTPS")
        self.host = parsed.netloc
        self.base_url = f"https://{self.host}"
        self.region = region

    @staticmethod
    def _credentials() -> AwsCredentials:
        relative = os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "")
        if not relative:
            raise RuntimeError("ECS task-role credential endpoint is unavailable")
        status, payload = _json_request(f"http://169.254.170.2{relative}")
        if status >= 300 or not isinstance(payload, dict):
            raise RuntimeError("ECS task-role credentials could not be read")
        return AwsCredentials(
            access_key=str(payload["AccessKeyId"]),
            secret_key=str(payload["SecretAccessKey"]),
            token=str(payload["Token"]),
        )

    def _request(
        self,
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, Any]:
        if body and content_type is None:
            raise RuntimeError("AOSS request body requires explicit Content-Type")
        credentials = self._credentials()
        now = dt.datetime.now(dt.UTC)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        short_date = now.strftime("%Y%m%d")
        payload_hash = hashlib.sha256(body).hexdigest()
        canonical_headers = (
            f"host:{self.host}\nx-amz-content-sha256:{payload_hash}\nx-amz-date:{amz_date}\n"
        )
        signed_headers = "host;x-amz-content-sha256;x-amz-date"
        canonical_request = "\n".join(
            [method, path, "", canonical_headers, signed_headers, payload_hash]
        )
        scope = f"{short_date}/{self.region}/aoss/aws4_request"
        to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                amz_date,
                scope,
                hashlib.sha256(canonical_request.encode()).hexdigest(),
            ]
        )
        key = hmac.new(
            ("AWS4" + credentials.secret_key).encode(), short_date.encode(), hashlib.sha256
        ).digest()
        key = hmac.new(key, self.region.encode(), hashlib.sha256).digest()
        key = hmac.new(key, b"aoss", hashlib.sha256).digest()
        key = hmac.new(key, b"aws4_request", hashlib.sha256).digest()
        signature = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
        headers = {
            "Host": self.host,
            "X-Amz-Date": amz_date,
            "X-Amz-Content-SHA256": payload_hash,
            "X-Amz-Security-Token": credentials.token,
            "Authorization": (
                "AWS4-HMAC-SHA256 "
                f"Credential={credentials.access_key}/{scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}"
            ),
        }
        if content_type is not None:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=body or None, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
                raw = response.read()
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            raw = error.read()
            try:
                decoded: Any = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                decoded = raw.decode("utf-8", errors="replace")
            return error.code, decoded
        except (TimeoutError, urllib.error.URLError, OSError) as error:
            # Keep transport failures diagnosable without logging the endpoint,
            # request body, credentials, or exception text (which may contain a
            # URL). A zero status is an internal sentinel, not an HTTP status.
            return 0, {"transport_error": type(error).__name__}

    @staticmethod
    def _error_detail(payload: Any) -> str:
        """Return bounded, non-secret detail from an AOSS error response."""

        details: list[str] = []
        if isinstance(payload, dict):
            transport_error = payload.get("transport_error")
            if isinstance(transport_error, str) and transport_error:
                details.append(f"transport_error={transport_error[:80]}")
            error = payload.get("error")
            if isinstance(error, dict):
                for key in ("type", "reason"):
                    value = error.get(key)
                    if isinstance(value, str) and value:
                        details.append(f"{key}={value}")
            elif isinstance(error, str) and error:
                details.append(f"error={error}")
            items = payload.get("items")
            if isinstance(items, list):
                for item in items[:5]:
                    if not isinstance(item, dict):
                        continue
                    for result in item.values():
                        if not isinstance(result, dict):
                            continue
                        item_error = result.get("error")
                        if isinstance(item_error, dict):
                            item_type = item_error.get("type")
                            item_reason = item_error.get("reason")
                            if isinstance(item_type, str) and item_type:
                                details.append(f"type={item_type}")
                            if isinstance(item_reason, str) and item_reason:
                                details.append(f"reason={item_reason}")
                        elif isinstance(item_error, str) and item_error:
                            details.append(f"error={item_error}")
        if not details:
            return "no response detail"
        return "; ".join(details)[:500]

    @staticmethod
    def _response_shape(payload: Any) -> str:
        """Describe only JSON container types for malformed search responses."""

        if not isinstance(payload, dict):
            return f"payload_type={type(payload).__name__}"
        hits = payload.get("hits")
        if not isinstance(hits, dict):
            return f"hits_type={type(hits).__name__}"
        nested_hits = hits.get("hits")
        return f"hits_hits_type={type(nested_hits).__name__}"

    @classmethod
    def _failure(cls, operation: str, status: int, payload: Any) -> RuntimeError:
        if status == 0:
            return RuntimeError(
                f"AOSS {operation} transport failure; {cls._error_detail(payload)}"
            )
        return RuntimeError(f"AOSS {operation} failed: HTTP {status}; {cls._error_detail(payload)}")

    def ensure_index(self, index: str, mapping: Mapping[str, Any]) -> None:
        status, _ = self._request("HEAD", f"/{index}")
        if status == 200:
            return
        if status != 404:
            raise self._failure("index existence check", status, _)
        body = json.dumps(mapping, separators=(",", ":")).encode()
        status, payload = self._request("PUT", f"/{index}", body, "application/json")
        if status not in {200, 201}:
            raise self._failure("index creation", status, payload)

    @staticmethod
    def _document(chunk: ChunkRecord) -> dict[str, Any]:
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "title": chunk.title,
            "content": chunk.content,
            "source_uri": chunk.source_uri,
            "allowed_roles": list(chunk.allowed_roles),
            "embedding_model_id": chunk.embedding_model_id,
            "embedding": list(chunk.embedding),
        }

    def _find_document_id(self, index: str, chunk_id: str) -> str | None:
        body = json.dumps(
            {
                "size": 1,
                "_source": False,
                "query": {"term": {"chunk_id": chunk_id}},
            },
            separators=(",", ":"),
        ).encode()
        status, payload = self._request("POST", f"/{index}/_search", body, "application/json")
        if status == 0 or status >= 300 or not isinstance(payload, dict):
            raise self._failure("chunk lookup", status, payload)
        hits = payload.get("hits", {}).get("hits", [])
        if not isinstance(hits, list):
            raise RuntimeError("AOSS chunk lookup returned an invalid hits array")
        if not hits:
            return None
        document_id = hits[0].get("_id")
        if not isinstance(document_id, str) or not document_id:
            raise RuntimeError("AOSS chunk lookup returned no document ID")
        return document_id

    def _create_document(self, index: str, document: Mapping[str, Any]) -> None:
        body = json.dumps(document, separators=(",", ":")).encode()
        status, payload = self._request("POST", f"/{index}/_doc", body, "application/json")
        if status == 0 or status >= 300 or not isinstance(payload, dict) or not payload.get("_id"):
            raise self._failure("vector document create", status, payload)

    def _update_document(self, index: str, document_id: str, document: Mapping[str, Any]) -> None:
        # Vector collections reject doc_as_upsert/custom-ID create operations.
        # Once the generated ID is discovered by chunk_id, an existing document
        # can be updated through the supported bulk document-ID path.
        lines = [
            json.dumps({"update": {"_index": index, "_id": document_id}}),
            json.dumps({"doc": document}),
        ]
        body = ("\n".join(lines) + "\n").encode()
        status, payload = self._request("POST", f"/{index}/_bulk", body, "application/x-ndjson")
        if status == 0 or status >= 300 or not isinstance(payload, dict) or payload.get("errors"):
            raise self._failure("vector document update", status, payload)

    def bulk_upsert(self, index: str, chunks: Sequence[ChunkRecord]) -> None:
        # AOSS VECTORSEARCH collections do not support custom-ID or
        # doc_as_upsert writes. Resolve the deterministic chunk_id first, then
        # create with a generated ID or update the existing generated ID.
        for chunk in chunks:
            document = self._document(chunk)
            document_id = self._find_document_id(index, chunk.chunk_id)
            if document_id is None:
                self._create_document(index, document)
            else:
                self._update_document(index, document_id, document)

    def search(self, index: str, vector: Sequence[float], role: str) -> list[dict[str, Any]]:
        body = json.dumps(
            {
                "size": 5,
                "query": {
                    "bool": {
                        "filter": [{"terms": {"allowed_roles": [role]}}],
                        "must": [{"knn": {"embedding": {"vector": list(vector), "k": 5}}}],
                    }
                },
            },
            separators=(",", ":"),
        ).encode()
        status, payload = self._request("POST", f"/{index}/_search", body, "application/json")
        if status == 0 or status >= 300 or not isinstance(payload, dict):
            failure = self._failure("vector search", status, payload)
            _LOGGER.error("AOSS vector search failed: %s", failure)
            raise failure
        hits_container = payload.get("hits")
        hits = hits_container.get("hits") if isinstance(hits_container, dict) else None
        if not isinstance(hits, list):
            detail = self._response_shape(payload)
            _LOGGER.error(
                "AOSS vector search response invalid: status=%s; %s",
                status,
                detail,
            )
            raise RuntimeError(f"AOSS vector search response invalid: HTTP {status}; {detail}")
        return [hit for hit in hits if isinstance(hit, dict)]


def main() -> int:
    catalog = _safe_identifier(_required("GOAL7_CATALOG"), "catalog name")
    collection = _required("GOAL7_COLLECTION_NAME")
    index = _safe_index(_required("GOAL7_INDEX_NAME"))
    region = _required("AWS_REGION")
    sql = DatabricksSqlClient.from_environment()
    chunks = sql.read_outbox(catalog, collection, index)
    mapping_path = "/app/opensearch/index-mapping.json"
    with open(mapping_path, encoding="utf-8") as mapping_file:
        mapping = json.load(mapping_file)
    aoss = AossClient(_required("GOAL7_AOSS_ENDPOINT"), region)
    aoss.ensure_index(index, mapping)
    aoss.bulk_upsert(index, chunks)
    query_vector = sql.query_embedding(CANONICAL_EMBEDDING_CONFIG.model_id, _QUERY_TEXT)
    hits = aoss.search(index, query_vector, "business-reader")
    expected_ids = {chunk.chunk_id for chunk in chunks}
    matched = any(
        isinstance(hit.get("_source"), dict) and str(hit["_source"].get("chunk_id")) in expected_ids
        for hit in hits
    )
    if not matched:
        _LOGGER.error(
            "AOSS search acceptance failed: expected_chunk_count=%s; response_hit_count=%s; "
            "matched_expected_chunk=false",
            len(expected_ids),
            len(hits),
        )
        raise RuntimeError("AOSS search did not return an indexed synthetic chunk")
    print(
        json.dumps(
            {
                "goal": "goal-07",
                "status": "index-and-search-ready",
                "collection": collection,
                "index": index,
                "indexed_chunks": len(chunks),
                "search_hits": len(hits),
                "embedding_model_id": CANONICAL_EMBEDDING_CONFIG.model_id,
                "embedding_dimension": CANONICAL_EMBEDDING_CONFIG.dimension,
                "role_filter": "business-reader",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
