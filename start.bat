@echo off
echo Sistema WMS - Recebimento e Impressao
echo ====================================
echo.
echo [1] Interface Grafica Simples (Recomendada)
echo [2] Interface Grafica com Validacao
echo [3] Interface de Linha de Comando (CLI)
echo [4] Sair
echo.
set /p choice="Escolha uma opcao (1-4): "

if "%choice%"=="1" (
    echo Iniciando interface grafica simples...
    python src\main_launcher.py --gui-simple
) else if "%choice%"=="2" (
    echo Iniciando interface grafica com validacao...
    python src\main_launcher.py --gui
) else if "%choice%"=="3" (
    echo Iniciando interface de linha de comando...
    python src\main_launcher.py --cli
) else if "%choice%"=="4" (
    echo Saindo...
    exit /b 0
) else (
    echo Opcao invalida. Iniciando interface grafica simples por padrao...
    python src\main_launcher.py --gui-simple
)

pause