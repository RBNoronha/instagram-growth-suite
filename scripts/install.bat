@echo off
chcp 65001 >nul
:: ============================================
:: Script de Instalação - Instagram Growth Suite
:: Windows
:: ============================================

echo ╔══════════════════════════════════════════════════════════╗
echo ║  📱 Instagram Growth Suite - Instalação                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Instale o Python 3.8+ de https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado

:: Verifica pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado!
    echo Instale o pip e tente novamente.
    pause
    exit /b 1
)

echo ✅ pip encontrado

:: Cria ambiente virtual
echo.
echo 📦 Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    echo ✅ Ambiente virtual criado
) else (
    echo ⚠️  Ambiente virtual já existe
)

:: Ativa ambiente virtual
echo.
echo 🚀 Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Atualiza pip
echo.
echo ⬆️  Atualizando pip...
pip install --upgrade pip -q

:: Instala dependências
echo.
echo 📥 Instalando dependências...
pip install -r requirements.txt -q

echo ✅ Dependências instaladas

:: Cria estrutura de diretórios
echo.
echo 📁 Criando estrutura de diretórios...
if not exist "data" mkdir data
if not exist "content\images" mkdir content\images
if not exist "content\videos" mkdir content\videos
if not exist "logs" mkdir logs
if not exist "data\chrome_profile" mkdir data\chrome_profile

echo ✅ Diretórios criados

:: Cria .env se não existir
echo.
if not exist ".env" (
    echo 📝 Criando arquivo .env...
    copy .env.example .env
    echo ⚠️  Arquivo .env criado!
    echo    Edite o arquivo .env e adicione suas credenciais do Instagram
) else (
    echo ⚠️  Arquivo .env já existe
)

:: Verifica Chrome
echo.
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Chrome não encontrado!
    echo    Instale o Google Chrome de https://google.com/chrome
) else (
    echo ✅ Chrome encontrado
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ Instalação Concluída!                                ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║                                                          ║
echo ║  Próximos passos:                                        ║
echo ║  1. Edite o arquivo .env com suas credenciais           ║
echo ║  2. Coloque imagens em content\images\                  ║
echo ║  3. Execute: python main.py                             ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

pause
