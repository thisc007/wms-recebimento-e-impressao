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
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        # Centralizar janela na tela
        self.center_window()
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar widgets com estilo compacto
        self.create_widgets_compact()
        
        # Configurar API e Login Manager
        self.api_client = APIClient()
        self.login_manager = LoginManager(self.api_client)
        
    def set_spacing_style(self, style='normal'):
        """Define o estilo de espaçamento da interface"""
        # Limpar widgets existentes
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if style == 'compact':
            self.create_widgets_compact()
        elif style == 'spacious':
            self.create_widgets_spacious()
        else:
            self.create_widgets()  # Normal/padrão
        
    def create_widgets_compact(self):
        """Cria os widgets da tela de login com espaçamento compacto"""
        # Frame principal com padding reduzido
        main_frame = ttk.Frame(self.root, padding="15")  # Reduzido de 20 para 15
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título com menos espaço abaixo
        title_label = ttk.Label(main_frame, text="Repositorium WMS - Sistema de Impressão", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))  # Reduzido de 30 para 20
        
        # Subtítulo com menos espaço
        subtitle_label = ttk.Label(main_frame, text="Faça login para continuar", 
                                  font=('Arial', 10))
        subtitle_label.pack(pady=(0, 15))  # Reduzido de 20 para 15
        
        # Frame para campos de entrada
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(pady=5)  # Reduzido de 10 para 5
        
        # Campo CPF - espaçamento reduzido
        cpf_label = ttk.Label(fields_frame, text="CPF (somente números):")
        cpf_label.grid(row=0, column=0, sticky='w', pady=(0, 3))  # Reduzido de 5 para 3
        
        self.cpf_entry = ttk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.cpf_entry.grid(row=1, column=0, pady=(0, 10))  # Reduzido de 15 para 10
        self.cpf_entry.focus()
        
        # Campo Senha - espaçamento reduzido
        password_label = ttk.Label(fields_frame, text="Senha:")
        password_label.grid(row=2, column=0, sticky='w', pady=(0, 3))  # Reduzido de 5 para 3
        
        self.password_entry = ttk.Entry(fields_frame, width=25, show='*', font=('Arial', 10))
        self.password_entry.grid(row=3, column=0, pady=(0, 15))  # Reduzido de 20 para 15
        
        # Botão de Login
        login_button = ttk.Button(fields_frame, text="Entrar", command=self.handle_login,
                                 style='Accent.TButton')
        login_button.grid(row=4, column=0, pady=8)  # Reduzido de 10 para 8
        
        # Configurar Enter para fazer login
        self.root.bind('<Return>', lambda event: self.handle_login())
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground='red')
        self.status_label.pack(pady=8)  # Reduzido de 10 para 8
        
    def create_widgets_spacious(self):
        """Cria os widgets da tela de login com espaçamento amplo"""
        # Frame principal com padding aumentado
        main_frame = ttk.Frame(self.root, padding="30")  # Aumentado de 20 para 30
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título com mais espaço abaixo
        title_label = ttk.Label(main_frame, text="Repositorium WMS - Sistema de Impressão", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 40))  # Aumentado de 30 para 40
        
        # Subtítulo com mais espaço
        subtitle_label = ttk.Label(main_frame, text="Faça login para continuar", 
                                  font=('Arial', 10))
        subtitle_label.pack(pady=(0, 30))  # Aumentado de 20 para 30
        
        # Frame para campos de entrada
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(pady=20)  # Aumentado de 10 para 20
        
        # Campo CPF - espaçamento aumentado
        cpf_label = ttk.Label(fields_frame, text="CPF (somente números):")
        cpf_label.grid(row=0, column=0, sticky='w', pady=(0, 8))  # Aumentado de 5 para 8
        
        self.cpf_entry = ttk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.cpf_entry.grid(row=1, column=0, pady=(0, 20))  # Aumentado de 15 para 20
        self.cpf_entry.focus()
        
        # Campo Senha - espaçamento aumentado
        password_label = ttk.Label(fields_frame, text="Senha:")
        password_label.grid(row=2, column=0, sticky='w', pady=(0, 8))  # Aumentado de 5 para 8
        
        self.password_entry = ttk.Entry(fields_frame, width=25, show='*', font=('Arial', 10))
        self.password_entry.grid(row=3, column=0, pady=(0, 25))  # Aumentado de 20 para 25
        
        # Botão de Login
        login_button = ttk.Button(fields_frame, text="Entrar", command=self.handle_login,
                                 style='Accent.TButton')
        login_button.grid(row=4, column=0, pady=15)  # Aumentado de 10 para 15
        
        # Configurar Enter para fazer login
        self.root.bind('<Return>', lambda event: self.handle_login())
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground='red')
        self.status_label.pack(pady=15)  # Aumentado de 10 para 15
        
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
        
        # Campo CPF - Versão Simples
        cpf_label = ttk.Label(fields_frame, text="CPF (somente números):")
        cpf_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.cpf_entry = ttk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.cpf_entry.grid(row=1, column=0, pady=(0, 15))
        self.cpf_entry.focus()  # Foco inicial no CPF
        
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
        
    def handle_login(self):
        """Manipula o processo de login"""
        cpf = clean_cpf(self.cpf_entry.get().strip())
        password = self.password_entry.get().strip()
        
        # Limpar mensagem de status anterior
        self.status_label.config(text="")
        
        if not cpf or not password:
            self.show_error("Por favor, preencha todos os campos.")
            return
        
        ## Validar CPF
        #if not validate_cpf(cpf):
            #self.show_error("CPF inválido. Verifique os números digitados.")
            #return
            
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
        self.root.destroy()
        main_window = MainWindow(cpf, token, user_data)
        main_window.set_main_spacing_style('compact')  # Aplicar estilo compacto
        main_window.run()
        
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()


class MainWindow:
    def __init__(self, cpf, token, user_data):
        self.cpf = cpf
        self.token = token
        self.user_data = user_data
        
        # Inicializar API Client com token
        self.api_client = APIClient()
        self.api_client.token = token
        
        self.root = tk.Tk()
        self.root.title("Repositorium WMS - Menu Principal")
        self.root.geometry("450x600")  # Tamanho compacto
        self.root.resizable(False, False)
        
        # Centralizar janela na tela
        self.center_window()
        
        # Criar widgets com estilo compacto
        self.create_widgets_compact_main()
        
    def create_widgets_compact_main(self):
        """Cria os widgets da tela principal com espaçamento compacto"""
        # Frame principal com padding reduzido
        main_frame = ttk.Frame(self.root, padding="8")  # Reduzido de 10 para 8
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho com espaçamento reduzido
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(5, 5))  # Reduzido de (10, 10) para (5, 5)
        
        title_label = ttk.Label(header_frame, text="Sistema de Impressão WMS", 
                               font=('Arial', 18, 'bold'))
        title_label.pack()
        
        # Informações do usuário com espaçamento reduzido
        user_name = self.user_data.get('name', 'Usuário')
        user_registration = self.user_data.get('registration', 'N/A')
        
        user_label = ttk.Label(header_frame, text=f"Usuário: {user_name}", 
                              font=('Arial', 12, 'bold'))
        user_label.pack(pady=(3, 0))  # Reduzido de (5, 0) para (3, 0)
        
        cpf_label = ttk.Label(header_frame, text=f"CPF: {format_cpf(self.cpf)}", 
                             font=('Arial', 10))
        cpf_label.pack()
        
        reg_label = ttk.Label(header_frame, text=f"Matrícula: {user_registration}", 
                             font=('Arial', 10))
        reg_label.pack(pady=(0, 8))  # Reduzido de (0, 10) para (0, 8)
        
        # Frame para botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(expand=True)
        
        # Estilo dos botões compacto
        style = ttk.Style()
        style.configure('Compact.TButton', font=('Arial', 11), padding=(8, 6))
        
        # Botões com espaçamento reduzido
        print_batch_button = ttk.Button(buttons_frame, 
                                       text="📦 Imprimir Etiquetas em Lote",
                                       command=self.open_batch_print,
                                       style='Compact.TButton')
        print_batch_button.pack(pady=8, fill=tk.X)  # Reduzido de 15 para 8
        
        reprint_button = ttk.Button(buttons_frame, 
                                   text="🔄 Reimpressão",
                                   command=self.open_reprint,
                                   style='Compact.TButton')
        reprint_button.pack(pady=8, fill=tk.X)
        
        receive_load_button = ttk.Button(buttons_frame, 
                                         text="📦 Receber Carga",
                                         command=self.open_receive_load,
                                         style='Compact.TButton')
        receive_load_button.pack(pady=8, fill=tk.X)
        
        # Botão Consolidação (novo)
        consolidation_button = ttk.Button(buttons_frame,
                                          text="🧩 Consolidação",
                                          command=self.open_consolidators,
                                          style='Compact.TButton')
        consolidation_button.pack(pady=8, fill=tk.X)
        
        # Separador
        separator = ttk.Separator(buttons_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=12)  # Reduzido de 20 para 12
        # Botão de configuração de impressoras
        printer_config_button = ttk.Button(buttons_frame, 
                                          text="⚙️ Configurar Impressoras",
                                          command=self.open_printer_config,
                                          style='Compact.TButton')
        printer_config_button.pack(pady=8, fill=tk.X)
        
        separator2 = ttk.Separator(buttons_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=12)
        
        logout_button = ttk.Button(buttons_frame, 
                                  text="🚪 Logout",
                                  command=self.logout,
                                  style='Compact.TButton')
        logout_button.pack(pady=8, fill=tk.X)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = ttk.Label(footer_frame, 
                                text="© 2025 Repositorium WMS - Recebimento e Impressão", 
                                font=('Arial', 8), foreground='gray')
        footer_label.pack()
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Cria os widgets da tela principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        title_label = ttk.Label(header_frame, text="Sistema de Impressão WMS", 
                               font=('Arial', 18, 'bold'))
        title_label.pack()
        
        # Exibir informações do usuário
        user_name = self.user_data.get('name', 'Usuário')
        user_registration = self.user_data.get('registration', 'N/A')
        
        user_label = ttk.Label(header_frame, text=f"Usuário: {user_name}", 
                              font=('Arial', 12, 'bold'))
        user_label.pack(pady=(5, 0))
        
        cpf_label = ttk.Label(header_frame, text=f"CPF: {format_cpf(self.cpf)}", 
                             font=('Arial', 10))
        cpf_label.pack()
        
        reg_label = ttk.Label(header_frame, text=f"Matrícula: {user_registration}", 
                             font=('Arial', 10))
        reg_label.pack(pady=(0, 10))
        
        # Frame para botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(expand=True)
        
        # Estilo dos botões
        style = ttk.Style()
        style.configure('Menu.TButton', font=('Arial', 12), padding=(10, 8))
        
        # Botão Imprimir Etiquetas em Lote
        print_batch_button = ttk.Button(buttons_frame, 
                                       text="📦 Imprimir Etiquetas em Lote",
                                       command=self.open_batch_print,
                                       style='Menu.TButton')
        print_batch_button.pack(pady=15, fill=tk.X)
        
        # Botão Reimpressão
        reprint_button = ttk.Button(buttons_frame, 
                                   text="🔄 Reimpressão",
                                   command=self.open_reprint,
                                   style='Menu.TButton')
        reprint_button.pack(pady=15, fill=tk.X)
        
        # Botão Receber carga
        receive_load_button = ttk.Button(buttons_frame, 
                                         text="📦 Receber Carga",
                                         command=self.open_receive_load,
                                         style='Menu.TButton')
        receive_load_button.pack(pady=15, fill=tk.X)
        
        # Botão Consolidação (novo)
        consolidation_button = ttk.Button(buttons_frame,
                                          text="🧩 Consolidação",
                                          command=self.open_consolidators,
                                          style='Menu.TButton')
        consolidation_button.pack(pady=15, fill=tk.X)
        
        # Separador
        separator = ttk.Separator(buttons_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # Botão de Configuração de etiquetadora
        label_printer_button = ttk.Button(buttons_frame, 
                                           text="🖨️ Configuração de Etiquetadora",
                                           command=self.open_label_printer_settings,
                                           style='Menu.TButton')
        label_printer_button.pack(pady=15, fill=tk.X)

        # Separador
        separator = ttk.Separator(buttons_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # Botão Logout
        logout_button = ttk.Button(buttons_frame, 
                                  text="🚪 Logout",
                                  command=self.logout,
                                  style='Menu.TButton')
        logout_button.pack(pady=15, fill=tk.X)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = ttk.Label(footer_frame, 
                                text="© 2025 Repositorium WMS - Recebimento e Impressão", 
                                font=('Arial', 8), foreground='gray')
        footer_label.pack()
        
    def open_batch_print(self):
        """Abre a janela de impressão em lote"""
        batch_window = None
        window_closed = False
        
        def on_window_close():
            nonlocal window_closed
            window_closed = True
            print("DEBUG: Callback de fechamento executado")
            if batch_window and batch_window.root.winfo_exists():
                batch_window.root.destroy()
        
        try:
            from ui.batch_print_window import BatchPrintWindow
            
            log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) acessou impressão em lote")
            
            # Desabilitar botões da janela principal
            print("DEBUG: Desabilitando janela principal...")
            self.disable_main_window()
            print("DEBUG: Janela principal desabilitada.")
            
            # Abrir janela de impressão em lote
            batch_window = BatchPrintWindow(self.cpf, self.token, self.user_data)
            
            # Configurar callback personalizado de fechamento
            batch_window.root.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # Executar janela modal
            batch_window.root.grab_set()
            
            # Aguardar fechamento da janela com timeout e verificação
            print("DEBUG: Aguardando fechamento da janela modal...")
            
            # Loop de espera mais robusto
            while not window_closed:
                try:
                    self.root.update()
                    if not batch_window.root.winfo_exists():
                        window_closed = True
                        break
                except:
                    window_closed = True
                    break
            
            print("DEBUG: Janela modal foi fechada.")
            
        except Exception as e:
            log_error(f"Erro ao abrir impressão em lote: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir impressão em lote:\n{str(e)}")
        finally:
            # Sempre reabilitar janela principal
            print("DEBUG: Executando finally - reabilitando janela principal...")
            try:
                if batch_window and batch_window.root.winfo_exists():
                    batch_window.root.destroy()
            except:
                pass
            self.enable_main_window()
            self.root.lift()
            self.root.focus_force()
            print("DEBUG: Janela principal reabilitada.")
        
    def open_reprint(self):
        """Abre a janela de reimpressão"""
        reprint_window = None
        window_closed = False
        
        def on_window_close():
            nonlocal window_closed
            window_closed = True
            print("DEBUG: Callback de fechamento (reprint) executado")
            if reprint_window and reprint_window.root.winfo_exists():
                reprint_window.root.destroy()
        
        try:
            from ui.reprint_window import ReprintWindow
            
            log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) acessou reimpressão")
            
            # Desabilitar botões da janela principal
            print("DEBUG: Desabilitando janela principal (reprint)...")
            self.disable_main_window()
            print("DEBUG: Janela principal desabilitada (reprint).")
            
            # Abrir janela de reimpressão
            reprint_window = ReprintWindow(self.cpf, self.token, self.user_data)
            
            # Configurar callback personalizado de fechamento
            reprint_window.root.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # Executar janela modal
            reprint_window.root.grab_set()
            
            # Aguardar fechamento da janela com timeout e verificação
            print("DEBUG: Aguardando fechamento da janela modal (reprint)...")
            
            # Loop de espera mais robusto
            while not window_closed:
                try:
                    self.root.update()
                    if not reprint_window.root.winfo_exists():
                        window_closed = True
                        break
                except:
                    window_closed = True
                    break
            
            print("DEBUG: Janela modal (reprint) foi fechada.")
            
        except Exception as e:
            log_error(f"Erro ao abrir reimpressão: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir reimpressão:\n{str(e)}")
        finally:
            # Sempre reabilitar janela principal
            print("DEBUG: Executando finally (reprint) - reabilitando janela principal...")
            try:
                if reprint_window and reprint_window.root.winfo_exists():
                    reprint_window.root.destroy()
            except:
                pass
            self.enable_main_window()
            self.root.lift()
            self.root.focus_force()
            print("DEBUG: Janela principal reabilitada (reprint).")
        
    def open_receive_load(self):
        """Abre a janela de recebimento de carga"""
        receive_window = None
        window_closed = False
        
        def on_window_close():
            nonlocal window_closed
            window_closed = True
            print("DEBUG: Callback de fechamento (receive_load) executado")
            if receive_window and receive_window.root.winfo_exists():
                receive_window.root.destroy()
        
        try:
            from ui.receive_load_window import ReceiveLoadWindow
            
            log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) acessou recebimento de carga")
            
            # Desabilitar botões da janela principal
            print("DEBUG: Desabilitando janela principal (receive_load)...")
            self.disable_main_window()
            print("DEBUG: Janela principal desabilitada (receive_load).")
            
            # Abrir janela de recebimento
            receive_window = ReceiveLoadWindow(self.cpf, self.token, self.user_data)
            
            # Configurar callback personalizado de fechamento
            receive_window.root.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # Executar janela modal
            receive_window.root.grab_set()
            
            # Aguardar fechamento da janela
            print("DEBUG: Aguardando fechamento da janela modal (receive_load)...")
            
            # Loop de espera
            while not window_closed:
                try:
                    self.root.update()
                    if not receive_window.root.winfo_exists():
                        window_closed = True
                        break
                except:
                    window_closed = True
                    break
            
            print("DEBUG: Janela modal (receive_load) foi fechada.")
            
        except Exception as e:
            log_error(f"Erro ao abrir recebimento de carga: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir recebimento de carga:\n{str(e)}")
        finally:
            # Sempre reabilitar janela principal
            print("DEBUG: Executando finally (receive_load) - reabilitando janela principal...")
            try:
                if receive_window and receive_window.root.winfo_exists():
                    receive_window.root.destroy()
            except:
                pass
            self.enable_main_window()
            self.root.lift()
            self.root.focus_force()
            print("DEBUG: Janela principal reabilitada (receive_load).")

    def open_consolidators(self):
        """Abre a janela de Consolidadores (Consolidação e Impressão)"""
        consol_window = None
        window_closed = False

        def on_window_close():
            nonlocal window_closed
            window_closed = True
            print("DEBUG: Callback de fechamento (consolidators) executado")
            if consol_window and consol_window.root.winfo_exists():
                consol_window.root.destroy()

        try:
            from ui.consolidator_window import ConsolidatorWindow

            log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) acessou consolidação")

            # Desabilitar janela principal
            print("DEBUG: Desabilitando janela principal (consolidators)...")
            self.disable_main_window()
            print("DEBUG: Janela principal desabilitada (consolidators).")

            # Abrir janela de consolidadores - passar self.root como parent
            consol_window = ConsolidatorWindow(self.cpf, self.token, self.user_data, parent=self.root)

            # Configurar callback de fechamento
            consol_window.root.protocol("WM_DELETE_WINDOW", on_window_close)

            # Executar modal
            consol_window.root.grab_set()

            print("DEBUG: Aguardando fechamento da janela modal (consolidators)...")
            while not window_closed:
                try:
                    self.root.update()
                    if not consol_window.root.winfo_exists():
                        window_closed = True
                        break
                except:
                    window_closed = True
                    break

            print("DEBUG: Janela modal (consolidators) foi fechada.")

        except Exception as e:
            log_error(f"Erro ao abrir consolidador: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir consolidador:\n{str(e)}")
        finally:
            print("DEBUG: Executando finally (consolidators) - reabilitando janela principal...")
            try:
                if consol_window and consol_window.root.winfo_exists():
                    consol_window.root.destroy()
            except:
                pass
            self.enable_main_window()
            self.root.lift()
            self.root.focus_force()
            print("DEBUG: Janela principal reabilitada (consolidators).")
        
    def open_label_printer_settings(self):
        """Abre a janela de configuração da etiquetadora"""
        messagebox.showinfo("Em Desenvolvimento", 
                           "Funcionalidade de configuração de etiquetadora será implementada em breve.")
        log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) acessou configuração de etiquetadora")

    def logout(self):
        """Faz logout e retorna à tela de login"""
        result = messagebox.askyesno("Confirmar Logout", 
                                    "Tem certeza que deseja sair?")
        if result:
            log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) fez logout")
            self.root.destroy()
            from ui.gui_simple import LoginWindowSimple
            login_window = LoginWindowSimple()
            login_window.run()
    
    def open_printer_config(self):
        """Abre a janela de configuração de impressoras"""
        try:
            log_info(f"Usuário {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)}) acessou configuração de impressoras")
            
            # Importar e abrir janela de configuração de impressoras
            from ui.printer_config_window import PrinterConfigWindow
            printer_config_window = PrinterConfigWindow(
                self.cpf, 
                self.api_client.token, 
                self.user_data,
                parent=self.root  # Passar a janela pai
            )
            
            # Aguardar o fechamento da janela modal
            self.root.wait_window(printer_config_window.window)
            
            log_info("Configuração de impressoras fechada")
        
        except Exception as e:
            log_error(f"Erro ao abrir configuração de impressoras: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir configuração de impressoras:\n{str(e)}")
    
    def disable_main_window(self):
        """Desabilita todos os botões da janela principal"""
        # Verificar se a janela principal ainda existe
        try:
            if not self.root.winfo_exists():
                print("DEBUG: Janela principal não existe para desabilitar")
                return
        except:
            print("DEBUG: Erro ao verificar janela principal para desabilitar")
            return
            
        # Armazenar referências dos botões para reabilitação
        if not hasattr(self, '_disabled_widgets'):
            self._disabled_widgets = []
        
        def disable_widget(widget):
            try:
                # Verificar se o widget ainda existe
                if not widget.winfo_exists():
                    return
                    
                # Verificar se é um widget que pode ser desabilitado
                widget_class = widget.__class__.__name__
                if widget_class in ['Button', 'Entry', 'Text', 'Listbox', 'Combobox', 'Scale', 'Spinbox']:
                    if hasattr(widget, 'config'):
                        current_state = str(widget['state']) if 'state' in widget.keys() else 'normal'
                        if current_state != 'disabled':
                            self._disabled_widgets.append((widget, current_state))
                            widget.config(state='disabled')
                            print(f"DEBUG: Widget {widget_class} desabilitado")
            except Exception as e:
                print(f"DEBUG: Erro ao desabilitar widget: {e}")
            
            # Recursivamente desabilitar widgets filhos
            try:
                children = widget.winfo_children()
                for child in children:
                    disable_widget(child)
            except Exception as e:
                print(f"DEBUG: Erro ao obter filhos para desabilitar: {e}")
        
        try:
            disable_widget(self.root)
            print(f"DEBUG: {len(self._disabled_widgets)} widgets desabilitados")
        except Exception as e:
            print(f"DEBUG: Erro geral ao desabilitar: {e}")
    
    def enable_main_window(self):
        """Reabilita todos os botões da janela principal"""
        print(f"DEBUG: enable_main_window chamado. _disabled_widgets existe: {hasattr(self, '_disabled_widgets')}")
        
        # Verificar se a janela principal ainda existe
        try:
            self.root.update()  # Forçar atualização da janela
        except Exception as e:
            print(f"DEBUG: Erro ao atualizar janela principal: {e}")
            return
        
        if hasattr(self, '_disabled_widgets') and self._disabled_widgets:
            print(f"DEBUG: Reabilitando {len(self._disabled_widgets)} widgets...")
            for widget, original_state in self._disabled_widgets:
                try:
                    # Verificar se widget ainda existe
                    widget.winfo_exists()
                    widget.config(state=original_state)
                    print(f"DEBUG: Widget {widget.__class__.__name__} reabilitado para estado '{original_state}'")
                except Exception as e:
                    print(f"DEBUG: Erro ao reabilitar widget: {e}")
            self._disabled_widgets.clear()
        else:
            print("DEBUG: Usando fallback para reabilitar widgets...")
            # Fallback: reabilitar todos os botões encontrados
            self._enable_all_buttons_fallback()
        
        print("DEBUG: enable_main_window concluído.")
    
    def _enable_all_buttons_fallback(self):
        """Método fallback para reabilitar todos os botões"""
        try:
            def enable_widget_recursive(widget):
                try:
                    # Se for um botão, reabilitar
                    widget_class = widget.__class__.__name__
                    if 'Button' in widget_class:
                        widget.config(state='normal')
                        print(f"DEBUG: Botão {widget_class} reabilitado (fallback)")
                    
                    # Processar widgets filhos
                    for child in widget.winfo_children():
                        enable_widget_recursive(child)
                        
                except Exception as e:
                    print(f"DEBUG: Erro ao processar widget {widget}: {e}")
            
            # Aplicar a toda a janela
            enable_widget_recursive(self.root)
            
        except Exception as e:
            print(f"DEBUG: Erro geral no fallback: {e}")
            
    def run(self):
        """Executa a janela principal"""
        self.root.mainloop()
        
    def set_main_spacing_style(self, style='normal'):
        """Define o estilo de espaçamento da tela principal"""
        # Limpar widgets existentes
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if style == 'compact':
            self.create_widgets_compact_main()
        elif style == 'spacious':
            self.create_widgets_spacious_main()
        else:
            self.create_widgets()  # Normal/padrão
            
        # Ajustar tamanho da janela baseado no estilo
        if style == 'compact':
            self.root.geometry("450x600")
        elif style == 'spacious':
            self.root.geometry("600x850")
        else:
            self.root.geometry("500x750")
            
        self.center_window()


def main_simple():
    """Função principal para executar a versão simples da aplicação GUI"""
    setup_logger()
    log_info("Iniciando aplicação GUI (versão simples)")
    
    login_window = LoginWindowSimple()
    login_window.run()


if __name__ == "__main__":
    main_simple()