# Makefile for cursor-tools MCP server
# Simplified command interface for development tasks

PRECOMMIT := mcp_server/.venv-mcp_server/bin/pre-commit

.PHONY: setup install-hooks lint fix pre-commit clean help

help:
	@echo "🛠️ cursor-tools MCP Server Commands:"
	@echo "  make setup          - Install dependencies & hooks"
	@echo "  make install-hooks  - Install pre-commit hooks"
	@echo "  make lint           - Run all linter/audit hooks"
	@echo "  make fix            - Run all auto-fix hooks"
	@echo "  make pre-commit     - Run pre-commit on all files"
	@echo "  make clean          - Remove temporary and build files"

setup:
	cd mcp_server && pip install -r requirements.txt && pip install pre-commit && $(PRECOMMIT) install

install-hooks:
	$(PRECOMMIT) install

lint:
	$(PRECOMMIT) run --all-files

fix:
	@$(PRECOMMIT) run --all-files || ( \
		EXIT_CODE=$$?; \
		if [ $$EXIT_CODE -eq 1 ]; then \
			echo "\n✨ Auto-fixes applied! Run 'make fix' again to finalize the Quality Gate. ✨\n"; \
		else \
			echo "\n❌ Pre-commit hooks found issues that require manual attention. ❌\n"; \
			exit $$EXIT_CODE; \
		fi \
	)

pre-commit:
	@$(PRECOMMIT) run --all-files || ( \
		EXIT_CODE=$$?; \
		if [ $$EXIT_CODE -eq 1 ]; then \
			echo "\n✨ Auto-fixes applied! Run 'make pre-commit' again to finalize the Quality Gate. ✨\n"; \
		else \
			echo "\n❌ Pre-commit hooks found issues that require manual attention. ❌\n"; \
			exit $$EXIT_CODE; \
		fi \
	)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
