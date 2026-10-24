#!/usr/bin/env bash
set -euo pipefail
PROFILE="${1:-DEFAULT}"
WAREHOUSE="${2:-a25e41e310648f85}"
PRINCIPAL="$(databricks apps get minha-torre --profile "$PROFILE" --output json | python -c 'import json,sys; print(json.load(sys.stdin)["service_principal_client_id"])')"
TMP_SQL="$(mktemp)"
trap 'rm -f "$TMP_SQL"' EXIT
cat > "$TMP_SQL" <<SQL
GRANT USE CATALOG ON CATALOG lakehouse_vertice TO \`$PRINCIPAL\`;
GRANT USE SCHEMA ON SCHEMA lakehouse_vertice.gold TO \`$PRINCIPAL\`;
GRANT SELECT ON SCHEMA lakehouse_vertice.gold TO \`$PRINCIPAL\`;
GRANT USE SCHEMA ON SCHEMA lakehouse_vertice.silver TO \`$PRINCIPAL\`;
GRANT SELECT ON SCHEMA lakehouse_vertice.silver TO \`$PRINCIPAL\`;
SQL
python "$(dirname "$0")/../../scripts/run_sql.py" "$TMP_SQL" --profile "$PROFILE" --warehouse "$WAREHOUSE"
