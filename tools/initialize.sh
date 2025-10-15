#!/bin/bash

# set -exuo pipefail

echo "Cleaning up DB..."
python -Bm tools.cleanup_chroma

echo "Initializing DB..."
python -Bm tools.embed_company -s policies/United -c United
python -Bm tools.embed_company -s policies/Delta -c Delta
python -Bm tools.embed_company -s policies/AmericanAirlines -c AmericanAirlines
