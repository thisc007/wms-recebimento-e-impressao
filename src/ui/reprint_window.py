#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Reimpressão
Interface para escanear código e reimprimir etiqueta específica
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cargo_manager import CargoManager
from printer.zpl_generator import ZplGenerator
from printer.label_printer import LabelPrinter
from api.client import APIClient
from utils.logger import log_info, log_error
from utils.validators import format_cpf
from utils.printer_config import PrinterConfigManager

class ReprintWindow:
    """Janela de reimpressão"""
    
    def __init__(self, cpf: str, token: str, user_data: dict):
        """
        Inicializa a janela
        
        Args:
            cpf: CPF do usuário
            token: Token de autenticação
            user_data: Dados do usuário
        """
        self.cpf = cpf
        self.token = token
        self.user_data = user_data
        
        # Configurar gerenciadores
        self.api_client = APIClient()
        self.cargo_manager = CargoManager(self.api_client, token)
        self.zpl_generator = ZplGenerator()
        self.printer = LabelPrinter()
        self.printer_config_manager = PrinterConfigManager()
        
        # Dados
        self.current_cargo = None
        self.configured_printers = {}
        
        # Interface
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Configura a janela principal"""
        self.root = tk.Tk()
        self.root.title("Reimpressão de Etiquetas")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # Centralizar janela
        self.center_window()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🔄 Reimpressão de Etiquetas", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        user_label = ttk.Label(header_frame, 
                              text=f"Usuário: {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)})",
                              font=('Arial', 10))
        user_label.pack(pady=(5, 0))
        
        # Frame de entrada de código
        input_frame = ttk.LabelFrame(main_frame, text="Código da Etiqueta", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Instruções
        instructions = ttk.Label(input_frame, text="Digite ou escaneie o código da etiqueta:")
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # Formatos aceitos
        formats_frame = ttk.Frame(input_frame)
        formats_frame.pack(fill=tk.X, pady=(0, 15))
        
        format_label = ttk.Label(formats_frame, text="Formatos aceitos:", font=('Arial', 9, 'bold'))
        format_label.pack(anchor=tk.W)
        
        format1_label = ttk.Label(formats_frame, text="• Entrada manual/arquivo: 080000004 (9 dígitos)", 
                                 font=('Arial', 9))
        format1_label.pack(anchor=tk.W, padx=(20, 0))
        
        format2_label = ttk.Label(formats_frame, text="• Inventário (OS):        00000001  (8 dígitos)", 
                                 font=('Arial', 9))
        format2_label.pack(anchor=tk.W, padx=(20, 0))
        
        # Campo de entrada
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(entry_frame, text="Código:").pack(side=tk.LEFT)
        self.code_entry = ttk.Entry(entry_frame, width=20, font=('Arial', 14, 'bold'))
        self.code_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.code_entry.focus()
        
        search_button = ttk.Button(entry_frame, text="🔍 Buscar", 
                                  command=self.search_cargo, style='Accent.TButton')
        search_button.pack(side=tk.RIGHT)
        
        # Enter para buscar
        self.code_entry.bind('<Return>', lambda e: self.search_cargo())
        
        # Frame de informações do cargo
        self.cargo_frame = ttk.LabelFrame(main_frame, text="Informações da Carga", padding="15")
        self.cargo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.cargo_info = tk.Text(self.cargo_frame, height=4, width=60, 
                                 font=('Consolas', 10), state=tk.DISABLED,
                                 wrap=tk.WORD)
        self.cargo_info.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar mensagem inicial
        self.show_cargo_info("Nenhuma carga carregada.\n\nDigite um código acima e clique em 'Buscar'.")
        
        # Frame de configuração de impressão
        print_frame = ttk.LabelFrame(main_frame, text="Configuração de Reimpressão", padding="10")
        print_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Quantidade
        qty_frame = ttk.Frame(print_frame)
        qty_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(qty_frame, text="Quantidade:").pack(side=tk.LEFT)
        self.qty_entry = ttk.Entry(qty_frame, width=10, font=('Arial', 12))
        self.qty_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.qty_entry.insert(0, "1")
        
        # Seleção de impressora
        printer_frame = ttk.Frame(print_frame)
        printer_frame.pack(fill=tk.X)
        
        ttk.Label(printer_frame, text="Impressora:").pack(side=tk.LEFT)
        
        self.selected_printer = tk.StringVar()
        self.printer_combo = ttk.Combobox(printer_frame, textvariable=self.selected_printer, 
                                         state='readonly', width=40)
        self.printer_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Carregar impressoras configuradas
        self.load_printers()
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.reprint_button = ttk.Button(action_frame, text="🖨️ Reimprimir", 
                                        command=self.reprint_label, style='Accent.TButton',
                                        state=tk.DISABLED)
        self.reprint_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ttk.Button(action_frame, text="🗑️ Limpar", 
                                 command=self.clear_form)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        close_button = ttk.Button(action_frame, text="🚪 Fechar", 
                                 command=self.close_window)
        close_button.pack(side=tk.RIGHT)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Digite um código para começar", foreground='blue')
        self.status_label.pack(pady=(10, 0))
    
    def load_printers(self):
        """Carrega impressoras configuradas"""
        try:
            # Obter impressoras habilitadas
            printers = self.printer_config_manager.get_enabled_printers()
            default_id = self.printer_config_manager.config.get('default_printer')
            
            # Montar lista de opções
            printer_options = []
            default_index = 0
            
            if printers:
                for i, (printer_id, printer_config) in enumerate(printers.items()):
                    name = printer_config.get('name', printer_id)
                    printer_type = printer_config.get('type', 'unknown')
                    
                    # Adicionar indicador de padrão
                    if printer_id == default_id:
                        display_name = f"⭐ {name} ({printer_type})"
                        default_index = i
                    else:
                        display_name = f"{name} ({printer_type})"
                    
                    printer_options.append(display_name)
                    self.configured_printers[display_name] = printer_id
                
                # Adicionar opção de arquivo ZPL
                printer_options.append("💾 Salvar como arquivo ZPL")
                self.configured_printers["💾 Salvar como arquivo ZPL"] = "file"
                
                # Configurar combobox
                self.printer_combo['values'] = printer_options
                self.printer_combo.current(default_index)
            else:
                # Sem impressoras configuradas
                printer_options = ["💾 Salvar como arquivo ZPL", "⚠️ Nenhuma impressora configurada"]
                self.configured_printers["💾 Salvar como arquivo ZPL"] = "file"
                self.printer_combo['values'] = printer_options
                self.printer_combo.current(0)
                
        except Exception as e:
            log_error(f"Erro ao carregar impressoras: {str(e)}")
            # Fallback para arquivo
            self.printer_combo['values'] = ["💾 Salvar como arquivo ZPL"]
            self.configured_printers["💾 Salvar como arquivo ZPL"] = "file"
            self.printer_combo.current(0)
    
    def search_cargo(self):
        """Busca cargo pelo código"""
        code = self.code_entry.get().strip()
        
        if not code:
            messagebox.showwarning("Aviso", "Digite um código primeiro.")
            return
        
        try:
            self.status_label.config(text="Buscando carga na API...", foreground='blue')
            self.root.update()
            
            # Buscar cargo
            cargo = self.cargo_manager.get_cargo_by_code(code)
            
            if cargo:
                self.current_cargo = cargo
                self.show_cargo_details(cargo)
                self.reprint_button.config(state=tk.NORMAL)
                self.status_label.config(text="✅ Carga encontrada! Pronta para reimpressão.", foreground='green')
                log_info(f"Cargo encontrado para reimpressão: {code}")
                
            else:
                self.current_cargo = None
                self.show_cargo_not_found(code)
                self.reprint_button.config(state=tk.DISABLED)
                self.status_label.config(text="❌ Carga não encontrada", foreground='red')
                
        except ValueError as e:
            self.current_cargo = None
            self.show_cargo_info(f"❌ ERRO DE VALIDAÇÃO\n\n{str(e)}\n\nFormatos aceitos:\n• 9 dígitos (entrada manual/arquivo): 080000004\n• 8 dígitos (inventário/OS): 00000001")
            self.reprint_button.config(state=tk.DISABLED)
            self.status_label.config(text="❌ Código inválido", foreground='red')
            
        except Exception as e:
            log_error(f"Erro ao buscar cargo {code}: {str(e)}")
            self.current_cargo = None
            self.show_cargo_error(str(e))
            self.reprint_button.config(state=tk.DISABLED)
            self.status_label.config(text=f"❌ Erro: {str(e)}", foreground='red')
    
    def show_cargo_details(self, cargo):
        """Mostra detalhes do cargo encontrado"""
        details = "✅ CARGA ENCONTRADA\n"
        details += "=" * 50 + "\n\n"
        details += self.cargo_manager.format_cargo_details(cargo)
        details += "\n\n" + "=" * 50
        details += "\n\n✅ Pronta para reimpressão!"
        
        self.show_cargo_info(details)
    
    def show_cargo_not_found(self, code):
        """Mostra mensagem de cargo não encontrado"""
        message = "❌ CARGA NÃO ENCONTRADA\n"
        message += "=" * 50 + "\n\n"
        message += f"O código '{code}' não foi encontrado no sistema.\n\n"
        message += "Possíveis causas:\n"
        message += "  • Código não existe no banco de dados\n"
        message += "  • Formato incorreto\n"
        message += "  • Carga ainda não foi registrada no sistema\n\n"
        message += "Formatos aceitos:\n"
        message += "  • 9 dígitos (entrada manual/arquivo): 080000004\n"
        message += "  • 8 dígitos (inventário/OS): 00000001\n\n"
        message += "Dica: Verifique o código no sistema web."
        
        self.show_cargo_info(message)
    
    def show_cargo_error(self, error):
        """Mostra erro na busca"""
        message = "❌ ERRO AO BUSCAR CARGA\n"
        message += "=" * 50 + "\n\n"
        message += f"Erro: {error}\n\n"
        message += "Verifique:\n"
        message += "  • Conexão com a API\n"
        message += "  • Token de autenticação\n"
        message += "  • Código digitado\n\n"
        message += "Tente novamente ou contate o suporte."
        
        self.show_cargo_info(message)
    
    def show_cargo_info(self, text):
        """Exibe texto no campo de informações"""
        self.cargo_info.config(state=tk.NORMAL)
        self.cargo_info.delete(1.0, tk.END)
        self.cargo_info.insert(1.0, text)
        self.cargo_info.config(state=tk.DISABLED)
    
    def reprint_label(self):
        """Executa reimpressão da etiqueta"""
        if not self.current_cargo:
            messagebox.showwarning("Aviso", "Busque uma carga primeiro.")
            return
        
        try:
            # Validar quantidade
            qty_text = self.qty_entry.get().strip()
            if not qty_text.isdigit() or int(qty_text) <= 0:
                messagebox.showerror("Erro", "Digite uma quantidade válida (número inteiro > 0)")
                return
            
            quantity = int(qty_text)
            
            # Obter código para impressão
            code_to_print = self.cargo_manager.get_code_to_print(self.current_cargo)
            
            # Confirmar reimpressão
            result = messagebox.askyesno("Confirmar Reimpressão", 
                                       f"Reimprimir {quantity} etiqueta(s) do código '{code_to_print}'?")
            if not result:
                return
            
            self.status_label.config(text="Preparando reimpressão...", foreground='blue')
            self.root.update()
            
            log_info(f"Iniciando reimpressão: {quantity}x código {code_to_print}")
            
            # Gerar ZPL com indicadores especiais
            self.status_label.config(text="Gerando código ZPL...", foreground='blue')
            self.root.update()
            
            # Preparar dados da carga para indicadores especiais
            cargo_data = None
            if self.current_cargo:
                cargo_data = {
                    'is_priority': self.current_cargo.get('is_priority', False),
                    'requires_special_handling': self.current_cargo.get('requires_special_handling', False),
                    'expiration_date': self.current_cargo.get('expiration_date'),
                    'handling_instructions': self.current_cargo.get('handling_instructions')
                }
                log_info(f"Indicadores na reimpressão: priority={cargo_data['is_priority']}, "
                        f"special_handling={cargo_data['requires_special_handling']}, "
                        f"expiration={cargo_data['expiration_date']}")
            
            zpl = self.zpl_generator.build_zpl(code_to_print, cargo_data)
            
            # Se múltiplas etiquetas, repetir o ZPL
            if quantity > 1:
                all_zpl = zpl * quantity
            else:
                all_zpl = zpl
            
            # Obter impressora selecionada diretamente do widget
            selected_display = self.printer_combo.get().strip()
            
            # Debug
            log_info(f"Display selecionado: '{selected_display}'")
            log_info(f"Impressoras configuradas: {list(self.configured_printers.keys())}")
            
            # Verificar se há seleção
            if not selected_display:
                raise Exception("Por favor, selecione uma impressora no combobox")
            
            printer_id = self.configured_printers.get(selected_display)
            
            if not printer_id:
                # Tentar encontrar por correspondência parcial
                for key in self.configured_printers.keys():
                    if selected_display in key or key in selected_display:
                        printer_id = self.configured_printers[key]
                        log_info(f"Impressora encontrada por correspondência: {key}")
                        break
                
                if not printer_id:
                    raise Exception(f"Impressora não encontrada no mapeamento.\nSelecionado: '{selected_display}'\nDisponíveis: {', '.join(self.configured_printers.keys())}")
            
            # Configurar impressora
            if printer_id == "file":
                # Modo arquivo
                self.printer.config['output_mode'] = 'file'
            else:
                # Usar configuração da impressora
                printer_config = self.printer_config_manager.get_printer(printer_id)
                if not printer_config:
                    raise Exception(f"Impressora {printer_id} não encontrada")
                
                self.printer.config['printer_id'] = printer_id
                self.printer.config['output_mode'] = 'configured'
            
            # Imprimir
            self.status_label.config(text="Enviando para impressão...", foreground='blue')
            self.root.update()
            
            self.printer.send_print_job(all_zpl, quantity)
            
            # Sucesso
            self.status_label.config(text=f"✅ {quantity} etiqueta(s) reimprimida(s) com sucesso!", foreground='green')
            
            log_info(f"Reimpressão concluída: {quantity} etiquetas do código {code_to_print}")
            
            messagebox.showinfo("Sucesso", f"Reimpressão concluída!\n\nCódigo: {code_to_print}\nQuantidade: {quantity}")
            
        except Exception as e:
            log_error(f"Erro na reimpressão: {str(e)}")
            self.status_label.config(text=f"❌ Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro na Reimpressão", f"Erro durante a reimpressão:\n{str(e)}")
    
    def clear_form(self):
        """Limpa o formulário"""
        self.code_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")
        self.current_cargo = None
        self.reprint_button.config(state=tk.DISABLED)
        self.show_cargo_info("Formulário limpo.\n\nDigite um código acima e clique em 'Buscar'.")
        self.status_label.config(text="Digite um código para começar", foreground='blue')
        self.code_entry.focus()
    
    def close_window(self):
        """Fecha a janela"""
        self.root.destroy()
    
    # Removido método run() - não é mais necessário para janelas modais