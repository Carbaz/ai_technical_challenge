#!/bin/bash

set -exuo pipefail

echo "Cleaning up DB..."
pipenv run python -Bm tools.cleanup_chroma

echo "Initializing DB..."
pipenv run python -Bm tools.embed_company -s policies/United -c United
pipenv run python -Bm tools.embed_company -s policies/Delta -c Delta
pipenv run python -Bm tools.embed_company -s policies/AmericanAirlines -c AmericanAirlines
