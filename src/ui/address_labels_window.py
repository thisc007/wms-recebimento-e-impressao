#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Janela de impressão de etiquetas de endereçamento
Permite selecionar galpão, impressora e imprimir etiquetas por andar ou individuais
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from typing import Dict, List, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from address_manager import AddressManager
from printer.zpl_generator import ZplGenerator
from printer.label_printer import LabelPrinter
from utils.logger import log_info, log_error
from utils.config import load_config
from utils.printer_config import printer_config

class AddressLabelsWindow:
    """Janela para impressão de etiquetas de endereçamento"""
    
    def __init__(self, parent, api_client, user_session):
        """
        Inicializa a janela de endereçamento
        
        Args:
            parent: Janela pai (Tkinter)
            api_client: Cliente da API
            user_session: Sessão do usuário
        """
        self.parent = parent
        self.api_client = api_client
        self.user_session = user_session
        self.config = load_config()
        
        # Managers
        self.address_manager = AddressManager()
        self.zpl_generator = ZplGenerator()
        # Não criar LabelPrinter aqui - será criado quando necessário
        
        # Criar janela PRIMEIRO (antes de criar qualquer variável Tkinter)
        self.window = tk.Toplevel(parent)
        self.window.title("Impressão de Etiquetas de Endereçamento")
        self.window.geometry("1200x800")
        
        # Dados
        self.warehouses = []
        self.printers = []
        self.printer_ids = {}  # Mapear nome -> ID da impressora
        self.current_warehouse_id = None
        self.organized_data = []  # Dados organizados por andar
        self.organized_blocks = []  # Dados organizados por bloco (posição vertical)
        self.print_mode = 'block'  # Modo de impressão: 'floor' ou 'block'
        
        self._create_widgets()
        self._load_initial_data()
    
    def _create_widgets(self):
        """Cria os widgets da interface"""
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # ===== Seção de Seleção =====
        selection_frame = ttk.LabelFrame(main_frame, text="Configuração", padding="10")
        selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Galpão
        ttk.Label(selection_frame, text="Galpão:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.warehouse_var = tk.StringVar(self.window)
        self.warehouse_combo = ttk.Combobox(selection_frame, textvariable=self.warehouse_var, 
                                            state='readonly', width=40)
        self.warehouse_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.warehouse_combo.bind('<<ComboboxSelected>>', self._on_warehouse_selected)
        
        # Impressora
        ttk.Label(selection_frame, text="Impressora:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.printer_var = tk.StringVar(self.window)
        self.printer_combo = ttk.Combobox(selection_frame, textvariable=self.printer_var, 
                                          state='readonly', width=30)
        self.printer_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        selection_frame.columnconfigure(1, weight=1)
        selection_frame.columnconfigure(3, weight=1)
        
        # ===== Modo de Impressão =====
        mode_frame = ttk.LabelFrame(main_frame, text="Modo de Impressão", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.mode_var = tk.StringVar(self.window, value='block')
        
        ttk.Radiobutton(mode_frame, text="🏢 Por Bloco", 
                       variable=self.mode_var, value='block',
                       command=self._on_mode_changed).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(mode_frame, text="📊 Por Andar", 
                       variable=self.mode_var, value='floor',
                       command=self._on_mode_changed).pack(side=tk.LEFT)
        
        ttk.Label(mode_frame, text="Bloco: mesma posição de todos os andares | Andar: todas as posições de um andar (até 8 QR codes)", 
                 foreground='gray', font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(20, 0))
        
        # ===== Botão Imprimir Tudo =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.print_all_button = ttk.Button(button_frame, text="🖨 Imprimir Todas as Etiquetas", 
                                          command=self._print_all, style='Accent.TButton')
        self.print_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.mode_description_label = ttk.Label(button_frame, text="", foreground='gray')
        self.mode_description_label.pack(side=tk.LEFT)
        self._update_mode_description()
        
        # ===== Lista de Endereços =====
        list_frame = ttk.LabelFrame(main_frame, text="Endereços do Galpão", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Criar frame com canvas e scrollbar para os botões
        canvas_frame = ttk.Frame(list_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar
        self.canvas = tk.Canvas(canvas_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # ===== Status =====
        self.status_label = ttk.Label(main_frame, text="Selecione um galpão para começar", 
                                     foreground='blue')
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def _on_mousewheel(self, event):
        """Handler para scroll com mouse wheel"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_mode_changed(self):
        """Callback quando o modo de impressão é alterado"""
        self._update_mode_description()
    
    def _update_mode_description(self):
        """Atualiza a descrição do modo de impressão"""
        mode = self.mode_var.get()
        if mode == 'block':
            self.mode_description_label.config(
                text="Imprime mesma posição de todos os andares (do mais alto ao mais baixo) - até 8 QR codes"
            )
        else:
            self.mode_description_label.config(
                text="Imprime uma etiqueta por andar com até 8 QR codes"
            )
    
    def _load_initial_data(self):
        """Carrega dados iniciais (galpões e impressoras)"""
        self._load_warehouses()
        self._load_printers()
    
    def _load_warehouses(self):
        """Carrega lista de galpões da API"""
        try:
            self.status_label.config(text="Carregando galpões...", foreground='blue')
            self.window.update()
            
            # Buscar galpões da API com autenticação
            headers = {'Authorization': f'Bearer {self.user_session.token}'}
            response = self.api_client.get('/warehouses/select', headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    warehouses_data = result.get('data', [])
                    self.warehouses = warehouses_data
                    
                    # Preencher combobox
                    warehouse_list = [f"{w['code']} - {w['name']}" for w in warehouses_data]
                    self.warehouse_combo['values'] = warehouse_list
                    
                    if warehouse_list:
                        self.warehouse_combo.current(0)
                        self.status_label.config(text=f"{len(warehouse_list)} galpão(ões) carregado(s)", 
                                               foreground='green')
                    else:
                        self.status_label.config(text="Nenhum galpão encontrado", foreground='orange')
                else:
                    self.status_label.config(text="Erro ao carregar galpões", foreground='red')
                    messagebox.showerror("Erro", "Não foi possível carregar a lista de galpões")
            else:
                self.status_label.config(text=f"Erro HTTP {response.status_code}", foreground='red')
                messagebox.showerror("Erro", f"Erro ao carregar galpões: HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao carregar galpões: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro ao carregar galpões:\n{str(e)}")
    
    def _load_printers(self):
        """Carrega lista de impressoras disponíveis"""
        try:
            printers_list = printer_config.list_printers()
            
            if printers_list:
                # Extrair nomes e IDs das impressoras
                self.printers = []
                self.printer_ids = {}
                
                for p in printers_list:
                    name = p.get('name', f"Impressora {p.get('id')}")
                    printer_id = p.get('id')
                    self.printers.append(name)
                    self.printer_ids[name] = printer_id
                
                self.printer_combo['values'] = self.printers
                
                # Tentar selecionar impressora padrão
                for idx, p in enumerate(printers_list):
                    if p.get('is_default', False):
                        self.printer_combo.current(idx)
                        break
                else:
                    # Se não tem padrão, selecionar primeira
                    self.printer_combo.current(0)
            else:
                messagebox.showwarning("Aviso", "Nenhuma impressora encontrada no sistema")
                
        except Exception as e:
            log_error(f"Erro ao carregar impressoras: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar impressoras:\n{str(e)}")
    
    def _on_warehouse_selected(self, event=None):
        """Callback quando um galpão é selecionado"""
        selected_index = self.warehouse_combo.current()
        if selected_index < 0:
            return
            
        selected_warehouse = self.warehouses[selected_index]
        self.current_warehouse_id = selected_warehouse['id']
        
        self.status_label.config(text=f"Carregando estrutura do galpão {selected_warehouse['code']}...", 
                               foreground='blue')
        self.window.update()
        
        self._load_warehouse_structure(self.current_warehouse_id)
    
    def _load_warehouse_structure(self, warehouse_id: int):
        """
        Carrega estrutura completa do galpão (prédios, andares, paletes)
        
        Args:
            warehouse_id: ID do galpão
        """
        try:
            # Buscar estrutura completa da API com autenticação
            headers = {'Authorization': f'Bearer {self.user_session.token}'}
            response = self.api_client.get(f'/warehouses/{warehouse_id}', headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Carregar no AddressManager
                    if self.address_manager.load_warehouse_data(result):
                        # Organizar dados por andar E por bloco
                        self.organized_data = self.address_manager.organize_addresses_by_floor()
                        self.organized_blocks = self.address_manager.organize_addresses_by_block()
                        
                        # Exibir endereços
                        self._display_addresses()
                        
                        total_pallets = sum(len(floor['pallets']) for floor in self.organized_data)
                        self.status_label.config(
                            text=f"Galpão carregado: {len(self.organized_data)} andar(es), {len(self.organized_blocks)} bloco(s), {total_pallets} palete(s)", 
                            foreground='green'
                        )
                    else:
                        self.status_label.config(text="Erro ao processar dados do galpão", foreground='red')
                else:
                    self.status_label.config(text="Erro ao carregar estrutura do galpão", foreground='red')
                    messagebox.showerror("Erro", "Não foi possível carregar a estrutura do galpão")
            else:
                self.status_label.config(text=f"Erro HTTP {response.status_code}", foreground='red')
                messagebox.showerror("Erro", f"Erro ao carregar estrutura: HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao carregar estrutura: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro ao carregar estrutura:\n{str(e)}")
    
    def _display_addresses(self):
        """Exibe os endereços organizados por andar com botões"""
        
        # Limpar frame anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.organized_data:
            ttk.Label(self.scrollable_frame, text="Nenhum endereço encontrado", 
                     foreground='gray').pack(pady=20)
            return
        
        # Organizar por prédio e andar
        for floor_data in self.organized_data:
            # Frame para cada andar
            floor_frame = ttk.LabelFrame(
                self.scrollable_frame, 
                text=f"{floor_data['building_name']} - {floor_data['floor_name']} ({len(floor_data['pallets'])} paletes)",
                padding="10"
            )
            floor_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Botão para imprimir andar completo (MODELO 01)
            floor_btn = ttk.Button(
                floor_frame,
                text=f"🖨 Imprimir Andar Completo ({floor_data['floor_name']})",
                command=lambda fd=floor_data: self._print_floor(fd)
            )
            floor_btn.pack(fill=tk.X, pady=(0, 10))
            
            # Grid de botões para paletes individuais (MODELO 02)
            pallets_frame = ttk.Frame(floor_frame)
            pallets_frame.pack(fill=tk.X)
            
            # Criar botões em grid (3 colunas)
            for idx, pallet in enumerate(floor_data['pallets']):
                row = idx // 3
                col = idx % 3
                
                pallet_btn = ttk.Button(
                    pallets_frame,
                    text=f"{pallet['full_address']}\n{pallet['name']}",
                    command=lambda fd=floor_data, p=pallet: self._print_single_pallet(fd, p),
                    width=30
                )
                pallet_btn.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # Configurar colunas para expandir
            for col in range(3):
                pallets_frame.columnconfigure(col, weight=1)
    
    def _print_zpl(self, zpl: str, printer_name: str) -> bool:
        """
        Helper para imprimir ZPL usando a impressora selecionada
        
        Args:
            zpl: Código ZPL para imprimir
            printer_name: Nome da impressora
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Obter ID da impressora
            printer_id = self.printer_ids.get(printer_name)
            if not printer_id:
                log_error(f"Impressora não encontrada: {printer_name}")
                return False
            
            # Criar LabelPrinter com a impressora selecionada
            printer = LabelPrinter(printer_id=printer_id)
            
            # Enviar job de impressão
            return printer.send_print_job(zpl, quantity=1)
            
        except Exception as e:
            log_error(f"Erro ao imprimir: {str(e)}")
            return False
    
    def _print_all(self):
        """Imprime todas as etiquetas de acordo com o modo selecionado"""
        mode = self.mode_var.get()
        
        if mode == 'block':
            self._print_all_blocks()
        else:
            self._print_all_floors()
    
    def _print_all_blocks(self):
        """Imprime etiquetas de todos os blocos (MODELO 03) - Por posição vertical"""
        if not self._validate_selection():
            return
        
        if not self.organized_blocks:
            messagebox.showwarning("Aviso", "Nenhum bloco para imprimir")
            return
        
        # Confirmar impressão
        total_blocks = len(self.organized_blocks)
        total_labels = sum((len(block['addresses']) + 7) // 8 for block in self.organized_blocks)
        
        if not messagebox.askyesno("Confirmar Impressão", 
                                   f"Deseja imprimir {total_labels} etiqueta(s) para {total_blocks} posição(ões) vertical(is)?"):
            return
        
        try:
            printer_name = self.printer_var.get()
            success_count = 0
            error_count = 0
            
            self.status_label.config(text="Imprimindo etiquetas de blocos...", foreground='blue')
            self.window.update()
            
            for block_data in self.organized_blocks:
                # Dividir endereços em grupos de 8 (máximo por etiqueta)
                addresses = block_data['addresses']
                groups = []
                for i in range(0, len(addresses), 8):
                    groups.append(addresses[i:i+8])
                
                # Imprimir cada grupo
                for group in groups:
                    try:
                        zpl = self.zpl_generator.build_block_addresses_zpl(
                            warehouse_code=block_data['warehouse_code'],
                            warehouse_name=block_data['warehouse_name'],
                            building_name=block_data['building_name'],
                            addresses_by_position=group
                        )
                        
                        if self._print_zpl(zpl, printer_name):
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        log_error(f"Erro ao imprimir bloco {block_data['position_group']}: {str(e)}")
                        error_count += 1
            
            # Mensagem final
            if error_count == 0:
                self.status_label.config(
                    text=f"✓ {success_count} etiqueta(s) de bloco impressa(s) com sucesso!", 
                    foreground='green'
                )
                messagebox.showinfo("Sucesso", 
                                   f"{success_count} etiqueta(s) impressa(s) com sucesso!")
            else:
                self.status_label.config(
                    text=f"⚠ {success_count} ok, {error_count} erro(s)", 
                    foreground='orange'
                )
                messagebox.showwarning("Aviso", 
                                      f"Impressão concluída com erros:\n"
                                      f"Sucesso: {success_count}\nErros: {error_count}")
                
        except Exception as e:
            log_error(f"Erro na impressão em lote de blocos: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro na impressão:\n{str(e)}")
    
    def _print_all_floors(self):
        """Imprime etiquetas de todos os andares (MODELO 01)"""
        if not self._validate_selection():
            return
        
        if not self.organized_data:
            messagebox.showwarning("Aviso", "Nenhum andar para imprimir")
            return
        
        # Confirmar impressão
        total_floors = len(self.organized_data)
        total_labels = sum((len(floor['pallets']) + 7) // 8 for floor in self.organized_data)
        
        if not messagebox.askyesno("Confirmar Impressão", 
                                   f"Deseja imprimir {total_labels} etiqueta(s) para {total_floors} andar(es)?"):
            return
        
        try:
            printer_name = self.printer_var.get()
            success_count = 0
            error_count = 0
            
            self.status_label.config(text="Imprimindo etiquetas de andares...", foreground='blue')
            self.window.update()
            
            for floor_data in self.organized_data:
                if self._print_floor(floor_data, show_messages=False):
                    success_count += 1
                else:
                    error_count += 1
            
            # Mensagem final
            if error_count == 0:
                self.status_label.config(
                    text=f"✓ {success_count} andar(es) impresso(s) com sucesso!", 
                    foreground='green'
                )
                messagebox.showinfo("Sucesso", 
                                   f"{success_count} andar(es) impresso(s) com sucesso!")
            else:
                self.status_label.config(
                    text=f"⚠ {success_count} ok, {error_count} erro(s)", 
                    foreground='orange'
                )
                messagebox.showwarning("Aviso", 
                                      f"Impressão concluída com erros:\n"
                                      f"Sucesso: {success_count}\nErros: {error_count}")
                
        except Exception as e:
            log_error(f"Erro na impressão em lote: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro na impressão:\n{str(e)}")
    
    def _print_floor(self, floor_data: Dict[str, Any], show_messages: bool = True) -> bool:
        """
        Imprime etiquetas de um andar completo (MODELO 01)
        
        Args:
            floor_data: Dados do andar
            show_messages: Se deve mostrar mensagens de sucesso/erro
            
        Returns:
            True se sucesso, False se erro
        """
        if not self._validate_selection():
            return False
        
        try:
            printer_name = self.printer_var.get()
            pallets = floor_data['pallets']
            
            # Dividir em grupos de 8
            groups = []
            for i in range(0, len(pallets), 8):
                groups.append(pallets[i:i+8])
            
            # Gerar e imprimir ZPL para cada grupo
            for group in groups:
                # Preparar dados para o gerador
                addresses = [{'full_address': p['full_address'], 'name': p['name']} for p in group]
                
                zpl = self.zpl_generator.build_floor_addresses_zpl(
                    warehouse_code=floor_data['warehouse_code'],
                    warehouse_name=floor_data['warehouse_name'],
                    building_name=floor_data['building_name'],
                    floor_name=floor_data['floor_name'],
                    addresses=addresses
                )
                
                # Imprimir
                if not self._print_zpl(zpl, printer_name):
                    if show_messages:
                        messagebox.showerror("Erro", f"Erro ao imprimir andar {floor_data['floor_name']}")
                    return False
            
            if show_messages:
                messagebox.showinfo("Sucesso", 
                                   f"Etiqueta(s) do andar {floor_data['floor_name']} impressa(s) com sucesso!")
            
            return True
            
        except Exception as e:
            log_error(f"Erro ao imprimir andar: {str(e)}")
            if show_messages:
                messagebox.showerror("Erro", f"Erro ao imprimir andar:\n{str(e)}")
            return False
    
    def _print_single_pallet(self, floor_data: Dict[str, Any], pallet: Dict[str, Any]):
        """
        Imprime etiqueta de um palete individual (MODELO 02)
        
        Args:
            floor_data: Dados do andar
            pallet: Dados do palete
        """
        if not self._validate_selection():
            return
        
        try:
            printer_name = self.printer_var.get()
            
            # Gerar ZPL
            zpl = self.zpl_generator.build_single_address_zpl(
                full_address=pallet['full_address'],
                pallet_name=pallet['name'],
                building_name=floor_data['building_name'],
                floor_name=floor_data['floor_name']
            )
            
            # Imprimir
            if self._print_zpl(zpl, printer_name):
                self.status_label.config(
                    text=f"✓ Etiqueta {pallet['full_address']} impressa com sucesso!", 
                    foreground='green'
                )
            else:
                self.status_label.config(
                    text=f"✗ Erro ao imprimir {pallet['full_address']}", 
                    foreground='red'
                )
                messagebox.showerror("Erro", f"Erro ao imprimir etiqueta {pallet['full_address']}")
                
        except Exception as e:
            log_error(f"Erro ao imprimir palete: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}", foreground='red')
            messagebox.showerror("Erro", f"Erro ao imprimir etiqueta:\n{str(e)}")
    
    def _validate_selection(self) -> bool:
        """
        Valida se galpão e impressora foram selecionados
        
        Returns:
            True se válido, False caso contrário
        """
        if not self.warehouse_var.get():
            messagebox.showwarning("Aviso", "Selecione um galpão")
            return False
            
        if not self.printer_var.get():
            messagebox.showwarning("Aviso", "Selecione uma impressora")
            return False
            
        return True
