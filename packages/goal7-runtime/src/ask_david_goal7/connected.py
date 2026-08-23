"""Connected adapters for the one-shot Goal 7 integrated demo.

These adapters are deployment-boundary code. Agents still receive only the
typed Query/Retrieval/Analytics services; credentials and network clients stay
inside this module and are injected by the ECS task definition.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import ssl
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .contracts import ChunkRecord
from .embedding import CANONICAL_EMBEDDING_CONFIG, EmbeddingConfig, EmbeddingProvider
from .indexer import AossClient, DatabricksSqlClient, _safe_identifier, _sql_string
from .services import (
    APPROVED_ANALYTICS_DATASETS,
    APPROVED_ANALYTICS_METRIC,
    APPROVED_DORIS_TABLE,
    AnalyticsExecutor,
    DorisExecutor,
    VectorIndex,
)

_SAFE_USER_RE = re.compile(r"^[A-Za-z0-9_]{1,64}$")
_DORIS_PORT = 9030
_MAX_QUERY_SECONDS = 30


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


@dataclass(frozen=True, slots=True)
class DorisQuerySecret:
    username: str
    password: str

    @classmethod
    def from_environment(cls) -> DorisQuerySecret:
        raw = json.loads(_required("DORIS_QUERY_SECRET"))
        if not isinstance(raw, dict):
            raise RuntimeError("DORIS_QUERY_SECRET must be a JSON object")
        username = str(raw.get("username", ""))
        password = str(raw.get("password", ""))
        if not _SAFE_USER_RE.fullmatch(username) or not password:
            raise RuntimeError("DORIS_QUERY_SECRET has an invalid query identity")
        return cls(username, password)


@dataclass(slots=True)
class DorisCliExecutor(DorisExecutor):
    """TLS-only, fixed read-only Doris adapter used behind QueryService."""

    host: str
    secret: DorisQuerySecret

    @classmethod
    def from_environment(cls) -> DorisCliExecutor:
        host = _required("DORIS_FE_HOST")
        try:
            address = ipaddress.ip_address(host)
        except ValueError as error:
            raise RuntimeError("DORIS_FE_HOST must be an IP address") from error
        if not address.is_private:
            raise RuntimeError("DORIS_FE_HOST must be private")
        return cls(host, DorisQuerySecret.from_environment())

    def execute(self, sql: str) -> Iterable[Mapping[str, Any]]:
        # QueryService is the primary guard. Keep a second deployment-boundary
        # guard so a future caller cannot turn this adapter into an arbitrary
        # Doris SQL shell.
        normalized = sql.strip()
        if not normalized.lower().startswith("select ") or ";" in normalized:
            raise RuntimeError("connected Doris adapter accepts one SELECT only")
        if APPROVED_DORIS_TABLE not in normalized:
            raise RuntimeError("Doris table is outside the approved allowlist")
        if re.search(
            r"(?i)\b(?:alter|create|delete|drop|grant|insert|merge|truncate|update)\b", normalized
        ):
            raise RuntimeError("connected Doris adapter rejected a mutating statement")

        try:
            import pymysql  # type: ignore[import-not-found]
        except ImportError as error:
            raise RuntimeError("connected Goal 7 image is missing PyMySQL") from error

        tls = {
            "check_hostname": False,
            "cert_reqs": ssl.CERT_NONE,
        }
        connection = None
        try:
            connection = pymysql.connect(
                host=self.host,
                port=_DORIS_PORT,
                user=self.secret.username,
                password=self.secret.password,
                database="ask_david_serving_development",
                connect_timeout=_MAX_QUERY_SECONDS,
                read_timeout=_MAX_QUERY_SECONDS,
                write_timeout=_MAX_QUERY_SECONDS,
                ssl=tls,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
            with connection.cursor() as cursor:
                cursor.execute(normalized)
                return tuple(dict(row) for row in cursor.fetchall())
        except Exception as error:
            # Do not expose SQL, endpoint, or credential material in task logs.
            raise RuntimeError("connected Doris read-only query failed") from error
        finally:
            if connection is not None:
                connection.close()


@dataclass(slots=True)
class DatabricksAnalyticsExecutor(AnalyticsExecutor):
    """One fixed Databricks read operation for the approved synthetic metric."""

    client: DatabricksSqlClient
    catalog: str

    def read_metric_rows(self, metric_name: str) -> Iterable[Mapping[str, Any]]:
        if metric_name != APPROVED_ANALYTICS_METRIC:
            raise RuntimeError("analytics metric is outside the approved allowlist")
        catalog = _safe_identifier(self.catalog, "catalog name")
        approved_datasets = ", ".join(
            _sql_string(dataset_id) for dataset_id in APPROVED_ANALYTICS_DATASETS
        )
        sql = (
            "SELECT dataset_id, CAST(metric_date AS STRING) AS metric_date, "
            "category, event_count, metric_total "
            f"FROM {catalog}.green_sm_business.goal5_structured_business_metrics "
            f"WHERE dataset_id IN ({approved_datasets}) "
            "ORDER BY metric_date ASC, category ASC, dataset_id ASC "
            "LIMIT 100"
        )
        rows = tuple(self.client.statement(sql))
        required_columns = {
            "dataset_id",
            "metric_date",
            "category",
            "event_count",
            "metric_total",
        }
        for row in rows:
            if required_columns.difference(row):
                raise RuntimeError("Databricks analytics source response was invalid")
            if str(row.get("dataset_id", "")) not in APPROVED_ANALYTICS_DATASETS:
                raise RuntimeError("Databricks analytics source returned an unapproved dataset")
            if (
                row["metric_date"] is None
                or row["category"] is None
                or not str(row["metric_date"]).strip()
                or not str(row["category"]).strip()
            ):
                raise RuntimeError("Databricks analytics source response was invalid")
            try:
                int(row["event_count"])
                float(row["metric_total"])
            except (TypeError, ValueError) as error:
                raise RuntimeError(
                    "Databricks analytics source response was invalid"
                ) from error
        return rows


@dataclass(slots=True)
class DatabricksEmbeddingProvider(EmbeddingProvider):
    """Query-time embedding provider using the same Databricks model contract."""

    client: DatabricksSqlClient
    config: EmbeddingConfig = CANONICAL_EMBEDDING_CONFIG

    def embed(self, text: str) -> tuple[float, ...]:
        return self.client.query_embedding(self.config.model_id, text)


@dataclass(slots=True)
class AossVectorIndexAdapter(VectorIndex):
    """Controlled RetrievalService adapter over the already-indexed AOSS data."""

    client: AossClient
    index_name: str

    def upsert(self, chunks: Sequence[ChunkRecord]) -> None:
        del chunks
        raise RuntimeError("connected demo retrieval boundary does not upsert; run indexer first")

    def search(
        self,
        vector: Sequence[float],
        top_k: int,
        allowed_roles: frozenset[str],
    ) -> Iterable[tuple[ChunkRecord, float]]:
        hits = self.client.search(self.index_name, vector, next(iter(sorted(allowed_roles))))
        records: list[tuple[ChunkRecord, float]] = []
        for hit in hits[:top_k]:
            source = hit.get("_source", {})
            if not isinstance(source, dict):
                continue
            roles = tuple(str(role) for role in source.get("allowed_roles", []))
            if not allowed_roles.intersection(roles):
                continue
            record = ChunkRecord(
                chunk_id=str(source["chunk_id"]),
                document_id=str(source["document_id"]),
                title=str(source["title"]),
                content=str(source["content"]),
                source_uri=str(source["source_uri"]),
                allowed_roles=roles,
                embedding_model_id=str(source["embedding_model_id"]),
                embedding=tuple(float(value) for value in source["embedding"]),
            )
            if record.embedding_model_id != CANONICAL_EMBEDDING_CONFIG.model_id:
                raise RuntimeError("AOSS result embedding model mismatch")
            CANONICAL_EMBEDDING_CONFIG.validate(record.embedding)
            records.append((record, float(hit.get("_score", 0.0))))
        return records
