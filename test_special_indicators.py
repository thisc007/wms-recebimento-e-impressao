#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de Geração de Etiquetas com Indicadores Especiais
"""

from src.printer.zpl_generator import ZplGenerator

# Criar gerador
generator = ZplGenerator()

print("=" * 70)
print("TESTE DE ETIQUETAS COM INDICADORES ESPECIAIS")
print("=" * 70)

# Teste 1: Etiqueta simples (sem indicadores)
print("\n1. ETIQUETA SIMPLES (sem indicadores)")
print("-" * 70)
zpl_simple = generator.build_zpl("010000031")
print(zpl_simple)

# Teste 2: Etiqueta com CARGA PRIORITÁRIA
print("\n2. ETIQUETA COM CARGA PRIORITÁRIA")
print("-" * 70)
cargo_priority = {
    'is_priority': True,
    'requires_special_handling': False,
    'expiration_date': None,
    'handling_instructions': None
}
zpl_priority = generator.build_zpl("010000031", cargo_priority)
print(zpl_priority)

# Teste 3: Etiqueta com MANUSEIO ESPECIAL
print("\n3. ETIQUETA COM MANUSEIO ESPECIAL")
print("-" * 70)
cargo_special = {
    'is_priority': False,
    'requires_special_handling': True,
    'expiration_date': None,
    'handling_instructions': "Frágil - não empilhar"
}
zpl_special = generator.build_zpl("010000031", cargo_special)
print(zpl_special)

# Teste 4: Etiqueta com DATA DE VALIDADE
print("\n4. ETIQUETA COM DATA DE VALIDADE")
print("-" * 70)
cargo_expiration = {
    'is_priority': False,
    'requires_special_handling': False,
    'expiration_date': '2025-12-31T23:59:59.000000Z',
    'handling_instructions': None
}
zpl_expiration = generator.build_zpl("010000031", cargo_expiration)
print(zpl_expiration)

# Teste 5: Etiqueta COMPLETA (todos os indicadores)
print("\n5. ETIQUETA COMPLETA (TODOS OS INDICADORES)")
print("-" * 70)
cargo_full = {
    'is_priority': True,
    'requires_special_handling': True,
    'expiration_date': '2025-12-31T23:59:59.000000Z',
    'handling_instructions': 'Manter refrigerado'
}
zpl_full = generator.build_zpl("010000031", cargo_full)
print(zpl_full)

# Salvar exemplos em arquivos
print("\n" + "=" * 70)
print("SALVANDO EXEMPLOS EM ARQUIVOS ZPL")
print("=" * 70)

examples = [
    ("etiqueta_simples.zpl", zpl_simple, "Etiqueta simples"),
    ("etiqueta_prioritaria.zpl", zpl_priority, "Com prioridade"),
    ("etiqueta_manuseio_especial.zpl", zpl_special, "Com manuseio especial"),
    ("etiqueta_validade.zpl", zpl_expiration, "Com data de validade"),
    ("etiqueta_completa.zpl", zpl_full, "Com todos os indicadores"),
]

import os
out_dir = "out/test_indicators"
os.makedirs(out_dir, exist_ok=True)

for filename, zpl_code, description in examples:
    filepath = os.path.join(out_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(zpl_code)
    print(f"✅ {filepath} - {description}")

print("\n" + "=" * 70)
print("TESTE CONCLUÍDO!")
print("=" * 70)
print(f"\nArquivos salvos em: {out_dir}/")
print("Você pode enviar esses arquivos para a impressora Zebra para testar.")
print("\nIndicadores implementados:")
print("  ✅ *PRIORITARIA* - Quando is_priority = true")
print("  ✅ MAN.ESPECIAL - Quando requires_special_handling = true")
print("  ✅ Val:DD/MM/YYYY - Quando expiration_date informado")
print("  ✅ Instruções - Quando handling_instructions informado (truncado)")
