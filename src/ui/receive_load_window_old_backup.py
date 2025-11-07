#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janela de Recebimento Físico de Cargas
Fluxo: Galpão → Área → Buscar Carga → Aceitar/Ressalvas/Rejeitar
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Optional, Dict, Any, List

from api.client import APIClient
from utils.logger import log_info, log_error
from utils.validators import format_cpf


class ReceiveLoadWindow:
    """Janela para recebimento físico de cargas"""
    
    def __init__(self, cpf: str, token: str, user_data: Dict[str, Any]):
        """
        Inicializa a janela de recebimento
        
        Args:
            cpf: CPF do usuário
            token: Token de autenticação
            user_data: Dados do usuário logado
        """
        self.cpf = cpf
        self.token = token
        self.user_data = user_data
        
        # Inicializar API Client
        self.api_client = APIClient()
        self.api_client.token = token
        
        # Dados de seleção
        self.warehouses = []
        self.warehouse_dict = {}  # nome -> id
        self.areas = []
        self.area_dict = {}  # nome -> id
        self.current_cargo = None
        
        # IDs selecionados
        self.selected_warehouse_id = None
        self.selected_area_id = None
        
        # Criar janela
        self.root = tk.Toplevel()
        self.root.title("Recebimento Físico de Cargas")
        self.root.geometry("750x800")
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.center_window()
        
        # Carregar galpões
        self.load_warehouses()
        
        # Criar interface
        self.create_widgets()
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_warehouses(self):
        """Carrega lista de galpões da API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Usar endpoint de seleção de galpões
            response = self.api_client.get('/warehouses/select', headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success') and result.get('data'):
                    self.warehouses = result['data']
                    
                    # Criar mapeamento nome -> id
                    for warehouse in self.warehouses:
                        warehouse_name = warehouse.get('name', 'N/A')
                        warehouse_id = warehouse.get('id')
                        self.warehouse_dict[warehouse_name] = warehouse_id
                    
                    log_info(f"Carregados {len(self.warehouses)} galpões")
                else:
                    log_error("Resposta da API de galpões sem dados")
                    self.warehouses = []
            else:
                log_error(f"Erro ao carregar galpões: HTTP {response.status_code}")
                self.warehouses = []
                
        except Exception as e:
            log_error(f"Erro ao carregar galpões: {str(e)}")
            self.warehouses = []
    
    def load_areas(self, warehouse_id: int):
        """Carrega áreas de um galpão específico"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = self.api_client.get(
                f'/warehouses/{warehouse_id}/areas',
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success') and result.get('data'):
                    data = result['data']
                    self.areas = data.get('areas', [])
                    
                    # Criar mapeamento nome -> id
                    self.area_dict = {}
                    for area in self.areas:
                        area_name = area.get('name', 'N/A')
                        area_id = area.get('id')
                        self.area_dict[area_name] = area_id
                    
                    log_info(f"Carregadas {len(self.areas)} áreas do galpão {warehouse_id}")
                    return True
                else:
                    log_error("Resposta da API de áreas sem dados")
                    self.areas = []
                    return False
            else:
                log_error(f"Erro ao carregar áreas: HTTP {response.status_code}")
                self.areas = []
                return False
                
        except Exception as e:
            log_error(f"Erro ao carregar áreas: {str(e)}")
            self.areas = []
            return False
        
    def create_widgets(self):
        """Cria os widgets da interface com fluxo em etapas"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== CABEÇALHO ==========
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                               text="📦 Recebimento Físico de Cargas",
                               font=('Arial', 14, 'bold'))
        title_label.pack()
        
        user_label = ttk.Label(header_frame,
                              text=f"Operador: {self.user_data.get('name', 'N/A')} | CPF: {format_cpf(self.cpf)}",
                              font=('Arial', 9))
        user_label.pack(pady=(3, 0))
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=8)
        
        # Frame de busca
        search_frame = ttk.LabelFrame(main_frame, text="1. Buscar Carga por Código", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Campo de código
        code_label = ttk.Label(search_frame, text="Código da Carga (Romaneio):")
        code_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        code_frame = ttk.Frame(search_frame)
        code_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        self.code_entry = ttk.Entry(code_frame, font=('Arial', 12), width=30)
        self.code_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.code_entry.bind('<Return>', lambda e: self.search_cargo())
        
        search_button = ttk.Button(code_frame, text="🔍 Buscar", command=self.search_cargo)
        search_button.pack(side=tk.LEFT)
        
        # Instrução
        info_label = ttk.Label(search_frame, 
                              text="💡 Digite o código da carga e pressione Enter ou clique em Buscar",
                              font=('Arial', 9), foreground='#666')
        info_label.grid(row=2, column=0, sticky='w')
        
        # Frame de informações da carga
        self.cargo_frame = ttk.LabelFrame(main_frame, text="2. Informações da Carga", padding="10")
        self.cargo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Text widget para exibir informações
        text_frame = ttk.Frame(self.cargo_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cargo_text = tk.Text(text_frame, height=15, width=70, 
                                  font=('Courier', 10), state='disabled',
                                  wrap=tk.WORD, bg='#f9f9f9')
        self.cargo_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', 
                                 command=self.cargo_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cargo_text.config(yscrollcommand=scrollbar.set)
        
        # Mostrar mensagem inicial
        self.show_cargo_info("Nenhuma carga carregada.\nBusque uma carga pelo código para continuar.")
        
        # Frame de recebimento
        receive_frame = ttk.LabelFrame(main_frame, text="3. Confirmar Recebimento", padding="10")
        receive_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Galpão (warehouse_id) - obrigatório
        warehouse_label = ttk.Label(receive_frame, text="Galpão:*")
        warehouse_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.warehouse_combo = ttk.Combobox(receive_frame, font=('Arial', 10), 
                                           state='readonly', width=25)
        
        # Preencher combobox com nomes dos galpões
        if self.warehouses:
            warehouse_names = [w.get('name', 'N/A') for w in self.warehouses]
            self.warehouse_combo['values'] = warehouse_names
            
            # Selecionar primeiro galpão por padrão
            if warehouse_names:
                self.warehouse_combo.current(0)
        else:
            self.warehouse_combo['values'] = ['Nenhum galpão disponível']
            self.warehouse_combo.current(0)
        
        self.warehouse_combo.grid(row=1, column=0, sticky='ew', padx=(0, 10))
        
        # Área (área_id) - opcional
        area_label = ttk.Label(receive_frame, text="ID da Área (opcional):")
        area_label.grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        self.area_entry = ttk.Entry(receive_frame, font=('Arial', 10), width=15)
        self.area_entry.grid(row=1, column=1, sticky='ew')
        
        receive_frame.columnconfigure(0, weight=1)
        receive_frame.columnconfigure(1, weight=1)
        
        # Tipo de área (opcional)
        area_type_label = ttk.Label(receive_frame, text="Tipo de Área (opcional):")
        area_type_label.grid(row=2, column=0, sticky='w', pady=(10, 5))
        
        self.area_type_combo = ttk.Combobox(receive_frame, font=('Arial', 10), 
                                           state='readonly', width=18)
        self.area_type_combo['values'] = ('', 'RECEBIMENTO', 'CONFERENCIA', 
                                          'ARMAZENAGEM', 'SEPARACAO', 
                                          'EXPEDICAO', 'DOCA')
        self.area_type_combo.grid(row=3, column=0, sticky='ew', padx=(0, 10))
        
        # Endereço específico (opcional)
        address_label = ttk.Label(receive_frame, text="Endereço Específico (opcional):")
        address_label.grid(row=2, column=1, sticky='w', pady=(10, 5))
        
        self.address_entry = ttk.Entry(receive_frame, font=('Arial', 10), width=18)
        self.address_entry.grid(row=3, column=1, sticky='ew')
        
        # Observações (opcional)
        notes_label = ttk.Label(receive_frame, text="Observações (opcional):")
        notes_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.notes_entry = ttk.Entry(receive_frame, font=('Arial', 10))
        self.notes_entry.grid(row=5, column=0, columnspan=2, sticky='ew')
        
        # Botões de ação
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.receive_button = ttk.Button(buttons_frame, 
                                        text="✅ Confirmar Recebimento",
                                        command=self.receive_cargo,
                                        state='disabled')
        self.receive_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ttk.Button(buttons_frame, 
                                 text="🔄 Limpar",
                                 command=self.clear_form)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        close_button = ttk.Button(buttons_frame, 
                                 text="❌ Fechar",
                                 command=self.root.destroy)
        close_button.pack(side=tk.RIGHT)
        
    def search_cargo(self):
        """Busca carga por código"""
        code = self.code_entry.get().strip()
        
        if not code:
            messagebox.showwarning("Atenção", "Digite o código da carga.")
            self.code_entry.focus()
            return
        
        try:
            # Buscar carga na API
            self.show_cargo_info("🔍 Buscando carga...", clear=True)
            self.root.update()
            
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Buscar na API de cargas pendentes de recebimento físico
            response = self.api_client.get(
                f'/cargos/pending-physical-receipt',
                headers=headers,
                params={'code': code, 'per_page': 1}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success') and result.get('data'):
                    cargas = result['data']
                    
                    if len(cargas) > 0:
                        self.current_cargo = cargas[0]
                        self.display_cargo_details(self.current_cargo)
                        self.receive_button.config(state='normal')
                        log_info(f"Carga {code} encontrada para recebimento")
                    else:
                        self.show_cargo_info(
                            f"❌ Carga '{code}' não encontrada ou já recebida.\n\n"
                            "Verifique:\n"
                            "• O código está correto?\n"
                            "• A carga já foi recebida fisicamente?\n"
                            "• A carga existe no sistema?"
                        )
                        self.current_cargo = None
                        self.receive_button.config(state='disabled')
                else:
                    self.show_cargo_info(
                        f"❌ Carga '{code}' não encontrada ou já recebida."
                    )
                    self.current_cargo = None
                    self.receive_button.config(state='disabled')
            else:
                raise Exception(f"Erro HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao buscar carga {code}: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao buscar carga:\n{str(e)}")
            self.show_cargo_info(f"❌ Erro ao buscar carga: {str(e)}")
            self.current_cargo = None
            self.receive_button.config(state='disabled')
            
    def display_cargo_details(self, cargo: Dict[str, Any]):
        """Exibe detalhes da carga encontrada"""
        details = []
        details.append("✅ CARGA ENCONTRADA\n")
        details.append("=" * 60)
        details.append(f"\n📦 INFORMAÇÕES DA CARGA\n")
        details.append(f"   Código: {cargo.get('code', 'N/A')}")
        details.append(f"   Código Cliente: {cargo.get('code_client', 'N/A')}")
        details.append(f"   Nota Fiscal: {cargo.get('invoice_number', 'N/A')}")
        details.append(f"   Status: {cargo.get('status', 'N/A')}")
        
        # Cliente
        customer = cargo.get('customer', {})
        if customer:
            details.append(f"\n👤 CLIENTE")
            details.append(f"   Nome: {customer.get('name', 'N/A')}")
            details.append(f"   Documento: {customer.get('document', 'N/A')}")
        
        # Tipo de carga
        cargo_type = cargo.get('cargo_type', {})
        if cargo_type:
            details.append(f"\n📦 TIPO DE CARGA")
            details.append(f"   Nome: {cargo_type.get('name', 'N/A')}")
            details.append(f"   Código: {cargo_type.get('code', 'N/A')}")
        
        # Dimensões
        details.append(f"\n📐 DIMENSÕES E PESO")
        details.append(f"   Peso: {cargo.get('weight', 'N/A')} kg")
        details.append(f"   Altura: {cargo.get('height', 'N/A')} m")
        details.append(f"   Largura: {cargo.get('width', 'N/A')} m")
        details.append(f"   Profundidade: {cargo.get('depth', 'N/A')} m")
        details.append(f"   Volume: {cargo.get('volume', 'N/A')} m³")
        
        # Datas
        details.append(f"\n📅 DATAS")
        details.append(f"   Recebido em: {cargo.get('received_at', 'N/A')}")
        
        # Descrição
        if cargo.get('description'):
            details.append(f"\n📝 DESCRIÇÃO")
            details.append(f"   {cargo.get('description')}")
        
        details.append("\n" + "=" * 60)
        details.append("\n✅ Carga pronta para recebimento físico")
        
        self.show_cargo_info("\n".join(details))
        
    def show_cargo_info(self, text: str, clear: bool = False):
        """Exibe informações no text widget"""
        self.cargo_text.config(state='normal')
        
        if clear:
            self.cargo_text.delete('1.0', tk.END)
        else:
            self.cargo_text.delete('1.0', tk.END)
            
        self.cargo_text.insert('1.0', text)
        self.cargo_text.config(state='disabled')
        
    def receive_cargo(self):
        """Confirma o recebimento físico da carga"""
        if not self.current_cargo:
            messagebox.showwarning("Atenção", "Nenhuma carga selecionada.")
            return
        
        # Validar warehouse_id
        warehouse_name = self.warehouse_combo.get().strip()
        if not warehouse_name or warehouse_name == 'Nenhum galpão disponível':
            messagebox.showwarning("Atenção", "Selecione um galpão válido.")
            self.warehouse_combo.focus()
            return
        
        # Obter ID do galpão pelo nome
        warehouse_id = self.warehouse_dict.get(warehouse_name)
        if not warehouse_id:
            messagebox.showwarning("Atenção", "Galpão selecionado inválido.")
            return
        
        # Confirmar recebimento
        cargo_code = self.current_cargo.get('code', 'N/A')
        confirm = messagebox.askyesno(
            "Confirmar Recebimento",
            f"Confirma o recebimento físico da carga:\n\n"
            f"Código: {cargo_code}\n"
            f"Cliente: {self.current_cargo.get('customer', {}).get('name', 'N/A')}\n"
            f"Galpão: {warehouse_name}\n\n"
            f"Esta ação será registrada no sistema."
        )
        
        if not confirm:
            return
        
        try:
            # Preparar dados
            cargo_id = self.current_cargo['id']
            
            payload = {
                'warehouse_id': int(warehouse_id)
            }
            
            # Adicionar campos opcionais se preenchidos
            area_id = self.area_entry.get().strip()
            if area_id and area_id.isdigit():
                payload['area_id'] = int(area_id)
            
            area_type = self.area_type_combo.get().strip()
            if area_type:
                payload['area_type'] = area_type
            
            specific_address = self.address_entry.get().strip()
            if specific_address:
                payload['specific_address'] = specific_address
            
            notes = self.notes_entry.get().strip()
            if notes:
                payload['notes'] = notes
            
            # Enviar para API
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.post(
                f'/cargos/{cargo_id}/receive-physically',
                data=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    # Sucesso
                    received_data = result.get('data', {})
                    received_cargo = received_data.get('cargo', {})
                    
                    log_info(
                        f"Carga {cargo_code} recebida fisicamente por "
                        f"{self.user_data.get('name')} no galpão {warehouse_name} (ID: {warehouse_id})"
                    )
                    
                    messagebox.showinfo(
                        "Sucesso",
                        f"✅ Carga recebida com sucesso!\n\n"
                        f"Código: {cargo_code}\n"
                        f"Status: {received_cargo.get('status', 'STORED')}\n"
                        f"Localização: {received_cargo.get('current_address', 'Galpão')}\n"
                        f"Recebido por: {received_data.get('received_by', 'N/A')}\n"
                        f"Data/Hora: {received_data.get('received_at', 'N/A')}"
                    )
                    
                    # Limpar formulário
                    self.clear_form()
                else:
                    messagebox.showerror(
                        "Erro",
                        f"Falha ao receber carga:\n{result.get('message', 'Erro desconhecido')}"
                    )
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('message', f'Erro HTTP {response.status_code}')
                
                # Mostrar erros de validação se houver
                if 'errors' in error_data:
                    errors = error_data['errors']
                    error_details = []
                    for field, messages in errors.items():
                        error_details.append(f"• {field}: {', '.join(messages)}")
                    error_msg += "\n\nDetalhes:\n" + "\n".join(error_details)
                
                messagebox.showerror("Erro", f"Erro ao receber carga:\n{error_msg}")
                
        except Exception as e:
            log_error(f"Erro ao receber carga {cargo_code}: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao receber carga:\n{str(e)}")
            
    def clear_form(self):
        """Limpa o formulário"""
        self.code_entry.delete(0, tk.END)
        self.area_entry.delete(0, tk.END)
        self.area_type_combo.set('')
        self.address_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        
        # Resetar combobox de galpão para primeiro item
        if self.warehouses and self.warehouse_combo['values']:
            self.warehouse_combo.current(0)
        
        self.current_cargo = None
        self.receive_button.config(state='disabled')
        self.show_cargo_info("Nenhuma carga carregada.\nBusque uma carga pelo código para continuar.")
        
        self.code_entry.focus()
