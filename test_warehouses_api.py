#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para verificar API de galpões
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/src')

from api.client import APIClient
from auth.login import LoginManager

def test_warehouses_api():
    """Testa a API de galpões"""
    
    print("=" * 60)
    print("TESTE DE API DE GALPÕES")
    print("=" * 60)
    
    # Configurar API client
    api_client = APIClient()
    
    # Fazer login
    print("\n1. Fazendo login...")
    login_manager = LoginManager(api_client)
    
    # Você pode configurar estas variáveis ou usar input
    cpf = input("Digite seu CPF (apenas números): ").strip()
    password = input("Digite sua senha: ").strip()
    
    try:
        result = login_manager.login(cpf, password)
        token = result['token']
        user_name = result['user']['name']
        
        print(f"✅ Login realizado com sucesso!")
        print(f"   Usuário: {user_name}")
        print(f"   Token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return
    
    # Testar endpoint de galpões
    print("\n2. Buscando galpões disponíveis...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Tentar endpoint público primeiro
        print("\n   Tentando: GET /public/warehouses")
        response = api_client.get('/public/warehouses', headers=headers)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Resposta: {result}")
            
            if result.get('success'):
                warehouses = result.get('data', [])
                print(f"\n✅ {len(warehouses)} galpão(s) encontrado(s):\n")
                
                for warehouse in warehouses:
                    print(f"   ID: {warehouse.get('id')}")
                    print(f"   Nome: {warehouse.get('name')}")
                    print(f"   Código: {warehouse.get('code', 'N/A')}")
                    print(f"   Endereço: {warehouse.get('address', 'N/A')}")
                    print(f"   Status: {warehouse.get('status', 'N/A')}")
                    print(f"   " + "-" * 50)
            else:
                print(f"⚠️ API retornou success=false")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar galpões: {e}")
        import traceback
        traceback.print_exc()
    
    # Tentar endpoint alternativo
    print("\n3. Tentando endpoint alternativo...")
    
    try:
        print("\n   Tentando: GET /warehouses")
        response = api_client.get('/warehouses', headers=headers)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, dict):
                if result.get('success'):
                    warehouses = result.get('data', [])
                    print(f"\n✅ {len(warehouses)} galpão(s) encontrado(s) via /warehouses")
                else:
                    print(f"⚠️ API retornou success=false")
            elif isinstance(result, list):
                print(f"\n✅ {len(result)} galpão(s) encontrado(s) via /warehouses")
                for warehouse in result[:3]:  # Mostrar apenas 3 primeiros
                    print(f"   - {warehouse.get('name')} (ID: {warehouse.get('id')})")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)


if __name__ == '__main__':
    test_warehouses_api()
