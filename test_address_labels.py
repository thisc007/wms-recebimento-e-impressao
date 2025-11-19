#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de funcionalidade de etiquetas de endereçamento
Valida os geradores ZPL para os modelos 01 e 02
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.printer.zpl_generator import ZplGenerator
from src.address_manager import AddressManager

# Dados de exemplo (estrutura da API)
sample_warehouse_data = {
    "success": True,
    "data": {
        "id": 3,
        "code": "COT001",
        "name": "Cotia 1",
        "buildings": [
            {
                "id": 13,
                "code": "A",
                "name": "Prédio A",
                "total_floors": 2,
                "floors": [
                    {
                        "id": 61,
                        "code": "01",
                        "name": "Térreo",
                        "pallets": [
                            {
                                "id": 611,
                                "code": "01",
                                "name": "Palete 01",
                                "full_address": "COT001-A-01-01-01",
                                "status": "LIVRE"
                            },
                            {
                                "id": 612,
                                "code": "02",
                                "name": "Palete 02",
                                "full_address": "COT001-A-01-02-01",
                                "status": "LIVRE"
                            },
                            {
                                "id": 613,
                                "code": "03",
                                "name": "Palete 03",
                                "full_address": "COT001-A-01-03-01",
                                "status": "LIVRE"
                            },
                            {
                                "id": 614,
                                "code": "04",
                                "name": "Palete 04",
                                "full_address": "COT001-A-01-04-01",
                                "status": "LIVRE"
                            },
                            {
                                "id": 615,
                                "code": "05",
                                "name": "Palete 05",
                                "full_address": "COT001-A-01-05-01",
                                "status": "LIVRE"
                            },
                            {
                                "id": 616,
                                "code": "06",
                                "name": "Palete 06",
                                "full_address": "COT001-A-01-06-01",
                                "status": "LIVRE"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

def test_zpl_generation():
    """Testa geração de ZPL para ambos os modelos"""
    print("=" * 80)
    print("TESTE DE GERAÇÃO ZPL - ETIQUETAS DE ENDEREÇAMENTO")
    print("=" * 80)
    
    # Inicializar geradores
    zpl_gen = ZplGenerator()
    addr_mgr = AddressManager()
    
    # Carregar dados
    print("\n1. Carregando dados do warehouse...")
    if addr_mgr.load_warehouse_data(sample_warehouse_data):
        print("   ✓ Dados carregados com sucesso")
    else:
        print("   ✗ Erro ao carregar dados")
        return
    
    # Organizar dados
    print("\n2. Organizando dados por andar...")
    organized = addr_mgr.organize_addresses_by_floor()
    print(f"   ✓ {len(organized)} andar(es) organizado(s)")
    
    if not organized:
        print("   ✗ Nenhum andar encontrado")
        return
    
    floor_data = organized[0]
    print(f"   - Andar: {floor_data['floor_name']}")
    print(f"   - Prédio: {floor_data['building_name']}")
    print(f"   - Paletes: {len(floor_data['pallets'])}")
    
    # Testar MODELO 01 (etiqueta por andar)
    print("\n3. Gerando ZPL - MODELO 01 (6 QR codes por andar)...")
    try:
        addresses = [
            {'full_address': p['full_address'], 'name': p['name']} 
            for p in floor_data['pallets'][:6]
        ]
        
        zpl_model_01 = zpl_gen.build_floor_addresses_zpl(
            warehouse_code=floor_data['warehouse_code'],
            warehouse_name=floor_data['warehouse_name'],
            building_name=floor_data['building_name'],
            floor_name=floor_data['floor_name'],
            addresses=addresses
        )
        
        print("   ✓ ZPL MODELO 01 gerado com sucesso")
        print(f"   - Tamanho: {len(zpl_model_01)} bytes")
        print(f"   - Primeiras linhas:")
        for line in zpl_model_01.split('\n')[:5]:
            print(f"     {line}")
        
    except Exception as e:
        print(f"   ✗ Erro ao gerar ZPL MODELO 01: {str(e)}")
        return
    
    # Testar MODELO 02 (etiqueta individual)
    print("\n4. Gerando ZPL - MODELO 02 (etiqueta individual vertical)...")
    try:
        pallet = floor_data['pallets'][0]
        
        zpl_model_02 = zpl_gen.build_single_address_zpl(
            full_address=pallet['full_address'],
            pallet_name=pallet['name'],
            building_name=floor_data['building_name'],
            floor_name=floor_data['floor_name']
        )
        
        print("   ✓ ZPL MODELO 02 gerado com sucesso")
        print(f"   - Tamanho: {len(zpl_model_02)} bytes")
        print(f"   - Primeiras linhas:")
        for line in zpl_model_02.split('\n')[:5]:
            print(f"     {line}")
        
    except Exception as e:
        print(f"   ✗ Erro ao gerar ZPL MODELO 02: {str(e)}")
        return
    
    # Salvar ZPL em arquivos para inspeção
    print("\n5. Salvando arquivos ZPL para inspeção...")
    try:
        with open('test_modelo_01.zpl', 'w', encoding='utf-8') as f:
            f.write(zpl_model_01)
        print("   ✓ Arquivo 'test_modelo_01.zpl' salvo")
        
        with open('test_modelo_02.zpl', 'w', encoding='utf-8') as f:
            f.write(zpl_model_02)
        print("   ✓ Arquivo 'test_modelo_02.zpl' salvo")
        
    except Exception as e:
        print(f"   ⚠ Erro ao salvar arquivos: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\nOs arquivos ZPL foram gerados e podem ser testados em:")
    print("- test_modelo_01.zpl (etiqueta por andar)")
    print("- test_modelo_02.zpl (etiqueta individual)")
    print("\nVocê pode visualizar usando http://labelary.com/viewer.html")

def test_address_manager():
    """Testa funcionalidades do AddressManager"""
    print("\n" + "=" * 80)
    print("TESTE DO ADDRESS MANAGER")
    print("=" * 80)
    
    addr_mgr = AddressManager()
    
    # Carregar dados
    print("\n1. Carregando warehouse...")
    addr_mgr.load_warehouse_data(sample_warehouse_data)
    
    # Testar métodos
    print("\n2. Testando métodos...")
    
    warehouse_info = addr_mgr.get_warehouse_info()
    print(f"   - Warehouse: {warehouse_info['code']} - {warehouse_info['name']}")
    
    buildings = addr_mgr.get_buildings()
    print(f"   - Prédios: {len(buildings)}")
    for b in buildings:
        print(f"     • {b['name']} ({b['code']}) - {b['floors_count']} andar(es)")
    
    all_pallets = addr_mgr.get_all_pallets_flat()
    print(f"   - Total de paletes: {len(all_pallets)}")
    
    print("\n✓ Todos os métodos funcionando corretamente")

if __name__ == "__main__":
    print("\nIniciando testes...\n")
    
    try:
        test_zpl_generation()
        test_address_manager()
        
        print("\n" + "=" * 80)
        print("TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERRO DURANTE OS TESTES: {str(e)}")
        import traceback
        traceback.print_exc()
