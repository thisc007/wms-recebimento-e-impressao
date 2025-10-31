#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Configuração de Impressoras
Interface para configurar impressoras Zebra GK420t (USB e Rede)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.printer_config import PrinterConfigManager
from utils.logger import log_info, log_error
from utils.validators import format_cpf

class PrinterConfigWindow:
    """Janela de configuração de impressoras"""
    
    def __init__(self, cpf: str, token: str, user_data: dict, parent=None):
        """
        Inicializa a janela
        
        Args:
            cpf: CPF do usuário
            token: Token de autenticação
            user_data: Dados do usuário
            parent: Janela pai (opcional)
        """
        self.cpf = cpf
        self.token = token
        self.user_data = user_data
        self.parent = parent
        
        # Inicializar gerenciador de configuração
        self.printer_config = PrinterConfigManager()
        
        # Interface
        self.setup_window()
        self.create_widgets()
        self.load_printers()
    
    def setup_window(self):
        """Configura a janela principal"""
        # Usar Toplevel se houver janela pai, caso contrário Tk
        if self.parent:
            self.root = tk.Toplevel(self.parent)
            # Tornar a janela modal
            self.root.transient(self.parent)
            self.root.grab_set()
        else:
            self.root = tk.Tk()
        
        self.window = self.root  # Adicionar referência para compatibilidade com wait_window
        self.root.title("Configuração de Impressoras Zebra GK420t")
        self.root.geometry("800x700")
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
        
        title_label = ttk.Label(header_frame, text="🖨️ Configuração de Impressoras Zebra GK420t", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        user_label = ttk.Label(header_frame, 
                              text=f"Usuário: {self.user_data.get('name', 'N/A')} (CPF: {format_cpf(self.cpf)})",
                              font=('Arial', 10))
        user_label.pack(pady=(5, 0))
        
        # Frame de lista de impressoras
        list_frame = ttk.LabelFrame(main_frame, text="Impressoras Configuradas", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Lista de impressoras com Treeview
        columns = ('name', 'type', 'status', 'default')
        self.printer_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Configurar colunas
        self.printer_tree.heading('name', text='Nome')
        self.printer_tree.heading('type', text='Tipo')
        self.printer_tree.heading('status', text='Status')
        self.printer_tree.heading('default', text='Padrão')
        
        self.printer_tree.column('name', width=200)
        self.printer_tree.column('type', width=100)
        self.printer_tree.column('status', width=100)
        self.printer_tree.column('default', width=80)
        
        # Scrollbar para lista
        tree_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.printer_tree.yview)
        self.printer_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.printer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10))
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        
        # Botões de ação para lista - Layout vertical (um por linha)
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botão Testar Conexão
        test_button = ttk.Button(list_buttons_frame, text="🔍 Testar Conexão", 
                                command=self.test_selected_printer)
        test_button.pack(fill=tk.X, pady=(0, 5))
        
        # Botão Teste com Padrão
        test_pattern_button = ttk.Button(list_buttons_frame, text="🖨️ Teste com Padrão", 
                                        command=self.test_printer_with_pattern)
        test_pattern_button.pack(fill=tk.X, pady=(0, 5))
        
        # Botão Definir como Padrão
        default_button = ttk.Button(list_buttons_frame, text="⭐ Definir como Padrão", 
                                   command=self.set_as_default)
        default_button.pack(fill=tk.X, pady=(0, 5))
        
        # Botão Editar
        edit_button = ttk.Button(list_buttons_frame, text="✏️ Editar Impressora", 
                                command=self.edit_selected_printer)
        edit_button.pack(fill=tk.X, pady=(0, 5))
        
        # Botão Remover
        remove_button = ttk.Button(list_buttons_frame, text="🗑️ Remover Impressora", 
                                  command=self.remove_selected_printer)
        remove_button.pack(fill=tk.X)
        
        # Frame de configuração rápida
        config_frame = ttk.LabelFrame(main_frame, text="Configuração Rápida", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botões de configuração rápida
        quick_buttons_frame = ttk.Frame(config_frame)
        quick_buttons_frame.pack(fill=tk.X)
        
        usb_button = ttk.Button(quick_buttons_frame, text="➕ Adicionar USB", 
                               command=self.add_usb_printer, style='Accent.TButton')
        usb_button.pack(side=tk.LEFT, padx=(0, 10))
        
        network_button = ttk.Button(quick_buttons_frame, text="🌐 Adicionar Rede", 
                                   command=self.add_network_printer, style='Accent.TButton')
        network_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = ttk.Button(quick_buttons_frame, text="🔄 Atualizar Lista", 
                                   command=self.load_printers)
        refresh_button.pack(side=tk.RIGHT)
        
        # Frame de botões principais
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(15, 0))
        
        close_button = ttk.Button(action_frame, text="🚪 Fechar", 
                                 command=self.close_window)
        close_button.pack(side=tk.RIGHT)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="", foreground='blue')
        self.status_label.pack(pady=(10, 0))
    
    def load_printers(self):
        """Carrega lista de impressoras"""
        try:
            # Limpar lista atual
            for item in self.printer_tree.get_children():
                self.printer_tree.delete(item)
            
            # Carregar configurações
            printers = self.printer_config.get_all_printers()
            default_printer = self.printer_config.config.get('default_printer')
            
            if not printers:
                self.status_label.config(text="Nenhuma impressora configurada", foreground='orange')
                return
            
            # Adicionar impressoras à lista
            for printer_id, config in printers.items():
                name = config.get('name', printer_id)
                printer_type = config.get('type', 'unknown').upper()
                enabled = config.get('enabled', False)
                status = "Habilitada" if enabled else "Desabilitada"
                is_default = "Sim" if printer_id == default_printer else "Não"
                
                # Adicionar à árvore usando printer_id como item ID
                item = self.printer_tree.insert('', 'end', iid=printer_id, values=(name, printer_type, status, is_default))
            
            self.status_label.config(text=f"{len(printers)} impressora(s) configurada(s)", foreground='green')
            
        except Exception as e:
            log_error(f"Erro ao carregar impressoras: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
    
    def test_selected_printer(self):
        """Testa conexão da impressora selecionada"""
        selected = self.printer_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma impressora para testar.")
            return
        
        try:
            # Obter ID da impressora (que é o item ID)
            item = selected[0]
            printer_id = item  # O item ID é o printer_id
            
            if not printer_id:
                messagebox.showerror("Erro", "Impressora não encontrada.")
                return
            
            # Obter nome da impressora para exibição
            printer_name = self.printer_tree.item(item)['values'][0]
            
            self.status_label.config(text="Testando conexão...", foreground='blue')
            self.root.update()
            
            # Testar conexão
            success = self.printer_config.test_connection(printer_id)
            
            if success:
                self.status_label.config(text="✅ Conexão bem-sucedida!", foreground='green')
                messagebox.showinfo("Sucesso", f"Conexão com '{printer_name}' bem-sucedida!")
            else:
                self.status_label.config(text="❌ Falha na conexão", foreground='red')
                messagebox.showerror("Erro", f"Falha na conexão com '{printer_name}'.")
                
        except Exception as e:
            log_error(f"Erro ao testar impressora: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro ao testar impressora:\n{str(e)}")
    
    def test_printer_with_pattern(self):
        """Testa impressora selecionada enviando padrão de teste"""
        selected = self.printer_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma impressora para testar com padrão.")
            return
        
        try:
            # Obter ID da impressora (que é o item ID)
            item = selected[0]
            printer_id = item  # O item ID é o printer_id
            
            if not printer_id:
                messagebox.showerror("Erro", "Impressora não encontrada.")
                return
            
            # Obter nome da impressora para exibição
            printer_name = self.printer_tree.item(item)['values'][0]
            
            # Confirmar envio do padrão de teste
            result = messagebox.askyesno(
                "Confirmar Teste", 
                f"Deseja enviar um padrão de teste para '{printer_name}'?\n\n"
                "Isso irá imprimir uma etiqueta de teste na impressora."
            )
            
            if not result:
                return
            
            self.status_label.config(text="Enviando padrão de teste...", foreground='blue')
            self.root.update()
            
            # Testar conexão com padrão
            success = self.printer_config.test_connection(printer_id, send_test_pattern=True)
            
            if success:
                self.status_label.config(text="✅ Padrão de teste enviado!", foreground='green')
                messagebox.showinfo("Sucesso", 
                                   f"Padrão de teste enviado para '{printer_name}'!\n\n"
                                   "Verifique se a etiqueta foi impressa corretamente.")
            else:
                self.status_label.config(text="❌ Falha no envio do padrão", foreground='red')
                messagebox.showerror("Erro", 
                                   f"Falha ao enviar padrão de teste para '{printer_name}'.\n\n"
                                   "Verifique a conexão e configurações da impressora.")
                
        except Exception as e:
            log_error(f"Erro ao testar impressora com padrão: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro ao testar impressora com padrão:\n{str(e)}")
    
    def set_as_default(self):
        """Define impressora selecionada como padrão"""
        selected = self.printer_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma impressora para definir como padrão.")
            return
        
        try:
            # Obter ID da impressora
            item = selected[0]
            printer_name = self.printer_tree.item(item)['values'][0]
            
            # Buscar pelo nome na configuração
            printer_id = None
            for pid, config in self.printer_config.get_all_printers().items():
                if config.get('name') == printer_name:
                    printer_id = pid
                    break
            
            if not printer_id:
                messagebox.showerror("Erro", "Impressora não encontrada.")
                return
            
            # Definir como padrão
            if self.printer_config.set_default_printer(printer_id):
                self.status_label.config(text=f"'{printer_name}' definida como padrão", foreground='green')
                self.load_printers()  # Recarregar lista
                log_info(f"Impressora padrão alterada para: {printer_name}")
            else:
                messagebox.showerror("Erro", "Falha ao definir impressora como padrão.")
                
        except Exception as e:
            log_error(f"Erro ao definir impressora padrão: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao definir impressora padrão:\n{str(e)}")
    
    def edit_selected_printer(self):
        """Edita impressora selecionada"""
        selected = self.printer_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma impressora para editar.")
            return
        
        try:
            # Obter ID da impressora (que é o item ID)
            item = selected[0]
            printer_id = item  # O item ID é o printer_id
            
            # Obter configuração atual
            printer_config = self.printer_config.get_printer(printer_id)
            if not printer_config:
                messagebox.showerror("Erro", "Impressora não encontrada.")
                return
            
            # Abrir diálogo de edição
            self.open_edit_printer_dialog(printer_id, printer_config)
            
        except Exception as e:
            log_error(f"Erro ao editar impressora: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao editar impressora:\n{str(e)}")
    
    def open_edit_printer_dialog(self, printer_id: str, current_config: dict):
        """Abre diálogo para editar impressora"""
        try:
            # Criar janela de edição
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Editar Impressora - {current_config.get('name', printer_id)}")
            edit_window.geometry("500x600")
            edit_window.resizable(False, False)
            edit_window.transient(self.root)
            edit_window.grab_set()
            
            # Centralizar janela
            edit_window.update_idletasks()
            x = (edit_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (edit_window.winfo_screenheight() // 2) - (600 // 2)
            edit_window.geometry(f"+{x}+{y}")
            
            # Criar interface de edição (reutilizando lógica de adição)
            self.create_edit_printer_form(edit_window, printer_id, current_config)
            
        except Exception as e:
            log_error(f"Erro ao abrir diálogo de edição: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir edição:\n{str(e)}")
    
    def create_edit_printer_form(self, parent_window, printer_id: str, current_config: dict):
        """Cria formulário de edição de impressora"""
        # Frame principal
        main_frame = ttk.Frame(parent_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Editar Configuração da Impressora", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Nome da impressora
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(name_frame, text="Nome da Impressora:").pack(anchor=tk.W)
        name_entry = ttk.Entry(name_frame, font=('Arial', 10))
        name_entry.pack(fill=tk.X, pady=(5, 0))
        name_entry.insert(0, current_config.get('name', ''))
        
        # Tipo de conexão
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(type_frame, text="Tipo de Conexão:").pack(anchor=tk.W)
        type_var = tk.StringVar(value=current_config.get('connection', {}).get('mode', 'network'))
        
        type_radio_frame = ttk.Frame(type_frame)
        type_radio_frame.pack(fill=tk.X, pady=(5, 0))
        
        usb_radio = ttk.Radiobutton(type_radio_frame, text="🔌 USB", 
                                   variable=type_var, value="usb")
        usb_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        network_radio = ttk.Radiobutton(type_radio_frame, text="🌐 Rede", 
                                       variable=type_var, value="network")
        network_radio.pack(side=tk.LEFT)
        
        # Frame para configurações de rede
        network_frame = ttk.LabelFrame(main_frame, text="Configurações de Rede", padding="15")
        network_frame.pack(fill=tk.X, pady=(0, 15))
        
        # IP
        ip_frame = ttk.Frame(network_frame)
        ip_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ip_frame, text="Endereço IP:").pack(anchor=tk.W)
        ip_entry = ttk.Entry(ip_frame)
        ip_entry.pack(fill=tk.X, pady=(5, 0))
        ip_entry.insert(0, current_config.get('connection', {}).get('ip_address', ''))
        
        # Porta
        port_frame = ttk.Frame(network_frame)
        port_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(port_frame, text="Porta:").pack(anchor=tk.W)
        port_entry = ttk.Entry(port_frame)
        port_entry.pack(fill=tk.X, pady=(5, 0))
        port_entry.insert(0, str(current_config.get('connection', {}).get('port', 9100)))
        
        # Frame para configurações USB
        usb_frame = ttk.LabelFrame(main_frame, text="Configurações USB", padding="15")
        usb_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(usb_frame, text="Nome do Dispositivo:").pack(anchor=tk.W)
        device_entry = ttk.Entry(usb_frame)
        device_entry.pack(fill=tk.X, pady=(5, 0))
        device_entry.insert(0, current_config.get('connection', {}).get('device_name', 'ZDesigner GK420t'))
        
        # Status da impressora
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        enabled_var = tk.BooleanVar(value=current_config.get('enabled', True))
        enabled_check = ttk.Checkbutton(status_frame, text="Impressora habilitada", 
                                       variable=enabled_var)
        enabled_check.pack(anchor=tk.W)
        
        # Função para alternar visibilidade dos frames
        def toggle_connection_frames():
            if type_var.get() == 'network':
                network_frame.pack(fill=tk.X, pady=(0, 15), before=usb_frame)
                usb_frame.pack_forget()
            else:
                usb_frame.pack(fill=tk.X, pady=(0, 15), before=status_frame)
                network_frame.pack_forget()
        
        # Vincular mudança de tipo
        type_var.trace('w', lambda *args: toggle_connection_frames())
        toggle_connection_frames()  # Aplicar estado inicial
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_changes():
            try:
                # Validar dados
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("Erro", "Nome da impressora é obrigatório.")
                    return
                
                # Montar configuração atualizada
                updated_config = current_config.copy()
                updated_config['name'] = name
                updated_config['enabled'] = enabled_var.get()
                
                if type_var.get() == 'network':
                    ip = ip_entry.get().strip()
                    port_str = port_entry.get().strip()
                    
                    if not ip:
                        messagebox.showerror("Erro", "Endereço IP é obrigatório para conexão de rede.")
                        return
                    
                    try:
                        port = int(port_str) if port_str else 9100
                    except ValueError:
                        messagebox.showerror("Erro", "Porta deve ser um número válido.")
                        return
                    
                    updated_config['connection'] = {
                        'mode': 'network',
                        'ip_address': ip,
                        'port': port,
                        'timeout': 5
                    }
                else:  # USB
                    device = device_entry.get().strip()
                    if not device:
                        messagebox.showerror("Erro", "Nome do dispositivo USB é obrigatório.")
                        return
                    
                    updated_config['connection'] = {
                        'mode': 'usb',
                        'device_name': device,
                        'port': None
                    }
                
                # Atualizar configuração
                if self.printer_config.update_printer(printer_id, updated_config):
                    self.status_label.config(text=f"'{name}' atualizada com sucesso", foreground='green')
                    self.load_printers()  # Recarregar lista
                    log_info(f"Impressora editada: {name}")
                    parent_window.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar impressora.")
                    
            except Exception as e:
                log_error(f"Erro ao salvar alterações: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
        
        def cancel_edit():
            parent_window.destroy()
        
        # Botões Salvar e Cancelar
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", command=cancel_edit)
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(buttons_frame, text="Salvar Alterações", 
                                command=save_changes, style='Accent.TButton')
        save_button.pack(side=tk.RIGHT)
    
    def remove_selected_printer(self):
        """Remove impressora selecionada"""
        selected = self.printer_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma impressora para remover.")
            return
        
        try:
            # Obter ID da impressora (que é o item ID)
            item = selected[0]
            printer_id = item  # O item ID é o printer_id
            printer_name = self.printer_tree.item(item)['values'][0]
            
            # Confirmar remoção
            result = messagebox.askyesno("Confirmar Remoção", 
                                       f"Tem certeza que deseja remover a impressora '{printer_name}'?\n\n"
                                       "Esta ação não pode ser desfeita.")
            if not result:
                return
            
            # Remover impressora
            if self.printer_config.remove_printer(printer_id):
                self.status_label.config(text=f"'{printer_name}' removida com sucesso", foreground='green')
                self.load_printers()  # Recarregar lista
                log_info(f"Impressora removida: {printer_name} (ID: {printer_id})")
            else:
                messagebox.showerror("Erro", "Falha ao remover impressora.")
                
        except Exception as e:
            log_error(f"Erro ao remover impressora: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao remover impressora:\n{str(e)}")
    
    def add_usb_printer(self):
        """Abre diálogo para adicionar impressora USB"""
        dialog = PrinterDialog(self.root, "usb")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            config = dialog.result
            if self.printer_config.add_printer(config):
                self.status_label.config(text=f"Impressora USB '{config['name']}' adicionada", foreground='green')
                self.load_printers()
                log_info(f"Impressora USB adicionada: {config['name']}")
            else:
                messagebox.showerror("Erro", "Falha ao adicionar impressora USB.")
    
    def add_network_printer(self):
        """Abre diálogo para adicionar impressora de rede"""
        dialog = PrinterDialog(self.root, "network")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            config = dialog.result
            if self.printer_config.add_printer(config):
                self.status_label.config(text=f"Impressora de rede '{config['name']}' adicionada", foreground='green')
                self.load_printers()
                log_info(f"Impressora de rede adicionada: {config['name']}")
            else:
                messagebox.showerror("Erro", "Falha ao adicionar impressora de rede.")
    
    def close_window(self):
        """Fecha a janela"""
        log_info("Fechando janela de configuração de impressoras")
        try:
            # Liberar o grab se estiver modal
            if self.parent:
                self.root.grab_release()
        except:
            pass
        self.root.destroy()


class PrinterDialog:
    """Diálogo para adicionar/editar impressora"""
    
    def __init__(self, parent, printer_type: str, printer_config: dict = None):
        """
        Inicializa diálogo
        
        Args:
            parent: Janela pai
            printer_type: Tipo da impressora ('usb' ou 'network')
            printer_config: Configuração existente (para edição)
        """
        self.result = None
        self.printer_type = printer_type
        self.editing = printer_config is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Editar' if self.editing else 'Adicionar'} Impressora {printer_type.upper()}")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Centralizar
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_dialog()
        
        # Criar widgets
        self.create_widgets(printer_config)
    
    def center_dialog(self):
        """Centraliza o diálogo"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self, config: dict = None):
        """Cria widgets do diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = f"{'Editar' if self.editing else 'Adicionar'} Impressora {self.printer_type.upper()}"
        title_label = ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Informações básicas
        info_frame = ttk.LabelFrame(main_frame, text="Informações Básicas", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Nome
        ttk.Label(info_frame, text="Nome da impressora:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(info_frame, width=40, font=('Arial', 10))
        self.name_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Habilitada
        self.enabled_var = tk.BooleanVar(value=True)
        enabled_check = ttk.Checkbutton(info_frame, text="Impressora habilitada", 
                                       variable=self.enabled_var)
        enabled_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Configurações de conexão
        conn_frame = ttk.LabelFrame(main_frame, text="Configurações de Conexão", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        if self.printer_type == "usb":
            self.create_usb_widgets(conn_frame)
        else:
            self.create_network_widgets(conn_frame)
        
        # Configurações de impressão
        print_frame = ttk.LabelFrame(main_frame, text="Configurações de Impressão", padding="10")
        print_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_print_settings_widgets(print_frame)
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_button = ttk.Button(buttons_frame, text="💾 Salvar", 
                                command=self.save_printer, style='Accent.TButton')
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        test_button = ttk.Button(buttons_frame, text="🔍 Testar", 
                                command=self.test_printer)
        test_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = ttk.Button(buttons_frame, text="❌ Cancelar", 
                                  command=self.cancel)
        cancel_button.pack(side=tk.RIGHT)
        
        # Preencher valores se editando
        if config:
            self.load_config_values(config)
    
    def create_usb_widgets(self, parent):
        """Cria widgets para configuração USB"""
        ttk.Label(parent, text="Nome do dispositivo:").pack(anchor=tk.W)
        self.device_entry = ttk.Entry(parent, width=40, font=('Arial', 10))
        self.device_entry.pack(fill=tk.X, pady=(5, 10))
        self.device_entry.insert(0, "ZDesigner GK420t")
        
        info_label = ttk.Label(parent, text="💡 Nome padrão da Zebra GK420t no Windows", 
                              foreground='gray', font=('Arial', 9))
        info_label.pack(anchor=tk.W)
    
    def create_network_widgets(self, parent):
        """Cria widgets para configuração de rede"""
        # IP
        ttk.Label(parent, text="Endereço IP:").pack(anchor=tk.W)
        self.ip_entry = ttk.Entry(parent, width=40, font=('Arial', 10))
        self.ip_entry.pack(fill=tk.X, pady=(5, 10))
        self.ip_entry.insert(0, "192.168.1.100")
        
        # Porta
        port_frame = ttk.Frame(parent)
        port_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(port_frame, text="Porta:").pack(side=tk.LEFT)
        self.port_entry = ttk.Entry(port_frame, width=10, font=('Arial', 10))
        self.port_entry.pack(side=tk.LEFT, padx=(10, 20))
        self.port_entry.insert(0, "9100")
        
        ttk.Label(port_frame, text="Timeout (s):").pack(side=tk.LEFT)
        self.timeout_entry = ttk.Entry(port_frame, width=10, font=('Arial', 10))
        self.timeout_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.timeout_entry.insert(0, "5")
    
    def create_print_settings_widgets(self, parent):
        """Cria widgets para configurações de impressão"""
        # Grid para organizar campos
        settings_grid = ttk.Frame(parent)
        settings_grid.pack(fill=tk.X)
        
        # Velocidade
        ttk.Label(settings_grid, text="Velocidade:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.speed_var = tk.StringVar(value="2")
        speed_combo = ttk.Combobox(settings_grid, textvariable=self.speed_var, 
                                  values=["1", "2", "3", "4", "5"], width=10, state="readonly")
        speed_combo.grid(row=0, column=1, padx=(10, 20), pady=2)
        
        # Escuridão
        ttk.Label(settings_grid, text="Escuridão:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.darkness_var = tk.StringVar(value="8")
        darkness_combo = ttk.Combobox(settings_grid, textvariable=self.darkness_var,
                                     values=[str(i) for i in range(1, 31)], width=10, state="readonly")
        darkness_combo.grid(row=0, column=3, padx=(10, 0), pady=2)
        
        # Largura da etiqueta
        ttk.Label(settings_grid, text="Largura etiqueta:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.label_width_entry = ttk.Entry(settings_grid, width=15, font=('Arial', 10))
        self.label_width_entry.grid(row=1, column=1, padx=(10, 20), pady=2)
        self.label_width_entry.insert(0, "100mm")
        
        # Altura da etiqueta
        ttk.Label(settings_grid, text="Altura etiqueta:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.label_height_entry = ttk.Entry(settings_grid, width=15, font=('Arial', 10))
        self.label_height_entry.grid(row=1, column=3, padx=(10, 0), pady=2)
        self.label_height_entry.insert(0, "50mm")
    
    def load_config_values(self, config: dict):
        """Carrega valores de configuração existente"""
        # Informações básicas
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, config.get('name', ''))
        self.enabled_var.set(config.get('enabled', True))
        
        # Conexão
        connection = config.get('connection', {})
        if self.printer_type == "usb":
            device_name = connection.get('device_name', '')
            self.device_entry.delete(0, tk.END)
            self.device_entry.insert(0, device_name)
        else:
            ip_address = connection.get('ip_address', '')
            port = connection.get('port', 9100)
            timeout = connection.get('timeout', 5)
            
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, ip_address)
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(port))
            self.timeout_entry.delete(0, tk.END)
            self.timeout_entry.insert(0, str(timeout))
        
        # Configurações de impressão
        settings = config.get('settings', {})
        self.speed_var.set(settings.get('print_speed', '2'))
        self.darkness_var.set(settings.get('darkness', '8'))
        
        label_width = settings.get('label_width', '100mm')
        self.label_width_entry.delete(0, tk.END)
        self.label_width_entry.insert(0, label_width)
        
        label_height = settings.get('label_height', '50mm')
        self.label_height_entry.delete(0, tk.END)
        self.label_height_entry.insert(0, label_height)
    
    def save_printer(self):
        """Salva configuração da impressora"""
        try:
            # Validar dados
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Erro", "Nome da impressora é obrigatório.")
                return
            
            # Gerar ID único
            import time
            printer_id = f"{self.printer_type}_{int(time.time())}"
            
            # Configuração básica
            config = {
                "id": printer_id,
                "name": name,
                "type": self.printer_type,
                "enabled": self.enabled_var.get(),
                "connection": {},
                "settings": {
                    "print_speed": self.speed_var.get(),
                    "darkness": self.darkness_var.get(),
                    "print_width": "104mm",
                    "label_width": self.label_width_entry.get().strip(),
                    "label_height": self.label_height_entry.get().strip(),
                    "dpi": "203"
                }
            }
            
            # Configuração de conexão
            if self.printer_type == "usb":
                config["connection"] = {
                    "mode": "usb",
                    "device_name": self.device_entry.get().strip(),
                    "port": None
                }
            else:
                try:
                    port = int(self.port_entry.get().strip())
                    timeout = int(self.timeout_entry.get().strip())
                except ValueError:
                    messagebox.showerror("Erro", "Porta e timeout devem ser números.")
                    return
                
                config["connection"] = {
                    "mode": "network",
                    "ip_address": self.ip_entry.get().strip(),
                    "port": port,
                    "timeout": timeout
                }
            
            self.result = config
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração:\n{str(e)}")
    
    def test_printer(self):
        """Testa configuração atual"""
        # TODO: Implementar teste de configuração
        messagebox.showinfo("Teste", "Funcionalidade de teste será implementada.")
    
    def cancel(self):
        """Cancela operação"""
        self.dialog.destroy()
