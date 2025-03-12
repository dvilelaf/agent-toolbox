.PHONY: format
format:
	uvx ruff check --select I --fix
	uvx ruff format


.PHONY: run_token_discovery
run_token_discovery:
	uv run python test_token_discovery.py


.PHONY: run_meta_tool
run_meta_tool:
	uv run python test_meta_tool.py