import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from ui.menu import Menu

def main():
    setup_logger()
    menu = Menu()
    menu.display()

if __name__ == "__main__":
    main()