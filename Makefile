.PHONY: setup format format-check lint typecheck test validate-env security check local-up local-down local-logs clean

setup format format-check lint typecheck test validate-env security check local-up local-down local-logs:
	uv run python scripts/dev.py $@

clean:
	python scripts/dev.py $@
