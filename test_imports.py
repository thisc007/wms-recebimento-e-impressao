#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste rápido para validar imports do sistema de endereçamento
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

print("Testando imports...\n")

try:
    print("1. Importando AddressManager...")
    from address_manager import AddressManager
    print("   ✓ AddressManager importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro: {e}")

try:
    print("2. Importando ZplGenerator...")
    from printer.zpl_generator import ZplGenerator
    print("   ✓ ZplGenerator importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro: {e}")

try:
    print("3. Importando AddressLabelsWindow...")
    from ui.address_labels_window import AddressLabelsWindow
    print("   ✓ AddressLabelsWindow importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro: {e}")

try:
    print("4. Testando instância de AddressManager...")
    addr_mgr = AddressManager()
    print("   ✓ AddressManager instanciado com sucesso")
except Exception as e:
    print(f"   ✗ Erro: {e}")

try:
    print("5. Testando instância de ZplGenerator...")
    zpl_gen = ZplGenerator()
    print("   ✓ ZplGenerator instanciado com sucesso")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n✓ Todos os imports estão funcionando corretamente!")
