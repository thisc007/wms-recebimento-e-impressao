#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Impressão em Lote
Interface para selecionar label e imprimir sequência de etiquetas
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from label_manager import LabelManager
from cargo_manager import CargoManager
from printer.zpl_generator import ZplGenerator
from printer.label_printer import LabelPrinter
from api.client import APIClient
from utils.logger import log_info, log_error
from utils.validators import format_cpf
from utils.printer_config import PrinterConfigManager

class BatchPrintWindow:
    """Janela de impressão em lote"""
    
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
        self.label_manager = LabelManager(self.api_client, token)
        self.zpl_generator = ZplGenerator()
        self.printer = LabelPrinter()
        self.printer_config_manager = PrinterConfigManager()
        
        # Dados
        self.labels = []
        self.selected_label = None
        self.configured_printers = {}
        
        # Interface
        self.setup_window()
        self.create_widgets()
        self.load_labels()
    
    def setup_window(self):
        """Configura a janela principal"""
        self.root = tk.Tk()
        self.root.title("Impressão de Etiquetas em Lote")
        self.root.geometry("600x700")
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
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="📦 Impressão de Etiquetas em Lote", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        user_label = ttk.Label(header_frame, 
                              text=f"Usuário: {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)})",
                              font=('Arial', 10))
        user_label.pack(pady=(5, 0))
        
        # Frame de seleção de label
        selection_frame = ttk.LabelFrame(main_frame, text="Seleção de Label", padding="10")
        selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Lista de labels
        labels_label = ttk.Label(selection_frame, text="Labels disponíveis:")
        labels_label.pack(anchor=tk.W)
        
        # Frame para lista com scrollbar
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Scrollbar e Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.labels_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                        height=8, font=('Consolas', 10))
        self.labels_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.labels_listbox.bind('<<ListboxSelect>>', self.on_label_select)
        
        scrollbar.config(command=self.labels_listbox.yview)
        
        # Botões de label
        buttons_frame = ttk.Frame(selection_frame)
        buttons_frame.pack(fill=tk.X)
        
        refresh_button = ttk.Button(buttons_frame, text="🔄 Atualizar Lista", 
                                   command=self.load_labels)
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        new_label_button = ttk.Button(buttons_frame, text="➕ Nova Label", 
                                     command=self.create_new_label)
        new_label_button.pack(side=tk.LEFT)
        
        # Frame de informações da label selecionada
        self.info_frame = ttk.LabelFrame(main_frame, text="Label Selecionada", padding="10")
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.info_label = ttk.Label(self.info_frame, text="Nenhuma label selecionada", 
                                   font=('Arial', 10))
        self.info_label.pack()
        
        # Frame de configuração de impressão
        print_frame = ttk.LabelFrame(main_frame, text="Configuração de Impressão", padding="10")
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
        
        print_button = ttk.Button(action_frame, text="🖨️ Imprimir", 
                                 command=self.print_labels, style='Accent.TButton')
        print_button.pack(side=tk.LEFT, padx=(0, 10))
        
        close_button = ttk.Button(action_frame, text="🚪 Fechar", 
                                 command=self.close_window)
        close_button.pack(side=tk.RIGHT)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="", foreground='blue')
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
    
    def load_labels(self):
        """Carrega labels do usuário"""
        try:
            self.status_label.config(text="Carregando labels...", foreground='blue')
            self.root.update()
            
            user_id = self.user_data.get('id')
            self.labels = self.label_manager.list_labels(user_id)
            
            # Atualizar listbox
            self.labels_listbox.delete(0, tk.END)
            
            if not self.labels:
                self.labels_listbox.insert(tk.END, "(nenhuma label cadastrada)")
                self.status_label.config(text="Nenhuma label encontrada", foreground='orange')
            else:
                for i, label in enumerate(self.labels):
                    last_number = self.label_manager.pad8(label.get('last_number', 0))
                    name = label.get('name', f'label {i+1}')
                    display_text = f"[{i+1}] {name} (último: {last_number})"
                    self.labels_listbox.insert(tk.END, display_text)
                
                self.status_label.config(text=f"{len(self.labels)} label(s) carregada(s)", foreground='green')
                
        except Exception as e:
            log_error(f"Erro ao carregar labels: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro ao carregar labels:\n{str(e)}")
    
    def on_label_select(self, event):
        """Callback para seleção de label"""
        selection = self.labels_listbox.curselection()
        if selection and self.labels:
            index = selection[0]
            if 0 <= index < len(self.labels):
                self.selected_label = self.labels[index]
                self.update_label_info()
    
    def update_label_info(self):
        """Atualiza informações da label selecionada"""
        if not self.selected_label:
            self.info_label.config(text="Nenhuma label selecionada")
            return
        
        name = self.selected_label.get('name', 'N/A')
        label_id = self.selected_label.get('id', 'N/A')
        last_number = self.label_manager.pad8(self.selected_label.get('last_number', 0))
        user_id = self.selected_label.get('user_id', 'N/A')
        
        info_text = f"Nome: {name} | ID: {label_id} | Último: {last_number} "
        self.info_label.config(text=info_text)
    
    def create_new_label(self):
        """Abre diálogo para criar nova label"""
        dialog = NewLabelDialog(self.root, self.user_data.get('id'))
        self.root.wait_window(dialog.dialog)  # Aguarda o diálogo fechar
        
        if dialog.result:
            name = dialog.result
            try:
                self.status_label.config(text="Criando nova label...", foreground='blue')
                self.root.update()
                
                new_label = self.label_manager.get_or_create_label(name, self.user_data.get('id'))
                log_info(f"Nova label criada/encontrada: {name}")
                
                # Recarregar lista
                self.load_labels()
                
                # Selecionar a nova label
                for i, label in enumerate(self.labels):
                    if label.get('id') == new_label.get('id'):
                        self.labels_listbox.selection_set(i)
                        self.selected_label = label
                        self.update_label_info()
                        break
                
                self.status_label.config(text=f"Label '{name}' pronta para uso", foreground='green')
                
            except Exception as e:
                log_error(f"Erro ao criar label: {str(e)}")
                self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
                messagebox.showerror("Erro", f"Erro ao criar label:\n{str(e)}")
    
    def print_labels(self):
        """Executa impressão das etiquetas"""
        if not self.selected_label:
            messagebox.showwarning("Aviso", "Selecione uma label primeiro.")
            return
        
        try:
            # Validar quantidade
            qty_text = self.qty_entry.get().strip()
            if not qty_text.isdigit() or int(qty_text) <= 0:
                messagebox.showerror("Erro", "Digite uma quantidade válida (número inteiro > 0)")
                return
            
            quantity = int(qty_text)
            
            # Confirmar impressão
            result = messagebox.askyesno("Confirmar Impressão", 
                                       f"Imprimir {quantity} etiqueta(s) da label '{self.selected_label.get('name', 'N/A')}'?")
            if not result:
                return
            
            self.status_label.config(text="Preparando impressão...", foreground='blue')
            self.root.update()
            
            # Calcular sequência
            last, start, end = self.label_manager.calculate_sequence(self.selected_label, quantity)
            
            log_info(f"Imprimindo sequência {self.label_manager.pad8(start)} até {self.label_manager.pad8(end)}")
            
            # Atualizar last_number na API primeiro
            self.status_label.config(text="Atualizando contador na API...", foreground='blue')
            self.root.update()
            
            self.label_manager.update_last_number(self.selected_label['id'], end)
            
            # Gerar ZPL
            self.status_label.config(text="Gerando códigos ZPL...", foreground='blue')
            self.root.update()
            
            all_zpl = self.zpl_generator.build_batch_zpl(start, quantity)
            
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
            self.status_label.config(text=f"✅ {quantity} etiqueta(s) impressa(s) com sucesso!", foreground='green')
            
            log_info(f"Impressão concluída: {quantity} etiquetas da label {self.selected_label.get('name', 'N/A')}")
            
            # Atualizar informações da label
            self.selected_label['last_number'] = end
            self.update_label_info()
            
            messagebox.showinfo("Sucesso", f"Impressão concluída!\n\nSequência: {self.label_manager.pad8(start)} até {self.label_manager.pad8(end)}")
            
        except Exception as e:
            log_error(f"Erro na impressão: {str(e)}")
            self.status_label.config(text=f"❌ Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro na Impressão", f"Erro durante a impressão:\n{str(e)}")
    
    def close_window(self):
        """Fecha a janela"""
        self.root.destroy()
    
    # Removido método run() - não é mais necessário para janelas modais


class NewLabelDialog:
    """Diálogo para criar nova label"""
    
    def __init__(self, parent, user_id):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nova Label")
        self.dialog.geometry("450x280")
        self.dialog.resizable(False, False)
        
        # Centralizar
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centralizar na tela
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Criar Nova Label", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Campo nome
        ttk.Label(main_frame, text="Nome da label:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(main_frame, width=40, font=('Arial', 12))
        self.name_entry.pack(fill=tk.X, pady=(5, 20))
        self.name_entry.focus()
        
        # Informações
        info_text = f"A label será criada para o usuário ID: {user_id}\nÚltimo número inicial: 00000000"
        info_label = ttk.Label(main_frame, text=info_text, foreground='gray')
        info_label.pack(pady=(0, 20))
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        create_button = ttk.Button(buttons_frame, text="Criar", 
                                  command=self.create_label, style='Accent.TButton')
        create_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", 
                                  command=self.cancel)
        cancel_button.pack(side=tk.RIGHT)
        
        # Enter para criar
        self.dialog.bind('<Return>', lambda e: self.create_label())
    
    def create_label(self):
        """Cria a label"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Erro", "Digite um nome para a label.")
            return
        
        self.result = name
        self.dialog.destroy()
    
    def cancel(self):
        """Cancela criação"""
        self.dialog.destroy()