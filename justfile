default:
    @just --list

install:
    poetry install

lock:
    poetry lock

fmt path=".":
    @echo "Formatting code in {{ path }}..."
    poetry run isort {{ path }}
    poetry run ruff format {{ path }}

lint path=".":
    @echo "Linting code in {{ path }}..."
    poetry run ruff check {{ path }}

run path="main.py":
    @echo "Running {{ path }}..."
    poetry run python {{ path }}

check path=".":
    just lint path={{ path }}
    just fmt path={{ path }}
