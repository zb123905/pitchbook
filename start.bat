@echo off
REM VC/PE PitchBook Report Automation System
REM MCP Protocol Solution with QQ Mail

title VC/PE PitchBook Automation System

echo ======================================
echo VC/PE PitchBook Report Automation
echo MCP Protocol + QQ Mail Solution
echo ======================================
echo.

REM Switch to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM [Step 1/4] Check MCP configuration
echo [1/4] Checking MCP configuration...
cd mcp-mail-master

if not exist ".env" (
    echo [ERROR] .env file not found in mcp-mail-master directory
    echo Please configure .env file with your QQ mail credentials:
    echo   IMAP_USER=your_qq@qq.com
    echo   IMAP_PASS=your_16_digit_authorization_code
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] Installing Node.js dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if dist exists (compiled code)
if not exist "dist\index.js" (
    echo [INFO] Building MCP server...
    call npm run build
    if errorlevel 1 (
        echo [ERROR] Failed to build MCP server
        pause
        exit /b 1
    )
)

REM Check .env configuration
findstr /C:"your_qq@qq.com" .env >nul
if not errorlevel 1 (
    echo [WARNING] QQ Mail credentials not configured!
    echo.
    echo Please edit mcp-mail-master\.env and set:
    echo   IMAP_USER=your_qq@qq.com
    echo   IMAP_PASS=your_16_digit_authorization_code
    echo.
    echo Get authorization code from: https://mail.qq.com -^> Settings -^> Account
    pause
)

cd ..

REM [Step 2/4] Activate virtual environment
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

REM [Step 3/4] Check dependencies
echo [3/4] Checking Python dependencies...
python -c "import PyPDF2" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Python dependencies...
    pip install -r requirements.txt
)

REM [Step 4/4] Start main program
echo [4/4] Starting main program...
echo.
echo Note: Make sure MCP server is configured correctly
echo Server location: mcp-mail-master\
echo.
set PYTHONIOENCODING=utf-8
python main.py

pause
