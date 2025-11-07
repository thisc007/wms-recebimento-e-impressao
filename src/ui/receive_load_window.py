#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janela de Recebimento Físico de Cargas - Nova Versão
Fluxo: 1. Selecionar Galpão → 2. Selecionar Área → 3. Buscar Carga → 4. Aceitar/Ressalvas/Rejeitar → 5. Imprimir Etiqueta
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Optional, Dict, Any, List

from api.client import APIClient
from printer.zpl_generator import ZplGenerator
from printer.label_printer import LabelPrinter
from utils.logger import log_info, log_error
from utils.validators import format_cpf
from utils.printer_config import PrinterConfigManager


class ReceiveLoadWindow:
    """Janela para recebimento físico de cargas com fluxo otimizado"""
    
    def __init__(self, cpf: str, token: str, user_data: Dict[str, Any]):
        self.cpf = cpf
        self.token = token
        self.user_data = user_data
        
        # API Client
        self.api_client = APIClient()
        self.api_client.token = token
        
        # Gerenciadores de impressão
        self.zpl_generator = ZplGenerator()
        self.printer = LabelPrinter()
        self.printer_config_manager = PrinterConfigManager()
        
        # Dados
        self.warehouses = []
        self.warehouse_dict = {}
        self.areas = []
        self.area_dict = {}
        self.current_cargo = None
        self.configured_printers = {}
        
        # IDs selecionados
        self.selected_warehouse_id = None
        self.selected_area_id = None
        
        # Criar janela
        self.root = tk.Toplevel()
        self.root.title("Recebimento Físico de Cargas")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        
        self.center_window()
        self.load_warehouses()
        self.create_widgets()
        
    def center_window(self):
        """Centraliza janela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_warehouses(self):
        """Carrega galpões"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.get('/warehouses/select', headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    self.warehouses = result['data']
                    for w in self.warehouses:
                        self.warehouse_dict[w.get('name', 'N/A')] = w.get('id')
                    log_info(f"Carregados {len(self.warehouses)} galpões")
        except Exception as e:
            log_error(f"Erro ao carregar galpões: {e}")
            
    def load_areas(self):
        """Carrega áreas do galpão selecionado"""
        if not self.selected_warehouse_id:
            return
        
        # Verificar se area_combo já foi criado
        if not hasattr(self, 'area_combo'):
            log_info("area_combo ainda não criado, pulando load_areas")
            return
            
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.get(
                f'/warehouses/{self.selected_warehouse_id}/areas',
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    self.areas = result['data'].get('areas', [])
                    self.area_dict = {}
                    for area in self.areas:
                        area_info = f"{area.get('name')} - {area.get('type', '')} (Disponível: {area.get('available', 0)})"
                        self.area_dict[area_info] = area.get('id')
                    
                    # Atualizar combobox de áreas
                    if self.areas:
                        area_options = list(self.area_dict.keys())
                        self.area_combo['values'] = area_options
                        self.area_combo.set('-- Selecione uma área --')
                        self.area_combo.config(state='readonly')
                        log_info(f"Carregadas {len(self.areas)} áreas")
                        self.show_cargo_info(f"✅ Galpão selecionado!\n\n⚠️ PASSO 2: Selecione uma área para continuar.\n\n{len(self.areas)} área(s) disponível(is).")
                    else:
                        self.area_combo['values'] = ['Nenhuma área disponível']
                        self.area_combo.set('Nenhuma área disponível')
                        self.area_combo.config(state='disabled')
                        self.show_cargo_info("⚠️ Este galpão não possui áreas cadastradas.\n\nSelecione outro galpão.")
                        
        except Exception as e:
            log_error(f"Erro ao carregar áreas: {e}")
            if hasattr(self, 'area_combo'):
                self.area_combo['values'] = ['Erro ao carregar áreas']
                self.area_combo.set('Erro ao carregar áreas')
            
    def on_warehouse_change(self, event=None):
        """Quando galpão muda, carregar áreas e resetar seleção de área"""
        warehouse_name = self.warehouse_combo.get()
        
        # Ignorar se é o texto de placeholder
        if warehouse_name.startswith('--'):
            return
        
        self.selected_warehouse_id = self.warehouse_dict.get(warehouse_name)
        
        # Resetar área selecionada
        self.selected_area_id = None
        
        if self.selected_warehouse_id:
            self.load_areas()
        
        # Verificar se pode habilitar busca (precisa galpão E área selecionados)
        self.check_enable_search()
            
    def on_area_change(self, event=None):
        """Quando área muda, armazenar ID e verificar se pode habilitar busca"""
        area_info = self.area_combo.get()
        
        # Ignorar se é o texto de placeholder
        if area_info.startswith('--'):
            self.selected_area_id = None
            self.check_enable_search()
            return
        
        self.selected_area_id = self.area_dict.get(area_info)
        
        # Verificar se pode habilitar busca
        self.check_enable_search()
    
    def check_enable_search(self):
        """Verifica se pode habilitar campo de busca (galpão E área devem estar selecionados)"""
        if not hasattr(self, 'code_entry') or not hasattr(self, 'search_button'):
            return
        
        # Habilitar apenas se AMBOS estiverem selecionados
        if self.selected_warehouse_id and self.selected_area_id:
            self.code_entry.config(state='normal')
            self.search_button.config(state='normal')
            self.show_cargo_info("✅ Galpão e área selecionados.\n\nDigite o código da carga e clique em Buscar.")
        else:
            self.code_entry.config(state='disabled')
            self.search_button.config(state='disabled')
            
            if not self.selected_warehouse_id:
                self.show_cargo_info("⚠️ Selecione um galpão para continuar.")
            elif not self.selected_area_id:
                self.show_cargo_info("⚠️ Selecione uma área para continuar.")
        
    def create_widgets(self):
        """Cria interface"""
        main_frame = ttk.Frame(self.root, padding="8")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # CABEÇALHO COMPACTO
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 6))
        
        ttk.Label(header_frame, text="📦 Recebimento Físico de Cargas",
                 font=('Arial', 11, 'bold')).pack()
        ttk.Label(header_frame,
                 text=f"{self.user_data.get('name', 'N/A')} | {format_cpf(self.cpf)}",
                 font=('Arial', 8)).pack(pady=(2, 0))
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=4)
        
        # PASSO 1: SELECIONAR GALPÃO
        step1_frame = ttk.LabelFrame(main_frame, text="1️⃣ Galpão", padding="6")
        step1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(step1_frame, text="Galpão:*", font=('Arial', 8)).pack(anchor='w')
        self.warehouse_combo = ttk.Combobox(step1_frame, font=('Arial', 9),
                                           state='readonly', width=50)
        if self.warehouses:
            self.warehouse_combo['values'] = list(self.warehouse_dict.keys())
            # Não selecionar automaticamente, usuário deve escolher
            self.warehouse_combo.set('-- Selecione um galpão --')
        else:
            self.warehouse_combo['values'] = ['Nenhum galpão disponível']
            self.warehouse_combo.set('Nenhum galpão disponível')
        self.warehouse_combo.pack(fill=tk.X, pady=(2, 0))
        self.warehouse_combo.bind('<<ComboboxSelected>>', self.on_warehouse_change)
        
        # PASSO 2: SELECIONAR ÁREA
        step2_frame = ttk.LabelFrame(main_frame, text="2️⃣ Área", padding="6")
        step2_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(step2_frame, text="Área:*", font=('Arial', 8)).pack(anchor='w')
        self.area_combo = ttk.Combobox(step2_frame, font=('Arial', 9),
                                      state='disabled', width=50)
        self.area_combo.set('-- Selecione um galpão primeiro --')
        self.area_combo.pack(fill=tk.X, pady=(2, 0))
        self.area_combo.bind('<<ComboboxSelected>>', self.on_area_change)
        
        # PASSO 3: BUSCAR CARGA
        step3_frame = ttk.LabelFrame(main_frame, text="3️⃣ Buscar Carga", padding="6")
        step3_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(step3_frame, text="Código:*", font=('Arial', 8)).pack(anchor='w')
        
        search_frame = ttk.Frame(step3_frame)
        search_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.code_entry = ttk.Entry(search_frame, font=('Arial', 9), state='disabled')
        self.code_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.code_entry.bind('<Return>', lambda e: self.search_cargo())
        
        self.search_button = ttk.Button(search_frame, text="🔍",
                                       command=self.search_cargo, state='disabled', width=4)
        self.search_button.pack(side=tk.LEFT)
        
        # INFORMAÇÕES DA CARGA
        info_frame = ttk.LabelFrame(main_frame, text="📋 Informações", padding="3")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.cargo_text = scrolledtext.ScrolledText(info_frame, height=5,
                                                    font=('Courier', 8),
                                                    wrap=tk.WORD, state='disabled')
        self.cargo_text.pack(fill=tk.BOTH, expand=True)
        self.show_cargo_info("⚠️ PASSO 1: Selecione um galpão acima para começar.")
        
        # PASSO 4: AÇÕES
        step4_frame = ttk.LabelFrame(main_frame, text="4️⃣ Ação", padding="6")
        step4_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Campo de observações (para ressalvas ou rejeição)
        ttk.Label(step4_frame, text="Observações:", font=('Arial', 8)).pack(anchor='w')
        self.remarks_text = scrolledtext.ScrolledText(step4_frame, height=2,
                                                     font=('Arial', 8), wrap=tk.WORD)
        self.remarks_text.pack(fill=tk.X, pady=(2, 5))
        
        # Botões de ação compactos
        action_buttons = ttk.Frame(step4_frame)
        action_buttons.pack(fill=tk.X)
        
        self.accept_button = ttk.Button(action_buttons, text="✅ Aceitar",
                                       command=lambda: self.process_cargo('accept'),
                                       state='disabled', width=15)
        self.accept_button.pack(side=tk.LEFT, padx=(0, 3))
        
        self.accept_remarks_button = ttk.Button(action_buttons, text="⚠️ Com Ressalvas",
                                               command=lambda: self.process_cargo('accept_with_remarks'),
                                               state='disabled', width=18)
        self.accept_remarks_button.pack(side=tk.LEFT, padx=(0, 3))
        
        self.reject_button = ttk.Button(action_buttons, text="❌ Rejeitar",
                                       command=lambda: self.process_cargo('reject'),
                                       state='disabled', width=15)
        self.reject_button.pack(side=tk.LEFT)
        
        # PASSO 5: IMPRESSÃO
        step5_frame = ttk.LabelFrame(main_frame, text="5️⃣ Impressão", padding="6")
        step5_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Linha 1: Impressora e Quantidade
        printer_qty_frame = ttk.Frame(step5_frame)
        printer_qty_frame.pack(fill=tk.X)
        
        # Impressora
        printer_left = ttk.Frame(printer_qty_frame)
        printer_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(printer_left, text="Impressora:*", font=('Arial', 8)).pack(anchor='w')
        self.printer_combo = ttk.Combobox(printer_left, font=('Arial', 8),
                                         state='readonly', width=35)
        self.printer_combo.pack(fill=tk.X, pady=(2, 0))
        
        # Quantidade
        qty_right = ttk.Frame(printer_qty_frame)
        qty_right.pack(side=tk.LEFT)
        
        ttk.Label(qty_right, text="Qtd:*", font=('Arial', 8)).pack(anchor='w')
        self.qty_entry = ttk.Entry(qty_right, font=('Arial', 9), width=8)
        self.qty_entry.pack(pady=(2, 0))
        self.qty_entry.insert(0, "1")
        
        # Carregar impressoras configuradas
        self.load_printers()
        
        # BOTÕES INFERIORES
        bottom_buttons = ttk.Frame(main_frame)
        bottom_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(bottom_buttons, text="🔄 Limpar",
                  command=self.clear_form, width=12).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(bottom_buttons, text="❌ Fechar",
                  command=self.root.destroy, width=12).pack(side=tk.RIGHT)
                  
    def show_cargo_info(self, text: str):
        """Exibe informações da carga"""
        self.cargo_text.config(state='normal')
        self.cargo_text.delete('1.0', tk.END)
        self.cargo_text.insert('1.0', text)
        self.cargo_text.config(state='disabled')
        
    def search_cargo(self):
        """Busca carga por código"""
        code = self.code_entry.get().strip()
        
        if not code:
            messagebox.showwarning("Atenção", "Digite o código da carga.")
            return
            
        if not self.selected_warehouse_id:
            messagebox.showwarning("Atenção", "Selecione um galpão primeiro.")
            return
            
        try:
            self.show_cargo_info("🔍 Buscando carga...")
            self.root.update()
            
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.get(
                '/cargos/pending-physical-receipt',
                headers=headers,
                params={'code': code, 'per_page': 1}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    cargas = result['data']
                    if cargas:
                        self.current_cargo = cargas[0]
                        self.display_cargo_details(self.current_cargo)
                        self.enable_action_buttons()
                        log_info(f"Carga {code} encontrada")
                        return
                        
            self.show_cargo_info(f"❌ Carga '{code}' não encontrada ou já recebida.")
            self.current_cargo = None
            self.disable_action_buttons()
            
        except Exception as e:
            log_error(f"Erro ao buscar carga: {e}")
            messagebox.showerror("Erro", f"Erro ao buscar carga:\n{e}")
            self.disable_action_buttons()
            
    def display_cargo_details(self, cargo: Dict):
        """Exibe detalhes da carga"""
        details = []
        details.append("✅ CARGA ENCONTRADA\n")
        details.append("=" * 70)
        details.append(f"\n📦 Código: {cargo.get('code', 'N/A')}")
        details.append(f"🏷️ Código Cliente: {cargo.get('code_client', 'N/A')}")
        details.append(f"📄 NF: {cargo.get('invoice_number', 'N/A')}")
        details.append(f"📊 Status: {cargo.get('status', 'N/A')}")
        
        customer = cargo.get('customer', {})
        if customer:
            details.append(f"\n👤 Cliente: {customer.get('name', 'N/A')}")
            details.append(f"📋 Documento: {customer.get('document', 'N/A')}")
        
        cargo_type = cargo.get('cargo_type', {})
        if cargo_type:
            details.append(f"\n📦 Tipo: {cargo_type.get('name', 'N/A')}")
        
        details.append(f"\n⚖️ Peso: {cargo.get('weight', 'N/A')} kg")
        details.append(f"📐 Volume: {cargo.get('volume', 'N/A')} m³")
        details.append(f"📅 Recebido: {cargo.get('received_at', 'N/A')}")
        
        if cargo.get('description'):
            details.append(f"\n📝 Descrição: {cargo.get('description')}")
        
        details.append("\n" + "=" * 70)
        details.append("\n✅ Carga pronta para ação de recebimento")
        
        self.show_cargo_info("\n".join(details))
        
    def enable_action_buttons(self):
        """Habilita botões de ação"""
        self.accept_button.config(state='normal')
        self.accept_remarks_button.config(state='normal')
        self.reject_button.config(state='normal')
        
    def disable_action_buttons(self):
        """Desabilita botões de ação"""
        self.accept_button.config(state='disabled')
        self.accept_remarks_button.config(state='disabled')
        self.reject_button.config(state='disabled')
        
    def process_cargo(self, action: str):
        """Processa a carga com a ação especificada"""
        if not self.current_cargo:
            messagebox.showwarning("Atenção", "Nenhuma carga selecionada.")
            return
            
        if not self.selected_warehouse_id:
            messagebox.showwarning("Atenção", "Selecione um galpão.")
            return
            
        remarks = self.remarks_text.get('1.0', tk.END).strip()
        
        # Validações por tipo de ação
        if action == 'accept_with_remarks':
            if len(remarks) < 10:
                messagebox.showwarning("Atenção",
                    "Para aceitar com ressalvas, é necessário descrever as ressalvas (mínimo 10 caracteres).")
                return
        elif action == 'reject':
            if len(remarks) < 20:
                messagebox.showwarning("Atenção",
                    "Para rejeitar, é necessário descrever o motivo (mínimo 20 caracteres).")
                return
        
        # Confirmar ação
        action_labels = {
            'accept': '✅ ACEITAR',
            'accept_with_remarks': '⚠️ ACEITAR COM RESSALVAS',
            'reject': '❌ REJEITAR'
        }
        
        cargo_code = self.current_cargo.get('code', 'N/A')
        warehouse_name = self.warehouse_combo.get()
        area_name = self.area_combo.get() if self.selected_area_id else "Nenhuma"
        
        confirm_msg = (
            f"Confirma a ação:\n\n"
            f"Ação: {action_labels.get(action)}\n"
            f"Carga: {cargo_code}\n"
            f"Galpão: {warehouse_name}\n"
            f"Área: {area_name}\n"
        )
        
        if remarks:
            confirm_msg += f"\nObservações: {remarks[:50]}..."
            
        if not messagebox.askyesno("Confirmar Ação", confirm_msg):
            return
            
        # Preparar payload
        payload = {
            'warehouse_id': self.selected_warehouse_id,
            'action': action
        }
        
        if self.selected_area_id:
            payload['area_id'] = self.selected_area_id
            payload['area_type'] = 'RECEIVING'  # API espera em inglês
        
        if remarks and action in ['accept_with_remarks', 'reject']:
            payload['remarks'] = remarks
            
        # Enviar para API
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            cargo_id = self.current_cargo['id']
            
            # Log detalhado do payload
            log_info(f"Enviando para API - Cargo ID: {cargo_id}")
            log_info(f"Payload: {payload}")
            
            response = self.api_client.post(
                f'/cargos/{cargo_id}/receive-physically',
                data=payload,
                headers=headers
            )
            
            log_info(f"Resposta da API - Status: {response.status_code}")
            
            # Log da resposta completa em caso de erro
            if response.status_code != 200:
                try:
                    error_response = response.json()
                    log_error(f"Erro da API (HTTP {response.status_code}): {error_response}")
                except:
                    log_error(f"Erro da API (HTTP {response.status_code}): {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    log_info(f"Carga {cargo_code} processada: {action}")
                    
                    # Imprimir etiqueta automaticamente (exceto para rejeição)
                    if action != 'reject':
                        print_success = self.print_label_after_receive(cargo_code)
                        
                        # Mensagem de sucesso incluindo status da impressão
                        success_msg = self.format_success_message(result, action)
                        if print_success:
                            success_msg += "\n\n✅ Etiqueta impressa com sucesso!"
                        else:
                            success_msg += "\n\n⚠️ Erro ao imprimir etiqueta (verifique os logs)"
                        
                        messagebox.showinfo("Recebimento Concluído", success_msg)
                    else:
                        # Rejeição - apenas mostrar mensagem de sucesso
                        success_msg = self.format_success_message(result, action)
                        messagebox.showinfo("Recebimento Concluído", success_msg)
                    
                    # Limpar formulário
                    self.clear_form()
                else:
                    messagebox.showerror("Erro", result.get('message', 'Erro desconhecido'))
            else:
                # Erro HTTP - mostrar detalhes
                try:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get('message', f'Erro HTTP {response.status_code}')
                    
                    # Se houver erros de validação (422), mostrar detalhes
                    if response.status_code == 422 and 'errors' in error_data:
                        errors = error_data.get('errors', {})
                        error_details = []
                        for field, messages in errors.items():
                            if isinstance(messages, list):
                                error_details.append(f"• {field}: {', '.join(messages)}")
                            else:
                                error_details.append(f"• {field}: {messages}")
                        
                        if error_details:
                            error_msg += "\n\nErros de validação:\n" + "\n".join(error_details)
                    
                    # Se erro 500, adicionar orientação
                    if response.status_code == 500:
                        error_msg += "\n\n⚠️ Este é um erro interno do servidor."
                        error_msg += "\nContate o administrador do sistema."
                        
                        # Se for erro de SQL relacionado a movement_type
                        if 'movement_type' in error_msg.lower() and 'truncated' in error_msg.lower():
                            error_msg += "\n\n💡 Problema detectado: O campo 'movement_type' no banco de dados"
                            error_msg += "\nprecisa ser ajustado para aceitar valores maiores."
                    
                    messagebox.showerror("Erro na API", error_msg)
                except Exception as parse_error:
                    log_error(f"Erro ao parsear resposta: {parse_error}")
                    messagebox.showerror("Erro", f"Erro HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao processar carga: {e}")
            messagebox.showerror("Erro", f"Erro ao processar carga:\n{e}")
            
    def format_success_message(self, result: Dict, action: str) -> str:
        """Formata mensagem de sucesso"""
        data = result.get('data', {})
        
        # Log para debug - ver o que a API está retornando
        log_info(f"Dados retornados pela API: {data}")
        
        if action == 'reject':
            return (
                f"❌ Carga rejeitada com sucesso!\n\n"
                f"Código: {data.get('cargo_code', 'N/A')}\n"
                f"Status: {data.get('status', 'REJECTED')}\n"
                f"Rejeitada por: {data.get('rejected_by', 'N/A')}\n"
                f"Data/Hora: {data.get('rejected_at', 'N/A')}"
            )
        else:
            cargo = data.get('cargo', {})
            status_emoji = '⚠️' if action == 'accept_with_remarks' else '✅'
            
            # Pegar o status real retornado pela API (não forçar 'STORED')
            actual_status = cargo.get('status', 'N/A')
            log_info(f"Status da carga retornado pela API: {actual_status}")
            
            return (
                f"{status_emoji} Carga recebida com sucesso!\n\n"
                f"Código: {cargo.get('code', 'N/A')}\n"
                f"Status: {actual_status}\n"
                f"Localização: {cargo.get('current_address', 'N/A')}\n"
                f"Recebida por: {data.get('received_by', 'N/A')}\n"
                f"Data/Hora: {data.get('received_at', 'N/A')}"
            )
            
    def load_printers(self):
        """Carrega impressoras configuradas"""
        try:
            printers = self.printer_config_manager.list_printers()
            self.configured_printers = {}
            
            log_info(f"Tentando carregar impressoras: {len(printers) if printers else 0} encontradas")
            
            if printers:
                for printer in printers:
                    printer_id = printer.get('id')
                    printer_name = printer.get('name', 'Sem nome')
                    connection_type = printer.get('connection_type', 'unknown')
                    is_default = printer.get('is_default', False)
                    enabled = printer.get('enabled', False)
                    
                    # Só adicionar impressoras habilitadas
                    if not enabled:
                        log_info(f"Impressora {printer_name} está desabilitada, pulando")
                        continue
                    
                    # Formato de exibição
                    if is_default:
                        display_name = f"⭐ {printer_name} ({connection_type})"
                    else:
                        display_name = f"{printer_name} ({connection_type})"
                    
                    self.configured_printers[display_name] = printer_id
                    log_info(f"Impressora adicionada: {display_name}")
                
                # Adicionar opção "Salvar em Arquivo"
                self.configured_printers["💾 Salvar em Arquivo"] = "file"
                
                # Preencher combobox
                printer_options = list(self.configured_printers.keys())
                self.printer_combo['values'] = printer_options
                
                # Selecionar impressora padrão
                default_found = False
                for display_name in printer_options:
                    if display_name.startswith("⭐"):
                        self.printer_combo.set(display_name)
                        default_found = True
                        break
                
                if not default_found and printer_options:
                    self.printer_combo.current(0)
                    
                log_info(f"Carregadas {len(printers)} impressoras configuradas")
            else:
                self.configured_printers["💾 Salvar em Arquivo"] = "file"
                self.printer_combo['values'] = ["💾 Salvar em Arquivo"]
                self.printer_combo.current(0)
                log_info("Nenhuma impressora configurada, usando modo arquivo")
                
        except Exception as e:
            log_error(f"Erro ao carregar impressoras: {e}")
            self.configured_printers["💾 Salvar em Arquivo"] = "file"
            self.printer_combo['values'] = ["💾 Salvar em Arquivo"]
            self.printer_combo.current(0)
    
    def print_label_after_receive(self, cargo_code: str):
        """Imprime etiqueta após recebimento bem-sucedido"""
        try:
            # Validar quantidade
            qty_text = self.qty_entry.get().strip()
            if not qty_text.isdigit() or int(qty_text) <= 0:
                messagebox.showerror("Erro", "Digite uma quantidade válida para impressão (número inteiro > 0)")
                return False
            
            quantity = int(qty_text)
            
            # Gerar ZPL com dados da carga (para indicadores especiais)
            log_info(f"Gerando ZPL para código: {cargo_code}")
            
            # Preparar dados da carga para indicadores especiais
            cargo_data = None
            if self.current_cargo:
                cargo_data = {
                    'is_priority': self.current_cargo.get('is_priority', False),
                    'requires_special_handling': self.current_cargo.get('requires_special_handling', False),
                    'expiration_date': self.current_cargo.get('expiration_date'),
                    'handling_instructions': self.current_cargo.get('handling_instructions')
                }
                log_info(f"Indicadores especiais: priority={cargo_data['is_priority']}, "
                        f"special_handling={cargo_data['requires_special_handling']}, "
                        f"expiration={cargo_data['expiration_date']}")
            
            zpl = self.zpl_generator.build_zpl(cargo_code, cargo_data)
            
            # Múltiplas etiquetas
            if quantity > 1:
                all_zpl = zpl * quantity
            else:
                all_zpl = zpl
            
            # Obter impressora selecionada
            selected_display = self.printer_combo.get().strip()
            
            if not selected_display:
                messagebox.showwarning("Atenção", "Selecione uma impressora")
                return False
            
            printer_id = self.configured_printers.get(selected_display)
            
            if not printer_id:
                messagebox.showerror("Erro", f"Impressora não encontrada no mapeamento")
                return False
            
            # Configurar impressora
            if printer_id == "file":
                self.printer.config['output_mode'] = 'file'
            else:
                printer_config = self.printer_config_manager.get_printer(printer_id)
                if not printer_config:
                    messagebox.showerror("Erro", f"Configuração da impressora não encontrada")
                    return False
                
                self.printer.config['printer_id'] = printer_id
                self.printer.config['output_mode'] = 'configured'
            
            # Imprimir
            log_info(f"Enviando para impressão: {quantity} etiqueta(s) do código {cargo_code}")
            self.printer.send_print_job(all_zpl, quantity)
            
            log_info(f"Impressão concluída: {quantity} etiquetas do código {cargo_code}")
            return True
            
        except Exception as e:
            log_error(f"Erro na impressão: {e}")
            return False
    
    def clear_form(self):
        """Limpa formulário"""
        self.code_entry.delete(0, tk.END)
        self.remarks_text.delete('1.0', tk.END)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")
        self.current_cargo = None
        self.disable_action_buttons()
        self.show_cargo_info("Formulário limpo. Busque nova carga.")
        self.code_entry.focus()
