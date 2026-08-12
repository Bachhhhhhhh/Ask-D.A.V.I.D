.PHONY: setup format format-check lint typecheck test validate-env security check local-up local-down local-logs infra-format infra-preflight infra-validate infra-test infra-lint infra-security infra-plan databricks-static tf-fmt-check tf-validate tf-test tf-lint tf-security clean

setup format format-check lint typecheck test validate-env security check local-up local-down local-logs infra-format infra-preflight infra-validate infra-test infra-lint infra-security infra-plan databricks-static:
	uv run python scripts/dev.py $@

tf-fmt-check: infra-format
tf-validate: infra-validate
tf-test: infra-test
tf-lint: infra-lint
tf-security: infra-security

clean:
	python scripts/dev.py $@
