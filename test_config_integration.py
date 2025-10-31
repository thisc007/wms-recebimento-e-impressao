#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de integração do sistema de configuração de impressoras
"""

import sys
import os
sys.path.append('src')

def test_printer_config():
    """Testa o carregamento da configuração de impressoras"""
    try:
        from utils.printer_config import PrinterConfigManager
        
        print("🔧 Testando PrinterConfigManager...")
        pc = PrinterConfigManager()
        
        printers = pc.get_all_printers()
        print(f"✅ Impressoras carregadas: {len(printers)}")
        
        for pid, config in printers.items():
            print(f"   - {pid}: {config.get('name')} ({config.get('connection_type')})")
        
        return True
    except Exception as e:
        print(f"❌ Erro no PrinterConfigManager: {e}")
        return False

def test_gui_imports():
    """Testa os imports das interfaces gráficas"""
    try:
        print("\n🖥️ Testando imports GUI...")
        
        from ui.gui_simple import LoginWindowSimple
        print("✅ LoginWindowSimple importado")
        
        from ui.gui import MainWindow
        print("✅ MainWindow importado")
        
        from ui.printer_config_window import PrinterConfigWindow
        print("✅ PrinterConfigWindow importado")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos imports GUI: {e}")
        return False

def test_api_integration():
    """Testa a integração com API"""
    try:
        print("\n🌐 Testando integração API...")
        
        from api.client import APIClient
        api = APIClient()
        print("✅ APIClient inicializado")
        
        return True
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Teste de Integração do Sistema de Configuração de Impressoras")
    print("=" * 60)
    
    tests = [
        test_printer_config,
        test_gui_imports,
        test_api_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema pronto para uso.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")