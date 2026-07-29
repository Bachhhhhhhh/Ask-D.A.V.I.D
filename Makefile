.PHONY: setup format format-check lint typecheck test validate-env security check local-up local-down local-logs infra-format infra-validate infra-test infra-lint infra-security infra-plan clean

setup format format-check lint typecheck test validate-env security check local-up local-down local-logs infra-format infra-validate infra-test infra-lint infra-security infra-plan:
	uv run python scripts/dev.py $@

clean:
	python scripts/dev.py $@
