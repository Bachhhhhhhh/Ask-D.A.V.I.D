"""Credential-free static validation for the minimal Goal 7 integrated demo."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _read(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing Goal 7 source: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def validate_goal7_repository(repository_root: Path = REPOSITORY_ROOT) -> list[str]:
    """Return deterministic errors without contacting AWS or Databricks."""

    errors: list[str] = []
    required = (
        "infrastructure/environments/development/goal7.tf",
        "infrastructure/environments/development/goal7_variables.tf",
        "infrastructure/environments/development/goal7_secrets.tf",
        "infrastructure/environments/development/main.tf",
        "infrastructure/modules/network/main.tf",
        "infrastructure/modules/opensearch-foundation/main.tf",
        "infrastructure/modules/opensearch-foundation/variables.tf",
        "infrastructure/modules/opensearch-foundation/outputs.tf",
        "infrastructure/modules/iam/main.tf",
        "infrastructure/modules/iam/variables.tf",
        "infrastructure/modules/databricks-identities/outputs.tf",
        "infrastructure/modules/databricks-identities/variables.tf",
        "infrastructure/modules/databricks-identities/main.tf",
        "infrastructure/modules/goal7-indexer/main.tf",
        "infrastructure/modules/goal7-indexer/variables.tf",
        "infrastructure/modules/goal7-indexer/outputs.tf",
        "infrastructure/modules/goal7-demo/main.tf",
        "infrastructure/modules/goal7-demo/variables.tf",
        "infrastructure/modules/goal7-demo/outputs.tf",
        "docker/Dockerfile.goal7-indexer",
        "docker/Dockerfile.goal7-runtime",
        "docker/requirements.goal7-runtime.txt",
        "opensearch/index-mapping.json",
        "databricks/databricks.yml",
        "databricks/bundles/goal_07_retrieval/resources.yml",
        "databricks/sql/goal_07/01_prepare_document_chunks.sql",
        "databricks/sql/goal_07/02_emit_vector_index_outbox.sql",
        "databricks/sql/goal_07/03_verify_vector_payload.sql",
        "databricks/sql/goal_07/04_verify_analytics_source.sql",
        "packages/goal7-runtime/src/ask_david_goal7/contracts.py",
        "packages/goal7-runtime/src/ask_david_goal7/embedding.py",
        "packages/goal7-runtime/src/ask_david_goal7/providers.py",
        "packages/goal7-runtime/src/ask_david_goal7/services.py",
        "packages/goal7-runtime/src/ask_david_goal7/agents.py",
        "packages/goal7-runtime/src/ask_david_goal7/graph.py",
        "packages/goal7-runtime/src/ask_david_goal7/demo.py",
        "packages/goal7-runtime/src/ask_david_goal7/indexer.py",
        "packages/goal7-runtime/src/ask_david_goal7/connected.py",
        "packages/goal7-runtime/src/ask_david_goal7/connected_demo.py",
        "agents/prompts/supervisor.md",
        "agents/prompts/structured_data.md",
        "agents/prompts/unstructured_rag.md",
        "agents/prompts/analytics.md",
    )
    sources = {relative: _read(repository_root, relative, errors) for relative in required}
    if errors:
        return errors

    variables = sources["infrastructure/environments/development/goal7_variables.tf"]
    foundation = sources["infrastructure/modules/opensearch-foundation/main.tf"]
    iam = sources["infrastructure/modules/iam/main.tf"]
    iam_variables = sources["infrastructure/modules/iam/variables.tf"]
    development_main = sources["infrastructure/environments/development/main.tf"]
    network = sources["infrastructure/modules/network/main.tf"]
    goal7_network = sources["infrastructure/environments/development/goal7.tf"]
    bundle = sources["databricks/databricks.yml"]
    resources = sources["databricks/bundles/goal_07_retrieval/resources.yml"]
    sql_prepare = sources["databricks/sql/goal_07/01_prepare_document_chunks.sql"]
    sql_outbox = sources["databricks/sql/goal_07/02_emit_vector_index_outbox.sql"]
    sql_verify = sources["databricks/sql/goal_07/03_verify_vector_payload.sql"]
    sql_analytics = sources["databricks/sql/goal_07/04_verify_analytics_source.sql"]
    services = sources["packages/goal7-runtime/src/ask_david_goal7/services.py"]
    agents = sources["packages/goal7-runtime/src/ask_david_goal7/agents.py"]
    graph = sources["packages/goal7-runtime/src/ask_david_goal7/graph.py"]
    connected_demo = sources["packages/goal7-runtime/src/ask_david_goal7/connected_demo.py"]
    providers = sources["packages/goal7-runtime/src/ask_david_goal7/providers.py"]
    indexer = sources["packages/goal7-runtime/src/ask_david_goal7/indexer.py"]
    dockerfile = sources["docker/Dockerfile.goal7-indexer"]
    identity_variables = sources["infrastructure/modules/databricks-identities/variables.tf"]
    identity_main = sources["infrastructure/modules/databricks-identities/main.tf"]
    doris_variables = _read(
        repository_root,
        "infrastructure/modules/doris-serving/variables.tf",
        errors,
    )
    doris_main = _read(repository_root, "infrastructure/modules/doris-serving/main.tf", errors)
    development_goal6 = _read(
        repository_root,
        "infrastructure/environments/development/goal6.tf",
        errors,
    )

    if not re.search(r'variable\s+"goal_7_enabled"[\s\S]*?default\s*=\s*false', variables):
        errors.append("Goal 7 must be disabled by default")
    if (
        'check "goal_7_indexer_requires_foundation"' not in variables
        or "!var.goal_7_indexer_task_enabled || var.goal_7_enabled" not in variables
    ):
        errors.append("Goal 7 indexer must require the Goal 7 foundation gate")
    for marker in (
        'variable "goal_7_collection_name"',
        'variable "goal_7_vector_index_name"',
        'variable "goal_7_embedding_model_id"',
        'variable "goal_7_embedding_dimension"',
        'default     = "databricks-gte-large-en"',
        "default     = 1024",
        "var.enable_opensearch_foundation",
        'variable "goal_7_indexer_task_enabled"',
        'variable "goal_7_demo_task_enabled"',
        'variable "goal_7_indexer_image"',
        'variable "goal_7_demo_image"',
    ):
        if marker not in variables:
            errors.append(f"Goal 7 Terraform input guard is missing: {marker}")
    if not re.search(r"(?m)^\s*image\s*=\s*var\.goal_7_indexer_image$", development_main):
        errors.append("Goal 7 indexer must use its dedicated image input")
    if not re.search(r"(?m)^\s*image\s*=\s*var\.goal_7_demo_image$", development_main):
        errors.append("Goal 7 integrated demo must use its dedicated image input")
    if "var.goal_7_demo_image != null" not in variables:
        errors.append("Goal 7 integrated demo image must be required when enabled")
    if "var.goal_7_indexer_image != var.goal_7_demo_image" not in variables:
        errors.append("Goal 7 indexer and integrated demo images must not be shared")
    for marker in (
        'resource "aws_opensearchserverless_collection" "knowledge"',
        'type             = "VECTORSEARCH"',
        'resource "aws_opensearchserverless_access_policy" "knowledge"',
        'ResourceType = "index"',
        "aoss:ReadDocument",
        "aoss:WriteDocument",
        "knowledge_enabled",
    ):
        if marker not in foundation:
            errors.append(f"Goal 7 AOSS foundation is missing: {marker}")
    for marker in (
        'resource "aws_iam_role_policy" "workload_goal7_opensearch"',
        '"aoss:APIAccessAll"',
        '"aoss:collection"',
    ):
        if marker not in iam:
            errors.append(f"Goal 7 IAM data-plane gate is missing: {marker}")
    for marker in (
        'resource "aws_ecs_task_definition" "this"',
        "DATABRICKS_OAUTH_SECRET",
        "goal7-indexer",
        "ask_david_goal7.indexer",
    ):
        if marker not in sources["infrastructure/modules/goal7-indexer/main.tf"]:
            errors.append(f"Goal 7 private indexer task is missing: {marker}")
    for marker in (
        'resource "aws_ecs_task_definition" "this"',
        "DORIS_QUERY_SECRET",
        "ask_david_goal7.connected_demo",
        "GOAL7_AOSS_ENDPOINT",
    ):
        if marker not in sources["infrastructure/modules/goal7-demo/main.tf"]:
            errors.append(f"Goal 7 integrated demo task is missing: {marker}")
    for marker in (
        'resource "aws_secretsmanager_secret_version" "goal7_workflow_oauth"',
        "workflow_service_principal_secret",
        "var.goal_7_indexer_task_enabled || var.goal_7_demo_task_enabled",
    ):
        if (
            marker not in sources["infrastructure/environments/development/goal7_secrets.tf"]
            and marker not in sources["infrastructure/modules/databricks-identities/outputs.tf"]
        ):
            errors.append(f"Goal 7 workflow OAuth secret boundary is missing: {marker}")
    for marker in ("goal7_indexer_enabled", "databricks_service_principal_secret"):
        if marker not in identity_variables and marker not in identity_main:
            errors.append(f"Goal 7 workflow secret gate is missing: {marker}")
    for marker in (
        "read_outbox",
        "ensure_index",
        "bulk_upsert",
        "_find_document_id",
        "_create_document",
        "_update_document",
        "_statement_detail",
        "json.loads(value)",
        "embedding_type",
        "query_embedding",
        "AOSS request body requires explicit Content-Type",
        "AOSS vector search failed:",
        "transport failure",
        "AOSS vector search response invalid",
        "_response_shape",
        "transport_error",
        "AOSS search acceptance failed",
        "AOSS search did not return an indexed synthetic chunk",
        "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
        "Databricks workspace host must be HTTPS",
    ):
        if marker not in indexer:
            errors.append(f"Goal 7 indexer implementation is missing: {marker}")
    if '"doc_as_upsert"' in indexer:
        errors.append("Goal 7 AOSS VECTORSEARCH writes must not use doc_as_upsert")
    search_method = indexer.split("def search(", 1)[-1].split("\ndef main(", 1)[0]
    if 'body, "application/json"' not in search_method:
        errors.append("Goal 7 vector search must send JSON with an explicit content type")
    for marker in (
        "FROM python:3.12-slim",
        "USER 65532:65532",
        'ENTRYPOINT ["python", "-m", "ask_david_goal7.indexer"]',
    ):
        if marker not in dockerfile:
            errors.append(f"Goal 7 indexer image boundary is missing: {marker}")
    if "connected_demo" in dockerfile or "DORIS_FE_HOST" in dockerfile:
        errors.append("Goal 7 indexer image must not contain the Doris demo entry point")
    if "DORIS_FE_HOST" in indexer:
        errors.append("Goal 7 indexer source must not depend on Doris")
    for marker in (
        'resource "aws_security_group" "goal7_tasks"',
        'resource "aws_vpc_security_group_egress_rule" "goal7_tasks_databricks_https"',
        'resource "aws_vpc_security_group_egress_rule" "goal7_tasks_aws_endpoints"',
        'resource "aws_vpc_security_group_egress_rule" "goal7_tasks_s3"',
        'resource "aws_vpc_security_group_ingress_rule" "goal7_tasks_to_aws_endpoints"',
        'resource "aws_vpc_security_group_egress_rule" "goal7_demo_to_doris"',
        "referenced_security_group_id = module.doris_serving.fe_security_group_id",
        "goal7_task_security_group_id",
        'cidr_ipv4         = "0.0.0.0/0"',
        "module.network.s3_gateway_prefix_list_id",
    ):
        if marker not in goal7_network:
            errors.append(f"Goal 7 Premium NAT boundary is missing: {marker}")
    if "egress      = []" not in goal7_network:
        errors.append("Goal 7 dedicated task SG must have no implicit egress")
    if "ignore_changes = [egress]" not in goal7_network:
        errors.append(
            "Goal 7 dedicated task SG must ignore inline egress drift because "
            "explicit egress rules are managed separately"
        )
    if re.search(
        r"referenced_security_group_id\s*=\s*module\.network\.workload_security_group_id",
        goal7_network,
    ):
        errors.append("Goal 7 task ingress must not use the shared workload SG")
    runtime_dockerfile = sources["docker/Dockerfile.goal7-runtime"]
    runtime_requirements = sources["docker/requirements.goal7-runtime.txt"]
    for marker in ("langgraph==1.2.9", "PyMySQL==1.2.0"):
        if marker not in runtime_requirements:
            errors.append(f"Goal 7 runtime dependency is missing: {marker}")
    for marker in (
        "requirements.goal7-runtime.txt",
        "ask_david_goal7.connected_demo",
        "USER 65532:65532",
    ):
        if marker not in runtime_dockerfile:
            errors.append(f"Goal 7 runtime image boundary is missing: {marker}")
    if "goal7_enabled" not in iam_variables:
        errors.append("Goal 7 IAM module gate is missing")
    for marker in (
        'variable "goal7_secrets_enabled"',
        "count = var.goal7_secrets_enabled ? 1 : 0",
    ):
        if marker not in iam_variables and marker not in iam:
            errors.append(f"Goal 7 IAM policy count is not plan-deterministic: {marker}")
    if "goal7_secrets_enabled" not in development_main:
        errors.append("Goal 7 IAM policy must receive an explicit task gate")
    for marker in (
        'variable "data_subnet_availability_zone"',
        'variable "data_subnet_cidr_block"',
    ):
        if marker not in doris_variables:
            errors.append(f"Goal 6 subnet metadata input is missing: {marker}")
    if 'data "aws_subnet" "goal6_selected"' not in development_main:
        errors.append("Goal 6 selected subnet metadata must be resolved at the root")
    if "data_subnet_availability_zone" not in development_goal6:
        errors.append("Goal 6 module must receive plan-time subnet availability zone")
    if 'data "aws_subnet" "selected"' in doris_main:
        errors.append(
            "Goal 6 module must not defer subnet metadata behind its module dependency graph"
        )
    if development_main.count("knowledge_collection_name") != 1:
        errors.append("Goal 7 must wire one collection name into the existing foundation module")
    if "goal7/workflow-oauth" not in development_main:
        errors.append("Goal 7 indexer must use the workflow service-principal secret")
    if "doris/external-read-oauth" in development_main.split('module "goal7_indexer"', 1)[-1]:
        errors.append("Goal 7 indexer must not use the Doris external-read secret")
    if (
        'aws_vpc_security_group_ingress_rule" "goal7_indexer_to_aoss"'
        not in sources["infrastructure/environments/development/goal7.tf"]
    ):
        errors.append("Goal 7 indexer private AOSS SG boundary is missing")
    if (
        'aws_vpc_security_group_ingress_rule" "goal7_demo_to_doris"'
        not in sources["infrastructure/environments/development/goal7.tf"]
    ):
        errors.append("Goal 7 integrated demo private Doris SG boundary is missing")
    workload_endpoint_rule = re.search(
        r'resource\s+"aws_vpc_security_group_egress_rule"\s+"workload_aws_endpoints"\s*\{(?P<body>.*?)\n\}',
        network,
        flags=re.DOTALL,
    )
    if workload_endpoint_rule is None:
        errors.append("Goal 7 workload-to-AWS-endpoints egress rule is missing")
    else:
        body = workload_endpoint_rule.group("body")
        for marker in (
            "security_group_id            = aws_security_group.workload.id",
            'ip_protocol                  = "tcp"',
            "from_port                    = 443",
            "to_port                      = 443",
            "referenced_security_group_id = aws_security_group.aws_endpoints.id",
        ):
            if marker not in body:
                errors.append(f"Goal 7 workload endpoint egress rule is missing: {marker}")
        if "cidr_ipv4" in body or "cidr_blocks" in body:
            errors.append("Goal 7 workload endpoint egress must remain SG-scoped")
    workload_s3_rule = re.search(
        r'resource\s+"aws_vpc_security_group_egress_rule"\s+"workload_s3"\s*\{(?P<body>.*?)\n\}',
        network,
        flags=re.DOTALL,
    )
    if workload_s3_rule is None:
        errors.append("Goal 7 workload-to-S3-prefix-list egress rule is missing")
    else:
        body = workload_s3_rule.group("body")
        for marker in (
            "security_group_id = aws_security_group.workload.id",
            'ip_protocol       = "tcp"',
            "from_port         = 443",
            "to_port           = 443",
            "prefix_list_id    = aws_vpc_endpoint.s3.prefix_list_id",
        ):
            if marker not in body:
                errors.append(f"Goal 7 S3 egress rule is missing: {marker}")
        if any(
            marker in body
            for marker in ("cidr_ipv4", "cidr_blocks", "referenced_security_group_id")
        ):
            errors.append("Goal 7 S3 egress must remain prefix-list-scoped")
    connected = sources["packages/goal7-runtime/src/ask_david_goal7/connected.py"]
    connected_demo = sources["packages/goal7-runtime/src/ask_david_goal7/connected_demo.py"]
    for marker in (
        "DorisCliExecutor",
        "DatabricksAnalyticsExecutor",
        "DatabricksEmbeddingProvider",
        "AossVectorIndexAdapter",
        "APPROVED_ANALYTICS_DATASETS",
        "LIMIT 100",
        "required_columns",
        "Databricks analytics source response was invalid",
        "pymysql",
        "ssl.CERT_NONE",
    ):
        if marker not in connected:
            errors.append(f"Goal 7 connected service adapter is missing: {marker}")
    for marker in (
        "build_langgraph",
        "integrated-demo-completed",
        "GOAL7_AOSS_ENDPOINT",
    ):
        if marker not in connected_demo:
            errors.append(f"Goal 7 connected demo entry point is missing: {marker}")
    try:
        mapping = json.loads(sources["opensearch/index-mapping.json"])
    except json.JSONDecodeError as error:
        errors.append(f"invalid Goal 7 OpenSearch mapping: {error}")
    else:
        embedding = mapping.get("mappings", {}).get("properties", {}).get("embedding", {})
        if embedding.get("type") != "knn_vector" or embedding.get("dimension") != 1024:
            errors.append("Goal 7 mapping must contain one 1024-dimensional knn_vector")
        required_fields = {
            "chunk_id",
            "document_id",
            "title",
            "content",
            "source_uri",
            "allowed_roles",
            "embedding_model_id",
            "embedding",
        }
        if required_fields.difference(mapping.get("mappings", {}).get("properties", {})):
            errors.append("Goal 7 mapping is missing a required chunk field")

    for marker in (
        "ai_query(",
        ":embedding_model_id",
        "embedding ARRAY<FLOAT>",
        "SHA2(CONCAT(document_id",
        "ARRAY('business-reader')",
        "USING ICEBERG",
    ):
        if marker not in sql_prepare:
            errors.append(f"Goal 7 chunk SQL is missing: {marker}")
    for sql_name, text in (("prepare", sql_prepare), ("outbox", sql_outbox)):
        if re.search(r"(?im)^\s*LOCATION\s+['\"]", text):
            errors.append(f"Goal 7 {sql_name} SQL must not create unmanaged LOCATION tables")
        if "synthetic-only" not in text or "goal-07" not in text:
            errors.append(f"Goal 7 {sql_name} SQL must be explicitly synthetic-only")
    for marker in ("assert_true", "SIZE(embedding)", "source_uri", "allowed_roles"):
        if marker not in sql_verify:
            errors.append(f"Goal 7 verification SQL is missing: {marker}")
    for marker in (
        "SELECT assert_true(",
        "COUNT(DISTINCT metric_date) >= 2",
        "goal5.synthetic.events",
        "goal6.synthetic.serving.increment",
        "green_sm_business.goal5_structured_business_metrics",
    ):
        if marker not in sql_analytics:
            errors.append(f"Goal 7 analytics readiness SQL is missing: {marker}")
    if re.search(
        r"(?im)^\s*(?:CREATE|MERGE|INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE)\b",
        sql_analytics,
    ):
        errors.append("Goal 7 analytics readiness SQL must remain read-only")
    for marker in (
        "bundles/goal_07_retrieval/resources.yml",
        "sql/goal_07/*.sql",
        "goal7_embedding_model_id",
        "goal7_embedding_dimension",
    ):
        if marker not in bundle:
            errors.append(f"Goal 7 bundle root is missing: {marker}")
    for marker in (
        "goal7_document_embedding",
        "prepare_document_chunks",
        "emit_vector_index_outbox",
        "verify_vector_payload",
        "goal7_analytics_readiness",
        "verify_analytics_source",
        "04_verify_analytics_source.sql",
        "warehouse_id: ${var.warehouse_id}",
    ):
        if marker not in resources:
            errors.append(f"Goal 7 bundle resource is missing: {marker}")
    if re.search(r"(?i)\b(cluster|new_cluster|compute_key)\s*:", resources):
        errors.append("Goal 7 bundle must reuse the existing Serverless SQL Warehouse")

    if agents.count("class ") != 4:
        errors.append(
            "Goal 7 must define exactly one Supervisor and three specialized agent classes"
        )
    for name in (
        "StructuredDataAgent",
        "UnstructuredRagAgent",
        "AnalyticsAgent",
        "SupervisorAgent",
    ):
        if f"class {name}" not in agents:
            errors.append(f"Goal 7 agent module is missing {name}")
    if (
        "QueryService" not in agents
        or "RetrievalService" not in agents
        or "AnalyticsService" not in agents
    ):
        errors.append("Goal 7 agents must call controlled service boundaries")
    if (
        'provider="openai"' not in providers
        or 'provider="novita"' not in providers
        or "credential_env_var" not in providers
    ):
        errors.append(
            "Goal 7 provider configuration must assign OpenAI and Novita without static keys"
        )
    if re.search(r"(?i)\b(boto3|opensearch|databricks|mysql|psycopg|redis)\b", agents):
        errors.append("Goal 7 agents must not import or mention direct infrastructure clients")
    for marker in (
        "_FORBIDDEN_SQL",
        "APPROVED_DORIS_TABLE",
        "APPROVED_DORIS_SOURCE_TABLE",
        "APPROVED_ANALYTICS_METRIC",
        "APPROVED_ANALYTICS_DATASETS",
        "def query_metric",
        "def retrieve",
        "def compare_periods",
        "allowed_roles",
        "embedding model mismatch",
        "OpenSearchVectorIndex",
        "IndexingService",
    ):
        if marker not in services:
            errors.append(f"Goal 7 controlled services are missing: {marker}")
    for marker in (
        "StateGraph",
        'add_node("structured_data_agent"',
        'add_node("unstructured_rag_agent"',
        'add_node("analytics_agent"',
        "supervisor_synthesis",
    ):
        if marker not in graph:
            errors.append(f"Goal 7 LangGraph assembly is missing: {marker}")
    for marker in (
        "_error_category",
        "_build_agent_diagnostics",
        "_emit_agent_diagnostics",
        '"integrated-demo-agent-diagnostics"',
        '"error_present"',
        '"error_category"',
        "unclassified_error",
        "_AGENT_KEYS",
    ):
        if marker not in connected_demo:
            errors.append(f"Goal 7 integrated-demo diagnostics are missing: {marker}")
    for prompt in (
        "agents/prompts/supervisor.md",
        "agents/prompts/structured_data.md",
        "agents/prompts/unstructured_rag.md",
        "agents/prompts/analytics.md",
    ):
        prompt_text = sources[prompt]
        if "Prohibited" not in prompt_text or "Allowed" not in prompt_text:
            errors.append(f"Goal 7 prompt must declare allowed and prohibited behavior: {prompt}")
    for path, text in sources.items():
        if re.search(
            r"(?i)(aws_secret_access_key|aws_access_key_id|BEGIN PRIVATE KEY|dapi[a-z0-9]{10,})",
            text,
        ):
            errors.append(f"Goal 7 source contains a possible credential marker: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    args = parser.parse_args()
    errors = validate_goal7_repository(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Goal 7 static validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
