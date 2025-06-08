#!/bin/bash
#docker compose exec web mypy expenses/ --show-error-codes

echo "mypy..."
docker compose exec web mypy expenses/

echo
echo "markdownlint..."
markdownlint --config .markdownlint.yaml.dist docs/*md project/*md README.md
