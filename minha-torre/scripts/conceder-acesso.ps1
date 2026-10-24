param([string]$Profile = 'DEFAULT', [string]$Warehouse = 'a25e41e310648f85')
$ErrorActionPreference = 'Stop'
$cli = (Get-Command databricks -ErrorAction Stop).Source
$app = & $cli apps get minha-torre --profile $Profile --output json | ConvertFrom-Json
$principal = $app.service_principal_client_id
if (-not $principal) { throw 'Service principal do app ainda não está disponível.' }
$sql = @"
GRANT USE CATALOG ON CATALOG lakehouse_vertice TO ``$principal``;
GRANT USE SCHEMA ON SCHEMA lakehouse_vertice.gold TO ``$principal``;
GRANT SELECT ON SCHEMA lakehouse_vertice.gold TO ``$principal``;
GRANT USE SCHEMA ON SCHEMA lakehouse_vertice.silver TO ``$principal``;
GRANT SELECT ON SCHEMA lakehouse_vertice.silver TO ``$principal``;
"@
$arquivo = Join-Path ([System.IO.Path]::GetTempPath()) "minha-torre-grants-$([guid]::NewGuid()).sql"
try {
  [System.IO.File]::WriteAllText($arquivo, $sql, [System.Text.UTF8Encoding]::new($false))
  python (Join-Path $PSScriptRoot '..\..\scripts\run_sql.py') $arquivo --profile $Profile --warehouse $Warehouse
  if ($LASTEXITCODE -ne 0) { throw "Falha ao conceder privilégios (código $LASTEXITCODE)." }
} finally { Remove-Item -LiteralPath $arquivo -Force -ErrorAction SilentlyContinue }
