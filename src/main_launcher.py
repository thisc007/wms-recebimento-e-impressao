import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger

def main():
    """Função principal que permite escolher entre interface GUI ou CLI"""
    setup_logger()
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == '--gui':
            # Executar interface gráfica
            from ui.gui import main as gui_main
            gui_main()
        elif sys.argv[1] == '--gui-simple':
            # Executar interface gráfica simples
            from ui.gui_simple import main_simple
            main_simple()
        elif sys.argv[1] == '--gui-debug':
            # Executar interface gráfica em modo debug
            from ui.gui_simple import main_simple
            # Configurar debug mode
            os.environ['WMS_DEBUG'] = 'true'
            main_simple()
        elif sys.argv[1] == '--cli':
            # Executar interface de linha de comando
            from ui.menu import Menu
            menu = Menu()
            menu.display()
        else:
            print("Argumentos disponíveis:")
            print("  --gui         : Executar interface gráfica (com validação)")
            print("  --gui-simple  : Executar interface gráfica simples (sem formatação)")
            print("  --gui-debug   : Executar interface gráfica em modo debug/teste")
            print("  --cli         : Executar interface de linha de comando")
            print("  (sem argumentos) : Executar interface gráfica simples por padrão")
    else:
        # Por padrão, executar interface gráfica simples
        try:
            from ui.gui_simple import main_simple
            main_simple()
        except ImportError as e:
            print(f"Erro ao importar interface gráfica: {e}")
            print("Executando interface de linha de comando...")
            from ui.menu import Menu
            menu = Menu()
            menu.display()
        except Exception as e:
            print(f"Erro na interface gráfica: {e}")
            print("Executando interface de linha de comando...")
            from ui.menu import Menu
            menu = Menu()
            menu.display()

if __name__ == "__main__":
    main()