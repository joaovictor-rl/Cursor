@echo off
REM Roda o Cursor no Windows: .\iniciar.bat  (ou dois cliques no arquivo)
cd /d "%~dp0"

REM 1. uv: instala o Python e as bibliotecas sem precisar de nada instalado antes
if exist "%USERPROFILE%\.local\bin\uv.exe" set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul || powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

REM 2. ambiente virtual .venv com as bibliotecas do back-end
if not exist ".venv\Scripts\python.exe" uv venv .venv --python 3.12
uv pip install --quiet --python .venv\Scripts\python.exe -r backend\requirements.txt || goto erro

REM 3. site: usa o frontend\dist pronto ou compila com o Node.js
if not exist "frontend\dist\index.html" (
  where npm >nul 2>nul || (echo  Instale o Node.js em https://nodejs.org para compilar o site. & goto erro)
  pushd frontend && call npm install && call npm run build && popd
)

REM 4. abre o navegador em 3 segundos e sobe o servidor
start "" /min cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8000"
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --port 8000
goto fim

:erro
echo  Algo deu errado. Tire um print desta janela e mande no chat.
:fim
pause
