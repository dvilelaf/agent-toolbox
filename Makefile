.PHONY: format
format:
	uvx ruff check --select I --fix
	uvx ruff format


.PHONY: run_token_discovery_tool
run_token_discovery_tool:
	uv run python test_token_discovery.py


.PHONY: run_orchestrator_tool
run_orchestrator_tool:
	uv run python test_orchestrator_tool.py


.PHONY: run_dynamic_tool
run_dynamic_tool:
	uv run python test_dynamic_tool.py