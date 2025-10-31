"""
Demonstração dos diferentes estilos de espaçamento da interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.gui import LoginWindowSimple, MainWindow
from src.utils.logger import setup_logger

def demo_login_styles():
    """Demonstra os diferentes estilos de espaçamento da tela de login"""
    
    print("=== Demo: Estilos de Espaçamento da Tela de Login ===")
    print("1. Estilo Compacto")
    print("2. Estilo Normal (Padrão)")  
    print("3. Estilo Espaçoso")
    
    choice = input("Escolha um estilo (1-3): ")
    
    setup_logger()
    login_window = LoginWindowSimple()
    
    if choice == '1':
        login_window.set_spacing_style('compact')
        login_window.root.title("WMS - Login (Compacto)")
        login_window.root.geometry("450x350")
    elif choice == '3':
        login_window.set_spacing_style('spacious')
        login_window.root.title("WMS - Login (Espaçoso)")
        login_window.root.geometry("550x500")
    else:
        # Usar estilo normal (padrão)
        login_window.root.title("WMS - Login (Normal)")
    
    login_window.center_window()
    login_window.run()

def demo_main_styles():
    """Demonstra os diferentes estilos de espaçamento da tela principal"""
    
    print("=== Demo: Estilos de Espaçamento da Tela Principal ===")
    print("1. Estilo Compacto")
    print("2. Estilo Normal (Padrão)")
    print("3. Estilo Espaçoso")
    
    choice = input("Escolha um estilo (1-3): ")
    
    # Dados de exemplo para demonstração
    cpf = "12345678901"
    token = "demo_token"
    user_data = {
        'name': 'Usuário Demo',
        'registration': 1234,
        'id': 1,
        'company_id': 1
    }
    
    setup_logger()
    main_window = MainWindow(cpf, token, user_data)
    
    if choice == '1':
        main_window.set_main_spacing_style('compact')
        main_window.root.title("WMS - Menu (Compacto)")
    elif choice == '3':
        main_window.set_main_spacing_style('spacious')
        main_window.root.title("WMS - Menu (Espaçoso)")
    else:
        # Usar estilo normal (padrão)
        main_window.root.title("WMS - Menu (Normal)")
    
    main_window.run()

if __name__ == "__main__":
    print("=== Demonstração de Estilos de Espaçamento ===")
    print("1. Demonstrar estilos da tela de Login")
    print("2. Demonstrar estilos da tela Principal")
    
    main_choice = input("Escolha uma opção (1-2): ")
    
    if main_choice == '1':
        demo_login_styles()
    elif main_choice == '2':
        demo_main_styles()
    else:
        print("Opção inválida!")