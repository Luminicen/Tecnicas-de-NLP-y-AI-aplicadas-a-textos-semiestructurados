param(
    [int]$BasePort = 8000,
    [string]$StartFolder = ".",
    [switch]$NewWindows
)

Write-Host "Buscando archivos .py con FastAPI en $StartFolder ..."
$pyFiles = Get-ChildItem -Path $StartFolder -Recurse -Filter *.py |
    Where-Object { $_.Name -notmatch '(^test_|requirements|readme|setup)' }

$matches = @()
foreach ($f in $pyFiles) {
    try {
        $head = Get-Content -Path $f.FullName -TotalCount 200 -Encoding UTF8 -Raw -ErrorAction Stop
        if ($head -match 'from\s+fastapi\s+import\s+FastAPI' -or $head -match 'FastAPI\(') {
            $matches += $f
        }
    } catch { }
}

if ($matches.Count -eq 0) {
    Write-Warning "No se encontraron archivos con FastAPI en $StartFolder"
    return
}

Write-Host "Se encontraron $($matches.Count) servicios FastAPI. Lanzando..."

$port = $BasePort
$launched = @()

foreach ($f in $matches) {
    # Carpeta (nombre del paquete)
    $packageName = Split-Path -Leaf $f.DirectoryName
    # Nombre del archivo sin extensión
    $moduleName  = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    # Target estilo paquete.modulo:app
    $uvicornTarget = "$packageName.$moduleName:app"

    $args = "-m uvicorn `"$uvicornTarget`" --host 0.0.0.0 --port $port"

    if ($NewWindows.IsPresent) {
        $psCommand = "python $args"
        Write-Host "Abrir ventana: $psCommand (target: $uvicornTarget) en puerto $port"
        Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$psCommand -WorkingDirectory $StartFolder
        $launched += @{Target=$uvicornTarget; Mode="NewWindow"; Port=$port}
    } else {
        $jobScript = {
            param($target, $portParam, $workDir)
            Set-Location $workDir
            python -m uvicorn "$target" --host 0.0.0.0 --port $portParam
        }
        $job = Start-Job -ScriptBlock $jobScript -ArgumentList $uvicornTarget, $port, $StartFolder
        Write-Host "Job lanzado Id=$($job.Id) target:$uvicornTarget puerto:$port"
        $launched += @{Target=$uvicornTarget; Mode="Job"; Port=$port; JobId=$job.Id}
    }

    $port++
    Start-Sleep -Milliseconds 200
}

Write-Host "Hecho. Resumen:"
foreach ($l in $launched) {
    if ($l.Mode -eq "Job") {
        Write-Host " JobId $($l.JobId) -> $($l.Target) (http://localhost:$($l.Port))"
    } else {
        Write-Host " Window   -> $($l.Target) (http://localhost:$($l.Port))"
    }
}

if (-not $NewWindows.IsPresent) {
    Write-Host "`nPara ver logs de un job: Receive-Job -Id <jobId> -Keep"
    Write-Host "Para detener un job: Stop-Job -Id <jobId> ; Remove-Job -Id <jobId>"
}
