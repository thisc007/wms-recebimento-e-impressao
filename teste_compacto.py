#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste rápido para verificar o estilo compacto
"""

import sys
import os
sys.path.append('src')

from ui.gui import LoginWindowSimple

def main():
    print("🎯 Iniciando teste do estilo COMPACTO...")
    print("✅ Interface configurada para modo compacto por padrão")
    print("📏 Características do modo compacto:")
    print("   - Janela Login: 450x350px")
    print("   - Janela Principal: 450x600px") 
    print("   - Espaçamento reduzido entre elementos")
    print("   - Fonte dos botões: Arial 11")
    print("   - Padding reduzido nos frames")
    print()
    
    # Criar janela de login já em modo compacto
    login_window = LoginWindowSimple()
    
    print("🚀 Abrindo janela de login em modo COMPACTO...")
    print("💡 Use CPF: 12345678901 e Senha: 123 para testar")
    
    login_window.run()

if __name__ == "__main__":
    main()