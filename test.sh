#!/usr/bin/env bash
set -euo pipefail

host="http://localhost:13373"

echo "Checking the health endpoint"
curl -s "$host/health"

echo
echo "Checking the models endpoint"
curl -s "$host/v1/models"

echo
echo "Checking the proof-of-work endpoint"
curl -s "$host/v1/sentinel/pow"

echo
echo "Checking the token endpoint"
curl -s "$host/v1/sentinel/token"
