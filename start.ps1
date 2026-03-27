# 设置编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "VC/PE PitchBook 报告自动化系统" -ForegroundColor Cyan
Write-Host "纯 MCP 方案" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

# 检查虚拟环境
$VenvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[错误] 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先运行: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 激活虚拟环境
Write-Host "[1/3] 激活虚拟环境..." -ForegroundColor Green
& .venv\Scripts\Activate.ps1

# 检查依赖
Write-Host "[2/3] 检查依赖..." -ForegroundColor Green
$null = & $VenvPython -c "import PyPDF2" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] PyPDF2 未安装，正在安装依赖..." -ForegroundColor Yellow
    & $VenvPython -m pip install -r requirements.txt
}

# 启动主程序
Write-Host "[3/3] 启动主程序..." -ForegroundColor Green
Write-Host ""
& $VenvPython main.py

Read-Host "按回车键退出"
