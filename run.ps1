$fullPath = Get-Location
$venvPath = Join-Path $fullPath ".venv/Scripts/python.exe"
$managePath = Join-Path $fullPath "manage.py"
$cmd = "runserver"
$runserver = "$venvPath $managePath $cmd"
Invoke-Expression $runserver
