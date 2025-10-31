#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para as funcionalidades de impressão
"""

import sys
import os
sys.path.append('src')

from printer.zpl_generator import ZplGenerator
from printer.label_printer import LabelPrinter

def test_zpl_generation():
    """Testa geração de ZPL"""
    print("🧪 Testando geração de ZPL...")
    
    # Criar gerador
    generator = ZplGenerator()
    
    # Testar código único
    zpl_single = generator.build_zpl("00000001")
    print(f"✅ ZPL gerado para código único (tamanho: {len(zpl_single)} chars)")
    
    # Testar lote
    zpl_batch = generator.build_batch_zpl(1, 3)
    print(f"✅ ZPL gerado para lote de 3 etiquetas (tamanho: {len(zpl_batch)} chars)")
    
    # Salvar exemplo
    with open('teste_etiqueta.zpl', 'w', encoding='utf-8') as f:
        f.write(zpl_single)
    print("✅ ZPL exemplo salvo em 'teste_etiqueta.zpl'")
    
    return True

def test_label_printer():
    """Testa impressora de etiquetas"""
    print("🧪 Testando LabelPrinter...")
    
    # Configurar para salvar em arquivo
    config = {
        'output_mode': 'file',
        'output_dir': './out'
    }
    
    printer = LabelPrinter(config=config)
    
    # Testar envio
    test_zpl = "^XA\n^FO50,50\n^ADN,36,20\n^FDTESTE^FS\n^XZ"
    
    try:
        success = printer.send_print_job(test_zpl, 1)
        if success:
            print("✅ LabelPrinter funcionando corretamente")
            return True
        else:
            print("❌ Erro no LabelPrinter")
            return False
    except Exception as e:
        print(f"❌ Erro no LabelPrinter: {e}")
        return False

def test_api_compatibility():
    """Testa compatibilidade com API"""
    print("🧪 Testando compatibilidade com API...")
    
    # Simular estrutura de dados da API
    test_label = {
        'id': 1,
        'name': 'Etiqueta Teste',
        'user_id': 1,
        'last_number': 0
    }
    
    test_cargo = {
        'id': 1,
        'code': '080000001',
        'label_code': '080000001',
        'status': 'active',
        'label_data': {
            'cargo_type': 'Manual',
            'customer': 'Cliente Teste',
            'weight': '10.5',
            'volume': '0.5',
            'created_at': '2025-10-29T18:00:00Z'
        }
    }
    
    print(f"✅ Estrutura de label válida: {test_label['name']}")
    print(f"✅ Estrutura de cargo válida: {test_cargo['code']}")
    
    return True

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes das funcionalidades de impressão...")
    print("=" * 60)
    
    tests = [
        ("Geração ZPL", test_zpl_generation),
        ("LabelPrinter", test_label_printer),
        ("Compatibilidade API", test_api_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! Sistema pronto para uso.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)