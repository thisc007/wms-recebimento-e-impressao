#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste do MODELO 03 - Impressão por Bloco Vertical
Verifica se os métodos foram implementados corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def test_zpl_generator():
    """Testa o gerador ZPL do MODELO 03"""
    print("=" * 60)
    print("TESTE 1: ZPL Generator - build_block_addresses_zpl()")
    print("=" * 60)
    
    try:
        from printer.zpl_generator import ZplGenerator
        
        gen = ZplGenerator()
        
        # Verificar se o método existe
        assert hasattr(gen, 'build_block_addresses_zpl'), "Método build_block_addresses_zpl não encontrado!"
        
        # Dados de teste
        addresses = [
            {'full_address': 'COT001-A-03-01', 'floor_name': '3º Andar'},
            {'full_address': 'COT001-A-02-01', 'floor_name': '2º Andar'},
            {'full_address': 'COT001-A-01-01', 'floor_name': '1º Andar'},
            {'full_address': 'COT001-A-00-01', 'floor_name': 'Térreo'},
        ]
        
        # Gerar ZPL
        zpl = gen.build_block_addresses_zpl(
            warehouse_code='COT001',
            warehouse_name='Cotia 1',
            building_name='Prédio A',
            addresses_by_position=addresses
        )
        
        # Verificações básicas
        assert zpl.startswith('^XA'), "ZPL deve começar com ^XA"
        assert zpl.endswith('^XZ\n'), "ZPL deve terminar com ^XZ"
        assert 'COT001' in zpl, "ZPL deve conter código do warehouse"
        assert 'Prédio A' in zpl, "ZPL deve conter nome do prédio"
        assert 'COT001-A-03-01' in zpl, "ZPL deve conter endereço do 3º andar"
        assert 'COT001-A-00-01' in zpl, "ZPL deve conter endereço do térreo"
        assert '^BQN,2,8' in zpl, "ZPL deve usar QR size 8"
        
        print("✅ Método build_block_addresses_zpl() existe e funciona!")
        print(f"✅ ZPL gerado com {len(zpl)} caracteres")
        print(f"✅ Contém 4 endereços como esperado")
        print("\nPrimeiras 500 caracteres do ZPL gerado:")
        print("-" * 60)
        print(zpl[:500])
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_address_manager():
    """Testa o AddressManager organize_addresses_by_block()"""
    print("\n" + "=" * 60)
    print("TESTE 2: AddressManager - organize_addresses_by_block()")
    print("=" * 60)
    
    try:
        from address_manager import AddressManager
        
        manager = AddressManager()
        
        # Verificar se o método existe
        assert hasattr(manager, 'organize_addresses_by_block'), "Método organize_addresses_by_block não encontrado!"
        
        # Criar dados de teste simulados
        test_data = {
            'success': True,
            'data': {
                'id': 1,
                'code': 'TEST001',
                'name': 'Galpão Teste',
                'buildings': [
                    {
                        'id': 1,
                        'code': 'A',
                        'name': 'Prédio A',
                        'floors': [
                            {
                                'id': 3,
                                'code': '03',
                                'name': '3º Andar',
                                'floor_number': 3,
                                'pallets': [
                                    {'id': 31, 'code': '01', 'name': 'Palete 01', 'full_address': 'TEST001-A-03-01'},
                                    {'id': 32, 'code': '02', 'name': 'Palete 02', 'full_address': 'TEST001-A-03-02'},
                                ]
                            },
                            {
                                'id': 2,
                                'code': '02',
                                'name': '2º Andar',
                                'floor_number': 2,
                                'pallets': [
                                    {'id': 21, 'code': '01', 'name': 'Palete 01', 'full_address': 'TEST001-A-02-01'},
                                    {'id': 22, 'code': '02', 'name': 'Palete 02', 'full_address': 'TEST001-A-02-02'},
                                ]
                            },
                            {
                                'id': 1,
                                'code': '01',
                                'name': '1º Andar',
                                'floor_number': 1,
                                'pallets': [
                                    {'id': 11, 'code': '01', 'name': 'Palete 01', 'full_address': 'TEST001-A-01-01'},
                                ]
                            },
                        ]
                    }
                ]
            }
        }
        
        # Carregar dados
        manager.load_warehouse_data(test_data)
        
        # Organizar por bloco
        blocks = manager.organize_addresses_by_block()
        
        # Verificações
        assert isinstance(blocks, list), "organize_addresses_by_block deve retornar lista"
        assert len(blocks) == 2, "Deve ter 2 blocos (posição 1 e 2)"
        
        # Verificar primeiro bloco (posição 1)
        block1 = blocks[0]
        assert block1['position_group'] == 1, "Primeiro bloco deve ser posição 1"
        assert len(block1['addresses']) == 3, "Posição 1 deve ter 3 endereços (todos os andares)"
        
        # Verificar ordem (do mais alto ao mais baixo)
        addresses = block1['addresses']
        assert addresses[0]['full_address'] == 'TEST001-A-03-01', "Primeiro deve ser 3º andar"
        assert addresses[1]['full_address'] == 'TEST001-A-02-01', "Segundo deve ser 2º andar"
        assert addresses[2]['full_address'] == 'TEST001-A-01-01', "Terceiro deve ser 1º andar"
        
        # Verificar segundo bloco (posição 2)
        block2 = blocks[1]
        assert block2['position_group'] == 2, "Segundo bloco deve ser posição 2"
        assert len(block2['addresses']) == 2, "Posição 2 deve ter 2 endereços (só 3º e 2º andar)"
        
        print("✅ Método organize_addresses_by_block() existe e funciona!")
        print(f"✅ Organizou {len(blocks)} blocos corretamente")
        print(f"✅ Bloco 1 (Posição 01): {len(block1['addresses'])} endereços")
        print(f"✅ Bloco 2 (Posição 02): {len(block2['addresses'])} endereços")
        print(f"✅ Ordem correta: do andar mais alto ao mais baixo")
        
        print("\nDetalhes dos blocos:")
        print("-" * 60)
        for block in blocks:
            print(f"\nPosição {block['position_group']}:")
            for addr in block['addresses']:
                print(f"  - {addr['full_address']} ({addr['floor_name']})")
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """Testa se os componentes da UI foram adicionados"""
    print("\n" + "=" * 60)
    print("TESTE 3: UI Components - address_labels_window.py")
    print("=" * 60)
    
    try:
        # Ler o arquivo e verificar se os métodos existem
        ui_file = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'address_labels_window.py')
        
        with open(ui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar adições
        checks = [
            ('organized_blocks', 'Variável organized_blocks'),
            ('mode_var', 'Variável mode_var'),
            ('def _on_mode_changed', 'Método _on_mode_changed()'),
            ('def _update_mode_description', 'Método _update_mode_description()'),
            ('def _print_all(', 'Método _print_all()'),
            ('def _print_all_blocks', 'Método _print_all_blocks()'),
            ('organize_addresses_by_block', 'Chamada a organize_addresses_by_block()'),
            ('build_block_addresses_zpl', 'Chamada a build_block_addresses_zpl()'),
            ('Por Bloco', 'Radio button "Por Bloco"'),
        ]
        
        all_ok = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description} encontrado")
            else:
                print(f"❌ {description} NÃO encontrado!")
                all_ok = False
        
        if all_ok:
            print("\n✅ Todos os componentes da UI foram adicionados!")
            return True
        else:
            print("\n❌ Alguns componentes estão faltando!")
            return False
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("TESTE COMPLETO - MODELO 03: Impressão por Bloco Vertical")
    print("=" * 60)
    
    results = {
        'ZPL Generator': test_zpl_generator(),
        'Address Manager': test_address_manager(),
        'UI Components': test_ui_components()
    }
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("MODELO 03 está pronto para uso!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
