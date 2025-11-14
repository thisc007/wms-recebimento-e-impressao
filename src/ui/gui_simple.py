import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.login import LoginManager
from api.client import APIClient
from utils.logger import setup_logger, log_info, log_error
from utils.validators import validate_cpf, format_cpf, clean_cpf

class LoginWindowSimple:
    """Versão simplificada da tela de login sem formatação automática"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Repositorium WMS - Sistema de Impressão")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Centralizar janela na tela
        self.center_window()
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar widgets
        self.create_widgets()
        
        # Configurar API e Login Manager
        self.api_client = APIClient()
        self.login_manager = LoginManager(self.api_client)
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """Configura os estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        self.root.configure(bg='#f0f0f0')
        
    def create_widgets(self):
        """Cria os widgets da tela de login"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Repositorium WMS - Sistema de Impressão", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Logo ou ícone (opcional)
        subtitle_label = ttk.Label(main_frame, text="Faça login para continuar", 
                                  font=('Arial', 10))
        subtitle_label.pack(pady=(0, 20))
        
        # Frame para campos de entrada
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(pady=10)
        
        # Campo CPF - Limitado a 11 dígitos
        cpf_label = ttk.Label(fields_frame, text="CPF (somente números):")
        cpf_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.cpf_entry = ttk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.cpf_entry.grid(row=1, column=0, pady=(0, 15))
        self.cpf_entry.focus()  # Foco inicial no CPF
        
        # Configurar limitação do CPF
        self.setup_cpf_limit()
        
        # Campo Senha
        password_label = ttk.Label(fields_frame, text="Senha:")
        password_label.grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.password_entry = ttk.Entry(fields_frame, width=25, show='*', font=('Arial', 10))
        self.password_entry.grid(row=3, column=0, pady=(0, 20))
        
        # Botão de Login
        login_button = ttk.Button(fields_frame, text="Entrar", command=self.handle_login,
                                 style='Accent.TButton')
        login_button.grid(row=4, column=0, pady=10)
        
        # Configurar Enter para fazer login
        self.root.bind('<Return>', lambda event: self.handle_login())
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground='red')
        self.status_label.pack(pady=10)
        
    def setup_cpf_limit(self):
        """Configura limitação de 11 dígitos para o campo CPF"""
        def validate_cpf_input(action, char, text):
            """Valida entrada limitando a 11 dígitos numéricos"""
            if action == '1':  # Inserção
                # Verificar se é número
                if not char.isdigit():
                    return False
                # Verificar se não excede 11 dígitos
                if len(text) > 11:
                    return False
            return True
        
        # Registrar validação
        vcmd = (self.root.register(validate_cpf_input), '%d', '%S', '%P')
        self.cpf_entry.config(validate='key', validatecommand=vcmd)
        
    def handle_login(self):
        """Manipula o processo de login"""
        cpf = clean_cpf(self.cpf_entry.get().strip())
        password = self.password_entry.get().strip()
        
        # Debug - mostrar CPF processado
        print(f"CPF digitado: '{self.cpf_entry.get()}'")
        print(f"CPF limpo: '{cpf}' (tamanho: {len(cpf)})")
        
        # Limpar mensagem de status anterior
        self.status_label.config(text="")
        
        if not cpf or not password:
            self.show_error("Por favor, preencha todos os campos.")
            return
        
        # Validar CPF - Temporariamente desabilitado para teste
        # if not validate_cpf(cpf):
        #     self.show_error("CPF inválido. Verifique os números digitados.")
        #     return
            
        try:
            # Validar credenciais
            self.login_manager.validate_credentials(cpf, password)
            
            # Tentar fazer login
            self.status_label.config(text="Fazendo login...", foreground='blue')
            self.root.update()
            
            login_result = self.login_manager.login(cpf, password)
            
            if login_result:
                # Extrair dados do retorno da API
                token = login_result['token']
                user_data = login_result['user']
                
                log_info(f"Login realizado com sucesso para CPF: {format_cpf(cpf)} - Usuário: {user_data.get('name', 'N/A')}")
                
                # Passar dados completos para a tela principal
                self.open_main_window(cpf, token, user_data)
            else:
                self.show_error("Falha no login. Verifique suas credenciais.")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            log_error(f"Erro durante o login: {str(e)}")
            self.show_error("Erro durante o login. Tente novamente.")
            
    def show_error(self, message):
        """Exibe mensagem de erro"""
        self.status_label.config(text=message, foreground='red')
        
    def open_main_window(self, cpf, token, user_data):
        """Abre a janela principal após login bem-sucedido"""
        from ui.gui import MainWindow  # Import da classe MainWindow correta
        # Cria a janela principal primeiro. Só destrói a janela de login
        # depois que a MainWindow for instanciada com sucesso, para evitar
        # acessar widgets destruídos se ocorrer um erro durante a criação.
        main_window = MainWindow(cpf, token, user_data)
        try:
            main_window.set_main_spacing_style('compact')
        except Exception:
            # Se falhar ao ajustar o estilo, não impedimos a abertura da janela
            pass
        # Agora podemos descartar a janela de login e abrir a principal
        try:
            self.root.destroy()
        except Exception:
            pass
        main_window.run()
        
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()


def main_simple():
    """Função principal para executar a versão simples da aplicação GUI"""
    setup_logger()
    log_info("Iniciando aplicação GUI (versão simples)")
    
    login_window = LoginWindowSimple()
    login_window.run()


if __name__ == "__main__":
    main_simple()