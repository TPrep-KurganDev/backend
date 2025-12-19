PYTHON_VERSION := 3.12
VENV ?= .venv
JOBS ?= 4

CODE = tprep

TESTS = tests

ALL = $(CODE) $(TESTS)


UNAME ?= $(shell uname)

ifeq ($(UNAME), Linux)
	INSTALL_OPTIONS=
	BEFORE_SCRIPT=echo empty
else
	MAC_INIT_CFLAGS=-Wno-unused-but-set-variable # mypycify clang-issue https://github.com/python/mypy/blob/291c39d5587d96b8f42fcebb3a6aa65e9eff1276/mypyc/build.py#L524
	INSTALL_OPTIONS=LDFLAGS="-L/usr/local/opt/openssl@1.1/lib" \
	CPPFLAGS="-I/usr/local/opt/openssl@1.1/include" \
	PYCURL_SSL_LIBRARY=openssl \
	CFLAGS="$(MAC_INIT_CFLAGS)"
	BEFORE_SCRIPT=$(VENV)/bin/python poetry_mac_init.py
endif

pre-init:
	brew install python@$(PYTHON_VERSION) gcc libsasl2 openldap libiconv graphviz libpq tmux librdkafka libxml2 libxslt

.create-venv:
	test -d $(VENV) || python$(PYTHON_VERSION) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry

init: .create-venv
	$(VENV)/bin/python -m pip install toml
	$(VENV)/bin/python poetry_mac_init.py
	LDFLAGS="-L/usr/local/opt/openssl@1.1/lib" \
	CPPFLAGS="-I/usr/local/opt/openssl@1.1/include" \
	PYCURL_SSL_LIBRARY=openssl \
	CFLAGS="$(MAC_INIT_CFLAGS)" \
	$(VENV)/bin/poetry install

clear-libs-cache:
	for lib in $(LIBS); do rm -rf $$lib/*.egg-info; done

lock: clear-libs-cache
	$(VENV)/bin/poetry lock

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f app

logs-notificator:
	docker-compose logs -f notificator

restart: down up

restart-notificator:
	docker-compose restart notificator

# Test database commands
test-db-up:
	docker-compose -f docker-compose.test.yml up -d

test-db-down:
	docker-compose -f docker-compose.test.yml down

test-db-logs:
	docker-compose -f docker-compose.test.yml logs -f test_db

test-db-restart: test-db-down test-db-up

test-db-clean:
	docker-compose -f docker-compose.test.yml down -v

test:
	$(VENV)/bin/pytest tests/unit/ -v

test-with-db: test-db-up
	@echo "Waiting for test database to be ready..."
	@sleep 3
	$(VENV)/bin/pytest tests/unit/ -v

mypy:
	$(VENV)/bin/mypy --install-types --non-interactive $(CODE) --show-traceback

pytest-lint:
	$(VENV)/bin/pytest -p deadfixtures --dead-fixtures --dup-fixtures $(TESTS)

check-lock:
	$(VENV)/bin/poetry check --lock

ruff-lint:
	$(VENV)/bin/ruff check $(ALL)

lint: ruff-lint mypy pytest-lint

parallel-lint:
	make -j $(JOBS) lint check-lock

pretty:
	$(VENV)/bin/ruff format $(ALL)
	$(VENV)/bin/ruff check $(ALL) --fix --show-fixes

plint: pretty lint
