PROJECTNAME := "django_sso_auth"

define HELP

Manage $(PROJECTNAME). Usage:

make lint           	Run linter
make format         	Run formatter
make test           	Run tests
make all            	Show help

endef

export HELP

help:
	@echo "$$HELP"

migrate:
	@bash ./scripts/migrate.sh

add-user:
	@bash ./scripts/add-user.sh

add-initial-data:
	@bash ./scripts/add-initial-data.sh

run-kafka:
	@bash ./scripts/run-kafka.sh

lint:
	 @bash ./scripts/lint.sh

format:
	@bash ./scripts/format.sh

test:
	@bash ./scripts/test.sh

all: help

.PHONY: help lint format test all