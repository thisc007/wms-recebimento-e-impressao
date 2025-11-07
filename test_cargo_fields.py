#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste: Verifica se a API retorna os campos de indicadores especiais
"""

import requests
import json

# Configuração
API_BASE_URL = "http://localhost:8000/api"

# Solicitar token (você precisa usar suas credenciais)
print("=" * 70)
print("TESTE: Verificando campos de indicadores especiais na API")
print("=" * 70)
print()

# Passo 1: Login
print("1. Faça login primeiro para obter o token")
cpf = input("Digite o CPF (apenas números): ")
password = input("Digite a senha: ")

print("\n🔐 Fazendo login...")
login_response = requests.post(
    f"{API_BASE_URL}/login",
    data={'cpf': cpf, 'password': password}
)

if login_response.status_code != 200:
    print(f"❌ Erro no login: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_result = login_response.json()
if not login_result.get('success'):
    print("❌ Login falhou")
    print(login_result)
    exit(1)

token = login_result['data']['token']
print("✅ Login bem-sucedido!")
print()

# Passo 2: Buscar cargas pendentes de recebimento físico
print("2. Buscando cargas pendentes de recebimento físico...")
headers = {'Authorization': f'Bearer {token}'}

cargos_response = requests.get(
    f"{API_BASE_URL}/cargos/pending-physical-receipt",
    headers=headers,
    params={'per_page': 5}
)

if cargos_response.status_code != 200:
    print(f"❌ Erro ao buscar cargas: {cargos_response.status_code}")
    print(cargos_response.text)
    exit(1)

cargos_result = cargos_response.json()
if not cargos_result.get('success'):
    print("❌ Busca de cargas falhou")
    print(cargos_result)
    exit(1)

cargas = cargos_result.get('data', [])

if not cargas:
    print("⚠️ Nenhuma carga pendente de recebimento encontrada")
    print()
    print("💡 Dica: Certifique-se de que existem cargas no sistema com status adequado")
    exit(0)

print(f"✅ Encontradas {len(cargas)} cargas pendentes")
print()

# Passo 3: Verificar campos de cada carga
print("3. Verificando campos de indicadores especiais:")
print("=" * 70)

for i, carga in enumerate(cargas, 1):
    print(f"\n📦 CARGA {i}:")
    print(f"   Código: {carga.get('code', 'N/A')}")
    print(f"   ID: {carga.get('id', 'N/A')}")
    print()
    print("   🔍 INDICADORES ESPECIAIS:")
    print(f"      • is_priority: {carga.get('is_priority', '❌ CAMPO NÃO RETORNADO')}")
    print(f"      • requires_special_handling: {carga.get('requires_special_handling', '❌ CAMPO NÃO RETORNADO')}")
    print(f"      • expiration_date: {carga.get('expiration_date', '❌ CAMPO NÃO RETORNADO')}")
    print(f"      • handling_instructions: {carga.get('handling_instructions', '❌ CAMPO NÃO RETORNADO')}")
    print()
    
    # Verificar se TODOS os campos estão presentes
    has_priority = 'is_priority' in carga
    has_special = 'requires_special_handling' in carga
    has_expiration = 'expiration_date' in carga
    has_instructions = 'handling_instructions' in carga
    
    if has_priority and has_special and has_expiration and has_instructions:
        print("   ✅ TODOS OS CAMPOS PRESENTES!")
    else:
        print("   ⚠️ ALGUNS CAMPOS FALTANDO:")
        if not has_priority:
            print("      ❌ is_priority ausente")
        if not has_special:
            print("      ❌ requires_special_handling ausente")
        if not has_expiration:
            print("      ❌ expiration_date ausente")
        if not has_instructions:
            print("      ❌ handling_instructions ausente")
    
    print("-" * 70)

# Passo 4: Verificar resposta RAW da primeira carga
print()
print("4. Resposta RAW da API (primeira carga):")
print("=" * 70)
if cargas:
    print(json.dumps(cargas[0], indent=2, ensure_ascii=False))

print()
print("=" * 70)
print("TESTE CONCLUÍDO!")
print("=" * 70)
print()
print("💡 INTERPRETAÇÃO DOS RESULTADOS:")
print()
print("✅ Se todos os campos aparecem: A API está retornando corretamente")
print("   → O sistema de impressão deve funcionar normalmente")
print()
print("❌ Se campos faltam: A API NÃO está retornando os indicadores")
print("   → Você precisa atualizar o backend para incluir esses campos no retorno")
print("   → Exemplo: No controller Laravel, adicione os campos ao select/with")
print()
print("📝 CAMPOS NECESSÁRIOS no backend:")
print("   • is_priority (boolean)")
print("   • requires_special_handling (boolean)")
print("   • expiration_date (date/datetime nullable)")
print("   • handling_instructions (text nullable)")
