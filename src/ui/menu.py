class Menu:
    def __init__(self):
        self.options = {
            'N': 'Nova impressão (listar labels disponíveis)',
            'R': 'Reimpressão (escanear código de etiqueta)',
            'X': 'Fechar o programa'
        }

    def display(self):
        print("[2/3] Seleção de modo")
        print("====================================================")
        for key, value in self.options.items():
            print(f"[{key}] {value}")
        print("====================================================")

    def get_user_choice(self):
        choice = input("Escolha o modo [N/R/X]: ").strip().upper()
        return choice if choice in self.options else 'N'  # Default to 'N' if invalid choice