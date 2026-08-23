"""Offline Goal 7 contract and integrated-demo tests."""

import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from ask_david_goal7.agents import SPECIALIZED_AGENT_NAMES
from ask_david_goal7.connected import DatabricksAnalyticsExecutor
from ask_david_goal7.connected_demo import _build_agent_diagnostics
from ask_david_goal7.contracts import (
    AgentResult,
    AnalyticsRequest,
    ChunkRecord,
    MetricQueryRequest,
    RetrievalRequest,
)
from ask_david_goal7.demo import build_offline_runtime
from ask_david_goal7.embedding import (
    CANONICAL_EMBEDDING_CONFIG,
    EmbeddingConfig,
    HashEmbeddingProvider,
)
from ask_david_goal7.indexer import (
    AossClient,
    AwsCredentials,
    DatabricksSqlClient,
    _safe_identifier,
    _safe_index,
)
from ask_david_goal7.services import (
    APPROVED_ANALYTICS_DATASETS,
    APPROVED_ANALYTICS_METRIC,
    AnalyticsService,
    IndexingService,
    InMemoryAnalyticsExecutor,
    InMemoryDorisExecutor,
    InMemoryVectorIndex,
    OpenSearchVectorIndex,
    QueryService,
    RetrievalService,
    deterministic_chunk_id,
)

from scripts.validate_goal7 import validate_goal7_repository

ROOT = Path(__file__).resolve().parents[2]
_AOSS_ERROR_PREFIX = "AOSS vector search failed: HTTP 400; type=illegal_argument; "
_AOSS_INVALID_KNN_ERROR = _AOSS_ERROR_PREFIX + "reason=invalid knn query"


def test_goal7_static_contract_passes() -> None:
    assert validate_goal7_repository(ROOT) == []


def test_goal7_connected_planability_contract_is_explicit() -> None:
    development = (ROOT / "infrastructure/environments/development/main.tf").read_text(
        encoding="utf-8"
    )
    iam = (ROOT / "infrastructure/modules/iam/main.tf").read_text(encoding="utf-8")
    doris = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")

    assert "goal7_secrets_enabled" in development
    assert "count = var.goal7_secrets_enabled ? 1 : 0" in iam
    assert 'data "aws_subnet" "selected"' not in doris


def test_goal7_indexer_and_demo_have_separate_image_contracts() -> None:
    development = (ROOT / "infrastructure/environments/development/main.tf").read_text(
        encoding="utf-8"
    )
    variables = (ROOT / "infrastructure/environments/development/goal7_variables.tf").read_text(
        encoding="utf-8"
    )
    indexer = (ROOT / "docker/Dockerfile.goal7-indexer").read_text(encoding="utf-8")
    runtime = (ROOT / "docker/Dockerfile.goal7-runtime").read_text(encoding="utf-8")
    indexer_source = (ROOT / "packages/goal7-runtime/src/ask_david_goal7/indexer.py").read_text(
        encoding="utf-8"
    )

    assert "image                      = var.goal_7_indexer_image" in development
    assert "image                       = var.goal_7_demo_image" in development
    assert 'variable "goal_7_demo_image"' in variables
    assert "var.goal_7_indexer_image != var.goal_7_demo_image" in variables
    assert 'ENTRYPOINT ["python", "-m", "ask_david_goal7.indexer"]' in indexer
    assert 'ENTRYPOINT ["python", "-m", "ask_david_goal7.connected_demo"]' in runtime
    assert "connected_demo" not in indexer
    assert "DORIS_FE_HOST" not in indexer
    assert "DORIS_FE_HOST" not in indexer_source


def test_foundation_image_includes_the_goal7_workspace_package() -> None:
    dockerfile = (ROOT / "docker/Dockerfile.foundation").read_text(encoding="utf-8")

    assert (
        "COPY packages/goal7-runtime/pyproject.toml packages/goal7-runtime/pyproject.toml"
        in dockerfile
    )
    assert "COPY packages/goal7-runtime/src packages/goal7-runtime/src" in dockerfile


def test_goal7_task_definition_modules_do_not_declare_unused_network_inputs() -> None:
    for relative in (
        "infrastructure/modules/goal7-indexer/variables.tf",
        "infrastructure/modules/goal7-demo/variables.tf",
    ):
        variables = (ROOT / relative).read_text(encoding="utf-8")
        assert 'variable "application_subnet_ids"' not in variables
        assert 'variable "workload_security_group_id"' not in variables


def test_goal7_workload_endpoint_egress_is_private_and_https_only() -> None:
    network = (ROOT / "infrastructure/modules/network/main.tf").read_text(encoding="utf-8")
    start = network.index('resource "aws_vpc_security_group_egress_rule" "workload_aws_endpoints"')
    rule = network[start : network.index("\n}", start) + 2]

    assert "security_group_id            = aws_security_group.workload.id" in rule
    assert 'ip_protocol                  = "tcp"' in rule
    assert "from_port                    = 443" in rule
    assert "to_port                      = 443" in rule
    assert "referenced_security_group_id = aws_security_group.aws_endpoints.id" in rule
    assert "cidr_ipv4" not in rule
    assert "cidr_blocks" not in rule


def test_goal7_workload_s3_egress_uses_existing_gateway_prefix_list() -> None:
    network = (ROOT / "infrastructure/modules/network/main.tf").read_text(encoding="utf-8")
    start = network.index('resource "aws_vpc_security_group_egress_rule" "workload_s3"')
    rule = network[start : network.index("\n}", start) + 2]

    assert "security_group_id = aws_security_group.workload.id" in rule
    assert 'ip_protocol       = "tcp"' in rule
    assert "from_port         = 443" in rule
    assert "to_port           = 443" in rule
    assert "prefix_list_id    = aws_vpc_endpoint.s3.prefix_list_id" in rule
    assert "cidr_ipv4" not in rule
    assert "cidr_blocks" not in rule
    assert "referenced_security_group_id" not in rule


def test_goal7_premium_nat_uses_a_dedicated_task_security_group() -> None:
    goal7 = (ROOT / "infrastructure/environments/development/goal7.tf").read_text(encoding="utf-8")
    assert 'resource "aws_security_group" "goal7_tasks"' in goal7
    assert "egress      = []" in goal7
    assert 'resource "aws_vpc_security_group_egress_rule" "goal7_tasks_databricks_https"' in goal7
    assert 'cidr_ipv4         = "0.0.0.0/0"' in goal7
    assert "existing private-subnet NAT gateway" in goal7
    assert "referenced_security_group_id = module.network.workload_security_group_id" not in goal7
    assert "module.network.s3_gateway_prefix_list_id" in goal7
    assert 'resource "aws_vpc_security_group_ingress_rule" "goal7_tasks_to_aws_endpoints"' in goal7
    assert "lifecycle" in goal7
    assert "ignore_changes = [egress]" in goal7


def test_goal7_demo_doris_path_has_sg_scoped_egress() -> None:
    goal7 = (ROOT / "infrastructure/environments/development/goal7.tf").read_text(encoding="utf-8")
    start = goal7.index('resource "aws_vpc_security_group_egress_rule" "goal7_demo_to_doris"')
    rule = goal7[start : goal7.index("\n}", start) + 2]

    assert "count = var.goal_7_demo_task_enabled ? 1 : 0" in rule
    assert "security_group_id            = local.goal7_task_security_group_id" in rule
    assert "referenced_security_group_id = module.doris_serving.fe_security_group_id" in rule
    assert 'ip_protocol                  = "tcp"' in rule
    assert "from_port                    = 9030" in rule
    assert "to_port                      = 9030" in rule
    assert "cidr_ipv4" not in rule


def test_goal7_offline_demo_routes_exactly_three_agents_and_merges_provenance() -> None:
    runtime = build_offline_runtime(ROOT)
    result = runtime.run_offline(
        "Compare the latest metric with the previous period, explain the main "
        "contributor, and provide supporting evidence."
    )

    assert result.agents_used == SPECIALIZED_AGENT_NAMES
    assert "Latest metric" in result.answer
    assert "Previous period" in result.answer
    assert "Main contributor: alpha" in result.answer
    assert "Source: s3://approved-goal5-documents/neutral_technical_guide.md" in result.answer
    assert result.structured.provenance
    assert result.analytics.provenance
    assert result.unstructured.provenance


def test_query_service_uses_the_approved_source_provenance() -> None:
    executor = InMemoryDorisExecutor(())
    QueryService(executor).query_metric(MetricQueryRequest("goal6-serving-metric", "user", "graph"))

    assert (
        "ask_david_development.green_sm_business.goal5_structured_business_metrics"
        in (executor.statements[0])
    )


def test_query_service_rejects_ddl_and_dml() -> None:
    executor = InMemoryDorisExecutor(())
    service = QueryService(executor)
    response = service.query_metric(
        MetricQueryRequest("'; DROP TABLE serving_metric_daily; --", "user", "graph")
    )

    assert response.status == "denied"
    assert executor.statements == []


def test_analytics_service_rejects_unapproved_metric() -> None:
    executor = InMemoryAnalyticsExecutor(())
    response = AnalyticsService(executor).compare_periods(
        AnalyticsRequest("other-metric", "user", "graph")
    )

    assert response.status == "error"
    assert response.error == "metric is not in the approved analytics allowlist"
    assert APPROVED_ANALYTICS_METRIC == "goal6-serving-metric"


def test_connected_analytics_reads_both_approved_period_sources_with_a_bound() -> None:
    rows = [
        {
            "dataset_id": "goal5.synthetic.events",
            "metric_date": "2026-02-01",
            "category": "alpha",
            "event_count": 1,
            "metric_total": 10.5,
        },
        {
            "dataset_id": "goal6.synthetic.serving.increment",
            "metric_date": "2026-08-13",
            "category": "synthetic-serving-increment",
            "event_count": 1,
            "metric_total": 42.0,
        },
    ]

    class FakeSqlClient:
        def __init__(self) -> None:
            self.sql = ""

        def statement(self, sql: str) -> list[dict[str, object]]:
            self.sql = sql
            return rows

    client = FakeSqlClient()
    executor = DatabricksAnalyticsExecutor(  # type: ignore[arg-type]
        client, "ask_david_development"
    )

    assert tuple(executor.read_metric_rows(APPROVED_ANALYTICS_METRIC)) == tuple(rows)
    assert APPROVED_ANALYTICS_DATASETS == (
        "goal5.synthetic.events",
        "goal6.synthetic.serving.increment",
    )
    assert (
        "dataset_id IN ('goal5.synthetic.events', "
        "'goal6.synthetic.serving.increment')" in client.sql
    )
    assert "ORDER BY metric_date ASC, category ASC, dataset_id ASC" in client.sql
    assert client.sql.endswith("LIMIT 100")
    result = AnalyticsService(executor).compare_periods(
        AnalyticsRequest(APPROVED_ANALYTICS_METRIC, "user", "graph")
    )
    assert result.status == "success"
    assert result.previous_period == "2026-02-01"
    assert result.latest_period == "2026-08-13"


def test_connected_analytics_fails_closed_for_unapproved_dataset_response() -> None:
    class FakeSqlClient:
        def statement(self, sql: str) -> list[dict[str, object]]:
            del sql
            return [
                {
                    "dataset_id": "unexpected.dataset",
                    "metric_date": "2026-08-14",
                    "category": "unexpected",
                    "event_count": 1,
                    "metric_total": 1.0,
                }
            ]

    executor = DatabricksAnalyticsExecutor(  # type: ignore[arg-type]
        FakeSqlClient(), "ask_david_development"
    )

    with pytest.raises(RuntimeError, match="unapproved dataset"):
        tuple(executor.read_metric_rows(APPROVED_ANALYTICS_METRIC))


def test_connected_analytics_fails_closed_for_invalid_response_contract() -> None:
    class FakeSqlClient:
        def statement(self, sql: str) -> list[dict[str, object]]:
            del sql
            return [
                {
                    "dataset_id": "goal5.synthetic.events",
                    "metric_date": "2026-02-01",
                    "category": "alpha",
                    "event_count": 1,
                }
            ]

    executor = DatabricksAnalyticsExecutor(  # type: ignore[arg-type]
        FakeSqlClient(), "ask_david_development"
    )

    with pytest.raises(RuntimeError, match="response was invalid"):
        tuple(executor.read_metric_rows(APPROVED_ANALYTICS_METRIC))


def test_goal7_analytics_readiness_sql_is_read_only_and_requires_two_periods() -> None:
    sql = (ROOT / "databricks/sql/goal_07/04_verify_analytics_source.sql").read_text(
        encoding="utf-8"
    )

    assert "COUNT(DISTINCT metric_date) >= 2" in sql
    assert "goal5.synthetic.events" in sql
    assert "goal6.synthetic.serving.increment" in sql
    assert sql.count("SELECT assert_true(") == 3
    assert not any(
        f"\n{keyword} " in sql.upper()
        for keyword in (
            "CREATE",
            "MERGE",
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
        )
    )


def test_goal7_analytics_readiness_job_reuses_the_existing_warehouse() -> None:
    resources = (ROOT / "databricks/bundles/goal_07_retrieval/resources.yml").read_text(
        encoding="utf-8"
    )
    readiness = resources.split("    goal7_analytics_readiness:", 1)[1]

    assert "verify_analytics_source" in readiness
    assert "04_verify_analytics_source.sql" in readiness
    assert "warehouse_id: ${var.warehouse_id}" in readiness
    assert "new_cluster:" not in readiness
    assert "existing_cluster_id:" not in readiness


def test_retrieval_filters_unauthorized_chunks() -> None:
    provider = HashEmbeddingProvider()
    index = InMemoryVectorIndex(provider)
    content = "restricted synthetic evidence"
    index.upsert(
        (
            ChunkRecord(
                deterministic_chunk_id("doc", content, 0),
                "doc",
                "Restricted",
                content,
                "s3://synthetic/restricted.md",
                ("admin",),
                CANONICAL_EMBEDDING_CONFIG.model_id,
                provider.embed(content),
            ),
        )
    )
    response = RetrievalService(index, provider).retrieve(
        RetrievalRequest("restricted evidence", 3, ("business-reader",), "user", "graph")
    )

    assert response.status == "success"
    assert response.results == ()


def test_retrieval_rejects_embedding_dimension_mismatch() -> None:
    provider = HashEmbeddingProvider(EmbeddingConfig("test-model", 4))
    index = InMemoryVectorIndex(provider)
    content = "test"
    index.upsert(
        (
            ChunkRecord(
                deterministic_chunk_id("doc", content, 0),
                "doc",
                "Test",
                content,
                "s3://synthetic/test.md",
                ("business-reader",),
                "test-model",
                provider.embed(content),
            ),
        )
    )

    class BadProvider:
        config = EmbeddingConfig("test-model", 8)

        def embed(self, text: str) -> tuple[float, ...]:
            del text
            return (0.0, 0.0, 0.0, 0.0)

    with pytest.raises(ValueError, match="dimension mismatch"):
        RetrievalService(index, BadProvider()).retrieve(
            RetrievalRequest("test", 1, ("business-reader",), "user", "graph")
        )


def test_controlled_opensearch_adapter_upserts_and_filters_vector_search() -> None:
    provider = HashEmbeddingProvider()
    content = "synthetic vector evidence"
    chunk = ChunkRecord(
        deterministic_chunk_id("doc", content, 0),
        "doc",
        "Synthetic",
        content,
        "s3://synthetic/doc.md",
        ("business-reader",),
        CANONICAL_EMBEDDING_CONFIG.model_id,
        provider.embed(content),
    )

    class FakeOpenSearchClient:
        def __init__(self) -> None:
            self.bulk_body: list[dict[str, object]] = []
            self.search_body: dict[str, object] = {}

        def bulk(self, *, body: list[dict[str, object]]) -> dict[str, object]:
            self.bulk_body = body
            return {"errors": False}

        def search(self, *, index: str, body: dict[str, object]) -> dict[str, object]:
            self.search_body = {"index": index, **body}
            return {
                "hits": {
                    "hits": [
                        {
                            "_score": 0.99,
                            "_source": {
                                "chunk_id": chunk.chunk_id,
                                "document_id": chunk.document_id,
                                "title": chunk.title,
                                "content": chunk.content,
                                "source_uri": chunk.source_uri,
                                "allowed_roles": list(chunk.allowed_roles),
                                "embedding_model_id": chunk.embedding_model_id,
                                "embedding": list(chunk.embedding),
                            },
                        }
                    ]
                }
            }

    client = FakeOpenSearchClient()
    index = OpenSearchVectorIndex(client, "synthetic-document-chunks", provider)
    IndexingService(index).upsert_chunks((chunk,))
    results = tuple(index.search(provider.embed("evidence"), 1, frozenset({"business-reader"})))

    assert client.bulk_body[0]["update"]
    assert client.search_body["index"] == "synthetic-document-chunks"
    assert results[0][0].chunk_id == chunk.chunk_id


def test_goal7_indexer_rejects_untrusted_identifiers_and_endpoints() -> None:
    with pytest.raises(RuntimeError, match="invalid catalog name"):
        _safe_identifier("catalog;DROP", "catalog name")
    with pytest.raises(RuntimeError, match="invalid Goal 7 index name"):
        _safe_index("Synthetic Chunks")
    with pytest.raises(RuntimeError, match="HTTPS"):
        AossClient("http://aoss.internal", "ap-southeast-1")


def test_goal7_index_creation_sets_json_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AossClient("https://aoss.internal", "ap-southeast-1")
    calls: list[tuple[str, str, bytes, str | None]] = []

    def fake_request(
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, object]:
        calls.append((method, path, body, content_type))
        return (404, {}) if method == "HEAD" else (201, {})

    monkeypatch.setattr(client, "_request", fake_request)
    client.ensure_index("synthetic-document-chunks", {"mappings": {}})

    assert calls[0][:2] == ("HEAD", "/synthetic-document-chunks")
    assert calls[1][0:2] == ("PUT", "/synthetic-document-chunks")
    assert calls[1][3] == "application/json"


def test_goal7_query_embedding_accepts_json_array_from_statements_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = [0.0] * CANONICAL_EMBEDDING_CONFIG.dimension
    client = DatabricksSqlClient("https://dbc.example", "warehouse", "client", "secret")

    def fake_statement(_client: DatabricksSqlClient, sql: str) -> list[dict[str, object]]:
        assert "ai_query" in sql
        return [{"embedding": json.dumps(expected)}]

    monkeypatch.setattr(DatabricksSqlClient, "statement", fake_statement)

    assert client.query_embedding("databricks-gte-large-en", "query") == tuple(expected)


def test_goal7_query_embedding_accepts_native_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = [0.0] * CANONICAL_EMBEDDING_CONFIG.dimension
    client = DatabricksSqlClient("https://dbc.example", "warehouse", "client", "secret")
    monkeypatch.setattr(
        DatabricksSqlClient,
        "statement",
        lambda _client, _sql: [{"embedding": expected}],
    )

    assert client.query_embedding("databricks-gte-large-en", "query") == tuple(expected)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (None, "embedding_type=NoneType"),
        ({"predictions": []}, "embedding_type=dict"),
        ("not-json", "embedding string is not JSON"),
    ],
)
def test_goal7_query_embedding_rejects_invalid_response_shapes(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
    message: str,
) -> None:
    client = DatabricksSqlClient("https://dbc.example", "warehouse", "client", "secret")
    monkeypatch.setattr(
        DatabricksSqlClient,
        "statement",
        lambda _client, _sql: [{"embedding": value}],
    )

    with pytest.raises(RuntimeError, match=message):
        client.query_embedding("databricks-gte-large-en", "query")


def test_goal7_query_embedding_rejects_wrong_row_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DatabricksSqlClient("https://dbc.example", "warehouse", "client", "secret")
    monkeypatch.setattr(DatabricksSqlClient, "statement", lambda _client, _sql: [])

    with pytest.raises(RuntimeError, match="row_count=0"):
        client.query_embedding("databricks-gte-large-en", "query")


def test_goal7_vector_upsert_uses_generated_ids_and_resolves_chunk_key() -> None:
    provider = HashEmbeddingProvider()
    chunk = ChunkRecord(
        "chunk-1",
        "doc-1",
        "Synthetic",
        "technical evidence",
        "s3://synthetic/doc.md",
        ("business-reader",),
        CANONICAL_EMBEDDING_CONFIG.model_id,
        provider.embed("technical evidence"),
    )
    client = AossClient("https://aoss.internal", "ap-southeast-1")
    calls: list[tuple[str, str, bytes, str | None]] = []

    def fake_request(
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, object]:
        calls.append((method, path, body, content_type))
        if path.endswith("/_search"):
            return 200, {"hits": {"hits": []}}
        if path.endswith("/_doc"):
            return 201, {"_id": "generated-id"}
        raise AssertionError(f"unexpected AOSS call: {method} {path}")

    client._request = fake_request  # type: ignore[method-assign]
    client.bulk_upsert("synthetic-document-chunks", (chunk,))

    assert [call[1] for call in calls] == [
        "/synthetic-document-chunks/_search",
        "/synthetic-document-chunks/_doc",
    ]
    assert calls[0][3] == "application/json"
    assert calls[1][3] == "application/json"
    assert b"doc_as_upsert" not in calls[1][2]


def test_goal7_vector_upsert_updates_existing_generated_id_without_upsert() -> None:
    provider = HashEmbeddingProvider()
    chunk = ChunkRecord(
        "chunk-1",
        "doc-1",
        "Synthetic",
        "technical evidence",
        "s3://synthetic/doc.md",
        ("business-reader",),
        CANONICAL_EMBEDDING_CONFIG.model_id,
        provider.embed("technical evidence"),
    )
    client = AossClient("https://aoss.internal", "ap-southeast-1")
    calls: list[tuple[str, str, bytes, str | None]] = []

    def fake_request(
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, object]:
        calls.append((method, path, body, content_type))
        if path.endswith("/_search"):
            return 200, {"hits": {"hits": [{"_id": "generated-id"}]}}
        if path.endswith("/_bulk"):
            return 200, {"errors": False, "items": [{"update": {"status": 200}}]}
        raise AssertionError(f"unexpected AOSS call: {method} {path}")

    client._request = fake_request  # type: ignore[method-assign]
    client.bulk_upsert("synthetic-document-chunks", (chunk,))

    assert [call[1] for call in calls] == [
        "/synthetic-document-chunks/_search",
        "/synthetic-document-chunks/_bulk",
    ]
    assert b"doc_as_upsert" not in calls[1][2]
    assert b'"_id": "generated-id"' in calls[1][2]


def test_goal7_aoss_search_reports_bounded_http_error() -> None:
    client = AossClient("https://aoss.internal", "ap-southeast-1")

    def fake_request(
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, object]:
        del method, path, body, content_type
        return 400, {"error": {"type": "illegal_argument", "reason": "invalid knn query"}}

    client._request = fake_request  # type: ignore[method-assign]

    with pytest.raises(
        RuntimeError,
        match=_AOSS_INVALID_KNN_ERROR,
    ):
        client.search("synthetic-document-chunks", (0.0,) * 1024, "business-reader")


def test_goal7_aoss_search_reports_bounded_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AossClient("https://aoss.internal", "ap-southeast-1")
    monkeypatch.setattr(
        client,
        "_credentials",
        lambda: AwsCredentials("access", "secret", "session"),
    )

    def fail_urlopen(*_args: object, **_kwargs: object) -> object:
        raise urllib.error.URLError("https://secret.example.invalid")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    with pytest.raises(
        RuntimeError,
        match="AOSS vector search transport failure; transport_error=URLError",
    ):
        client.search("synthetic-document-chunks", (0.0,) * 1024, "business-reader")


def test_goal7_aoss_search_accepts_valid_hits() -> None:
    client = AossClient("https://aoss.internal", "ap-southeast-1")
    calls: list[tuple[str, str, bytes, str | None]] = []

    def fake_request(
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, object]:
        calls.append((method, path, body, content_type))
        return 200, {"hits": {"hits": [{"_source": {"chunk_id": "chunk-1"}}]}}

    client._request = fake_request  # type: ignore[method-assign]

    assert client.search("synthetic-document-chunks", (0.0,) * 1024, "business-reader") == [
        {"_source": {"chunk_id": "chunk-1"}}
    ]
    assert calls[0][0:2] == ("POST", "/synthetic-document-chunks/_search")
    assert calls[0][3] == "application/json"
    assert json.loads(calls[0][2])["query"]["bool"]["filter"] == [
        {"terms": {"allowed_roles": ["business-reader"]}}
    ]


def test_goal7_aoss_request_rejects_body_without_content_type() -> None:
    client = AossClient("https://aoss.internal", "ap-southeast-1")

    with pytest.raises(RuntimeError, match="AOSS request body requires explicit Content-Type"):
        client._request("POST", "/synthetic-document-chunks/_search", b"{}")


def test_goal7_aoss_search_rejects_malformed_hits_response() -> None:
    client = AossClient("https://aoss.internal", "ap-southeast-1")

    def fake_request(
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str | None = None,
    ) -> tuple[int, object]:
        del method, path, body, content_type
        return 200, {"hits": {"total": 1}}

    client._request = fake_request  # type: ignore[method-assign]

    with pytest.raises(
        RuntimeError,
        match="AOSS vector search response invalid: HTTP 200; hits_hits_type=NoneType",
    ):
        client.search("synthetic-document-chunks", (0.0,) * 1024, "business-reader")


def test_goal7_indexer_rejects_insecure_databricks_workspace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABRICKS_OAUTH_SECRET", '{"client_id":"id","client_secret":"secret"}')
    monkeypatch.setenv("DATABRICKS_WORKSPACE_HOST", "http://workspace.internal")
    monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "warehouse")
    with pytest.raises(RuntimeError, match="Databricks workspace host must be HTTPS"):
        DatabricksSqlClient.from_environment()


def test_goal7_connected_adapters_are_static_and_service_bound() -> None:
    connected = (ROOT / "packages/goal7-runtime/src/ask_david_goal7/connected.py").read_text(
        encoding="utf-8"
    )
    demo = (ROOT / "packages/goal7-runtime/src/ask_david_goal7/connected_demo.py").read_text(
        encoding="utf-8"
    )
    assert "DorisCliExecutor" in connected
    assert "DatabricksEmbeddingProvider" in connected
    assert "AossVectorIndexAdapter" in connected
    assert "build_langgraph" in demo
    assert "integrated-demo-completed" in demo
    assert "subprocess" not in connected


def test_goal7_connected_demo_diagnostics_identify_agents_without_leaking_error_text() -> None:
    state = {
        "structured": AgentResult("Structured Data Agent", "success", "ok"),
        "unstructured": AgentResult(
            "Unstructured Data / RAG Agent",
            "error",
            "Evidence retrieval failed",
            error="AOSS request failed: https://secret.example token=do-not-log",
        ),
        "analytics": AgentResult(
            "Analytics Agent",
            "error",
            "Analytics failed",
            error="approved analytics source returned no rows",
        ),
    }

    diagnostics = _build_agent_diagnostics(state)
    encoded = json.dumps(diagnostics, sort_keys=True)

    assert diagnostics["structured"] == {
        "status": "success",
        "error_present": False,
        "error_category": None,
    }
    assert diagnostics["unstructured"] == {
        "status": "error",
        "error_present": True,
        "error_category": "aoss_error",
    }
    assert diagnostics["analytics"]["error_category"] == "analytics_no_rows"
    assert "secret.example" not in encoded
    assert "do-not-log" not in encoded
    assert "token=" not in encoded


def test_goal7_connected_demo_diagnostics_fail_closed_for_missing_agent_result() -> None:
    diagnostics = _build_agent_diagnostics({})

    assert diagnostics == {
        "structured": {
            "status": "missing",
            "error_present": False,
            "error_category": "missing_result",
        },
        "unstructured": {
            "status": "missing",
            "error_present": False,
            "error_category": "missing_result",
        },
        "analytics": {
            "status": "missing",
            "error_present": False,
            "error_category": "missing_result",
        },
    }


def test_goal7_indexer_reads_only_the_approved_outbox_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = HashEmbeddingProvider()
    chunk = ChunkRecord(
        "chunk-1",
        "doc-1",
        "Synthetic",
        "technical evidence",
        "s3://synthetic/doc.md",
        ("business-reader",),
        CANONICAL_EMBEDDING_CONFIG.model_id,
        provider.embed("technical evidence"),
    )
    rows = [
        {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "title": chunk.title,
            "content": chunk.content,
            "source_uri": chunk.source_uri,
            "allowed_roles": list(chunk.allowed_roles),
            "embedding_model_id": chunk.embedding_model_id,
            "embedding": list(chunk.embedding),
        }
    ]

    def fake_statement(self: DatabricksSqlClient, sql: str) -> list[dict[str, object]]:
        assert "goal7_vector_index_outbox" in sql
        assert "ORDER BY chunk_id LIMIT 100" in sql
        return rows

    monkeypatch.setattr(DatabricksSqlClient, "statement", fake_statement)
    client = DatabricksSqlClient("https://dbc.example", "warehouse", "client", "secret")
    result = client.read_outbox("ask_david_development", "knowledge", "synthetic-document-chunks")
    assert result == [chunk]
