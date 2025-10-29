from src.utils.logger import setup_logging
from src.ui.menu import Menu

def main():
    setup_logging()
    menu = Menu()
    menu.display()

if __name__ == "__main__":
    main()