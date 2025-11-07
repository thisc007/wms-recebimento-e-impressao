#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Teste de listagem de impressoras"""

from src.utils.printer_config import PrinterConfigManager

# Criar gerenciador
manager = PrinterConfigManager()

# Listar impressoras
print("=" * 60)
print("TESTE DE LISTAGEM DE IMPRESSORAS")
print("=" * 60)

printers = manager.list_printers()

print(f"\nTotal de impressoras encontradas: {len(printers)}")
print()

if printers:
    for printer in printers:
        print(f"ID: {printer.get('id')}")
        print(f"Nome: {printer.get('name')}")
        print(f"Tipo: {printer.get('type')}")
        print(f"Conexão: {printer.get('connection_type')}")
        print(f"Habilitada: {printer.get('enabled')}")
        print(f"Padrão: {printer.get('is_default')}")
        print(f"Detalhes: {printer.get('connection_details')}")
        print("-" * 60)
else:
    print("Nenhuma impressora encontrada!")

print()
print("Teste concluído!")
