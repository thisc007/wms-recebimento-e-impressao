#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demonstração da Funcionalidade de Teste de Impressoras
Mostra como usar os métodos de teste implementados
"""

import sys
import os
sys.path.append('src')

def demo_test_printer():
    """Demonstra as funcionalidades de teste de impressora"""
    try:
        from utils.printer_config import PrinterConfigManager
        
        print("🖨️ Demonstração - Teste de Impressoras Zebra GK420t")
        print("=" * 55)
        
        # Inicializar gerenciador
        pc = PrinterConfigManager()
        printers = pc.get_all_printers()
        
        print(f"\n📋 Impressoras Configuradas: {len(printers)}")
        for pid, config in printers.items():
            name = config.get('name', pid)
            conn_type = config.get('connection', {}).get('mode', 'unknown')
            enabled = "✅" if config.get('enabled', False) else "❌"
            print(f"   {enabled} {pid}: {name} ({conn_type.upper()})")
        
        print("\n🔍 Funcionalidades de Teste Disponíveis:")
        print("   1. Teste de Conectividade Básica")
        print("   2. Teste com Envio de Padrão de Impressão")
        
        # Teste de conectividade básica
        print("\n🔗 Testando Conectividade Básica...")
        for pid in printers.keys():
            if printers[pid].get('enabled', False):
                name = printers[pid].get('name', pid)
                print(f"   🔍 Testando {name}...")
                
                result = pc.test_connection(pid, send_test_pattern=False)
                status = "✅ CONECTADO" if result else "❌ FALHA"
                print(f"      {status}")
        
        # Exemplo de ZPL gerado
        print("\n📄 Exemplo de ZPL de Teste Gerado:")
        print("-" * 40)
        test_zpl = pc._generate_test_zpl()
        lines = test_zpl.split('\n')
        for i, line in enumerate(lines[:10]):  # Mostrar primeiras 10 linhas
            print(f"   {line}")
        if len(lines) > 10:
            print(f"   ... (mais {len(lines) - 10} linhas)")
        
        print("\n🎯 Como Usar no Sistema:")
        print("   1. Execute: python src/main_launcher.py --gui-debug")
        print("   2. Faça login (CPF: 12345678901)")
        print("   3. Clique em '⚙️ Configurar Impressoras'")
        print("   4. Selecione uma impressora")
        print("   5. Use '🔍 Testar Conexão' ou '🖨️ Teste com Padrão'")
        
        print("\n💡 Funcionalidades Implementadas:")
        print("   ✅ Teste de conexão TCP/IP para impressoras de rede")
        print("   ✅ Verificação de impressoras USB no Windows")
        print("   ✅ Geração automática de ZPL de teste")
        print("   ✅ Envio de padrão de teste via rede")
        print("   ✅ Envio de padrão de teste via USB (Windows)")
        print("   ✅ Interface gráfica com confirmação")
        print("   ✅ Logs detalhados de todas as operações")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        return False

def demo_test_pattern_content():
    """Mostra o conteúdo do padrão de teste"""
    try:
        from utils.printer_config import PrinterConfigManager
        
        print("\n📋 Conteúdo do Padrão de Teste:")
        print("=" * 35)
        
        pc = PrinterConfigManager()
        zpl = pc._generate_test_zpl()
        
        print("🏷️ O padrão de teste inclui:")
        print("   • Logo/ícone gráfico")
        print("   • Texto 'Teste de Impressora'")
        print("   • Data e hora atual")
        print("   • Identificação da impressora")
        print("   • Mensagem de confirmação")
        print("   • Código de barras de exemplo (123456789)")
        
        print(f"\n📏 Tamanho do ZPL: {len(zpl)} caracteres")
        print("📐 Dimensões: ~100mm x 80mm (padrão etiqueta)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sistema de Teste de Impressoras - WMS Repositorium")
    print("🎯 Zebra GK420t - USB e Rede")
    
    success1 = demo_test_printer()
    success2 = demo_test_pattern_content()
    
    if success1 and success2:
        print("\n🎉 Demonstração concluída com sucesso!")
        print("💼 Sistema pronto para testes em produção.")
    else:
        print("\n⚠️ Houve problemas na demonstração.")