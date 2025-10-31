# Sistema WMS - Recebimento e Impressão
# Script de inicialização PowerShell

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "           Sistema WMS - Recebimento e Impressão               " -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1] Interface Gráfica Simples (Recomendada)" -ForegroundColor Green
Write-Host "[2] Interface Gráfica com Validação" -ForegroundColor Cyan
Write-Host "[3] Interface de Linha de Comando (CLI)" -ForegroundColor White
Write-Host "[4] Sair" -ForegroundColor Red
Write-Host ""

do {
    $choice = Read-Host "Escolha uma opção (1-4)"
    
    switch ($choice) {
        "1" {
            Write-Host "Iniciando interface gráfica simples..." -ForegroundColor Green
            python src\main_launcher.py --gui-simple
            break
        }
        "2" {
            Write-Host "Iniciando interface gráfica com validação..." -ForegroundColor Cyan
            python src\main_launcher.py --gui
            break
        }
        "3" {
            Write-Host "Iniciando interface de linha de comando..." -ForegroundColor Yellow
            python src\main_launcher.py --cli
            break
        }
        "4" {
            Write-Host "Saindo..." -ForegroundColor Red
            exit
        }
        default {
            Write-Host "Opção inválida. Iniciando interface gráfica simples por padrão..." -ForegroundColor Yellow
            python src\main_launcher.py --gui-simple
            break
        }
    }
} while ($true)

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")