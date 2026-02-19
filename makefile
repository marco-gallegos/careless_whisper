PLIST_NAME = com.marcogallegos.translateapi.plist
PLIST_SRC = $(CURDIR)/$(PLIST_NAME)
PLIST_DST = $(HOME)/Library/LaunchAgents/$(PLIST_NAME)
SERVICE_LABEL = com.marcogallegos.translateapi
LOG_DIR = $(CURDIR)/logs
STDOUT_LOG = $(LOG_DIR)/stdout.log
STDERR_LOG = $(LOG_DIR)/stderr.log

.PHONY: help install uninstall load unload reload status logs logs-clear

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

install: ## Copy plist to ~/Library/LaunchAgents/
	@mkdir -p $(HOME)/Library/LaunchAgents
	@mkdir -p $(LOG_DIR)
	@cp $(PLIST_SRC) $(PLIST_DST)
	@echo "Installed $(PLIST_NAME) to ~/Library/LaunchAgents/"

uninstall: unload ## Unload and remove plist from LaunchAgents
	@rm -f $(PLIST_DST)
	@echo "Removed $(PLIST_NAME) from ~/Library/LaunchAgents/"

load: install ## Install and load the service
	@launchctl load $(PLIST_DST)
	@echo "Loaded $(PLIST_NAME)"

unload: ## Unload the service
	@launchctl unload $(PLIST_DST) 2>/dev/null || true
	@echo "Unloaded $(PLIST_NAME)"

reload: unload load ## Reload the service (unload + load)

status: ## Show service status
	@uv run scripts/status.py --label $(SERVICE_LABEL) --stdout-log $(STDOUT_LOG) --stderr-log $(STDERR_LOG)

logs: ## Show recent stdout and stderr logs
	@echo "┌──────────────────────────────────────────────┐"
	@echo "│  stdout  (last 30 lines)                     │"
	@echo "└──────────────────────────────────────────────┘"
	@tail -30 $(STDOUT_LOG) 2>/dev/null || echo "  (no stdout log yet)"
	@echo ""
	@echo "┌──────────────────────────────────────────────┐"
	@echo "│  stderr  (last 30 lines)                     │"
	@echo "└──────────────────────────────────────────────┘"
	@tail -30 $(STDERR_LOG) 2>/dev/null || echo "  (no stderr log yet)"

logs-clear: ## Clear log files
	@> $(STDOUT_LOG) 2>/dev/null; > $(STDERR_LOG) 2>/dev/null || true
	@echo "Logs cleared"
