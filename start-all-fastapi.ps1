# Levanta todos los servicios FastAPI que tengan archivos que empiezan con "api_"
$basePath = Get-Location
$apis = Get-ChildItem -Recurse -Filter "api_*.py"

if ($apis.Count -eq 0) {
    Write-Host "⚠️ No se encontraron archivos api_*.py en $basePath"
    exit
}

$port = 8000

foreach ($api in $apis) {
    Write-Host "🚀 Levantando $($api.FullName) en puerto $port ..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$($api.DirectoryName)'; uvicorn $($api.BaseName):app --reload --port $port"
    $port++
}
