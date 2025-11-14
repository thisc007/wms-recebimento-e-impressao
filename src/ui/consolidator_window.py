#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tela de Consolidação e Impressão de Etiquetas (Consolidadores)

Funcionalidades:
- Listar consolidadores (com filtros: warehouse, status, search)
- Consultar detalhes de um consolidador
- Criar novo consolidador (inserir cargo ids)
- Adicionar cargas a um consolidador existente
- Imprimir etiqueta do consolidador (QR + campos independentes)

"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import APIClient
from printer.zpl_generator import ZplGenerator
from printer.label_printer import LabelPrinter
from utils.printer_config import PrinterConfigManager
from utils.logger import log_info, log_error


class ConsolidatorWindow:
    def __init__(self, cpf: str, token: str, user_data: Dict[str, Any], parent=None):
        self.cpf = cpf
        self.token = token
        self.user_data = user_data

        self.api_client = APIClient()
        self.api_client.token = token
        self.zpl_generator = ZplGenerator()
        self.printer = LabelPrinter()
        self.printer_config = PrinterConfigManager()

        self.consolidators = []
        self.selected_consolidator = None
        self.configured_printers = {}
        self.warehouses = []
        self.warehouse_dict = {}
        self.cargo_codes_cache = []  # Cache dos códigos digitados

        # Criar Toplevel passando o parent para evitar janela órfã
        self.root = tk.Toplevel(parent) if parent else tk.Toplevel()
        self.root.title("Consolidação de Cargas")
        self.root.geometry("750x700")
        self.root.resizable(False, False)

        # Carregar galpões antes de criar widgets para popular o select
        self.load_warehouses()
        self.create_widgets()
        self.load_printers()

    def create_widgets(self):
        """Cria interface simplificada para consolidação de cargas"""
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        # CABEÇALHO
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🔗 Consolidação de Cargas", 
                 font=("Arial", 14, "bold")).pack()
        ttk.Label(header_frame, 
                 text=f"{self.user_data.get('name', 'N/A')} | CPF: {self.cpf}",
                 font=("Arial", 9)).pack(pady=(2, 0))

        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=8)

        # SETUP: GALPÃO
        setup_frame = ttk.LabelFrame(frame, text="1. Configuração", padding=10)
        setup_frame.pack(fill=tk.X, pady=(0, 10))

        # Galpão
        ttk.Label(setup_frame, text="Galpão:*", font=('Arial', 9)).pack(anchor='w')
        self.warehouse_combo = ttk.Combobox(setup_frame, state='readonly', 
                                           font=('Arial', 10), width=50)
        if self.warehouses:
            self.warehouse_combo['values'] = list(self.warehouse_dict.keys())
            self.warehouse_combo.set('-- Selecione um galpão --')
        else:
            self.warehouse_combo['values'] = ['-- Nenhum galpão disponível --']
            self.warehouse_combo.set('-- Nenhum galpão disponível --')
            self.warehouse_combo.config(state='disabled')
        self.warehouse_combo.pack(fill=tk.X, pady=(2, 10))

        # Impressora
        ttk.Label(setup_frame, text="Impressora:*", font=('Arial', 9)).pack(anchor='w')
        self.printer_combo = ttk.Combobox(setup_frame, state='readonly', 
                                         font=('Arial', 10), width=50)
        self.printer_combo.pack(fill=tk.X, pady=(2, 10))

        # Quantidade de etiquetas
        qty_frame = ttk.Frame(setup_frame)
        qty_frame.pack(fill=tk.X)
        ttk.Label(qty_frame, text="Qtd Etiquetas:*", font=('Arial', 9)).pack(side=tk.LEFT)
        self.qty_entry = ttk.Entry(qty_frame, font=('Arial', 10), width=10)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side=tk.LEFT, padx=(8, 0))

        # ENTRADA DE CARGAS
        cargos_frame = ttk.LabelFrame(frame, text="2. Cargas (Cole ou Digite os Códigos)", padding=10)
        cargos_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(cargos_frame, 
                 text="Digite ou cole os códigos das cargas (um por linha ou separados por Enter):",
                 font=('Arial', 9)).pack(anchor='w', pady=(0, 4))

        # Text widget com scroll para entrada de códigos
        text_frame = ttk.Frame(cargos_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.cargos_text = tk.Text(text_frame, height=8, font=('Consolas', 10), 
                                   wrap=tk.WORD)
        self.cargos_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                              command=self.cargos_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.cargos_text.config(yscrollcommand=scroll.set)

        # INFO/RESULTADO
        result_frame = ttk.LabelFrame(frame, text="📋 Resultado", padding=8)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.result_text = tk.Text(result_frame, height=5, font=('Consolas', 9),
                                   wrap=tk.WORD, state='disabled')
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # BOTÕES DE AÇÃO
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X)

        ttk.Button(buttons_frame, text="✅ Consolidar e Imprimir",
                  command=self.consolidate_and_print,
                  width=25).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons_frame, text="� Limpar",
                  command=self.clear_form,
                  width=15).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons_frame, text="❌ Fechar",
                  command=self.root.destroy,
                  width=15).pack(side=tk.RIGHT)

    def load_printers(self):
        try:
            printers = self.printer_config.list_printers()
            self.configured_printers = {}
            options = []
            if printers:
                for p in printers:
                    if not p.get('enabled', False):
                        continue
                    display = ("⭐ " if p.get('is_default') else "") + f"{p.get('name')} ({p.get('connection_type')})"
                    options.append(display)
                    self.configured_printers[display] = p.get('id')
            # opção salvar em arquivo
            options.append("💾 Salvar em Arquivo")
            self.configured_printers["💾 Salvar em Arquivo"] = "file"
            self.printer_combo['values'] = options
            if options:
                self.printer_combo.current(0)
        except Exception as e:
            log_error(f"Erro ao carregar impressoras: {e}")
            self.printer_combo['values'] = ["💾 Salvar em Arquivo"]
            self.printer_combo.current(0)

    def load_warehouses(self):
        """Carrega lista de galpões para o select box"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            resp = self.api_client.get('/warehouses/select', headers=headers)
            if resp.status_code == 200:
                result = resp.json()
                if result.get('success') and result.get('data'):
                    self.warehouses = result.get('data', [])
                    self.warehouse_dict = {}
                    for w in self.warehouses:
                        name = w.get('name') or f"ID:{w.get('id')}"
                        self.warehouse_dict[name] = w.get('id')
                    log_info(f"Carregados {len(self.warehouses)} galpões para consolidação")
        except Exception as e:
            log_error(f"Erro ao carregar galpões (consolidator): {e}")

    def show_result(self, text: str, color: str = 'black'):
        """Exibe resultado na caixa de texto"""
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', text)
        self.result_text.tag_add("color", "1.0", tk.END)
        self.result_text.tag_config("color", foreground=color)
        self.result_text.config(state='disabled')

    def parse_cargo_codes(self) -> list:
        """Extrai códigos de carga do campo de texto (um por linha ou separados)"""
        text = self.cargos_text.get('1.0', tk.END).strip()
        if not text:
            return []
        
        # Separar por quebras de linha, vírgulas, ponto-e-vírgula ou espaços
        import re
        codes = re.split(r'[\n,;\s]+', text)
        # Filtrar vazios e limpar espaços
        codes = [c.strip() for c in codes if c.strip()]
        return codes

    def consolidate_and_print(self):
        """Consolida cargas e imprime etiquetas"""
        try:
            # Validar galpão
            wh_name = self.warehouse_combo.get().strip()
            if not wh_name or wh_name.startswith('--'):
                messagebox.showwarning("Atenção", "Selecione um galpão")
                return
            warehouse_id = self.warehouse_dict.get(wh_name)
            if not warehouse_id:
                messagebox.showerror("Erro", "Galpão inválido")
                return

            # Validar impressora
            printer_name = self.printer_combo.get().strip()
            if not printer_name:
                messagebox.showwarning("Atenção", "Selecione uma impressora")
                return
            printer_id = self.configured_printers.get(printer_name)
            if not printer_id:
                messagebox.showerror("Erro", "Impressora não encontrada")
                return

            # Validar quantidade
            qty_text = self.qty_entry.get().strip()
            if not qty_text.isdigit() or int(qty_text) <= 0:
                messagebox.showwarning("Atenção", "Quantidade inválida (mínimo 1)")
                return
            qty = int(qty_text)

            # Extrair códigos de carga
            cargo_codes = self.parse_cargo_codes()
            if not cargo_codes:
                messagebox.showwarning("Atenção", 
                    "Digite ou cole os códigos das cargas no campo de texto\n(um por linha ou separados por Enter)")
                return

            self.show_result(f"⏳ Processando {len(cargo_codes)} carga(s)...\n\nGalpão: {wh_name}\nImpressora: {printer_name}", "blue")
            self.root.update()

            # Buscar cargo_ids via API (usando códigos)
            # Cargas aptas para consolidação têm status: RECEIVED, CHECKED
            cargo_ids = []
            codes_not_found = []
            codes_wrong_status = []
            codes_with_errors = []  # Erros HTTP (500, etc.)
            
            headers = {'Authorization': f'Bearer {self.token}'}
            for code in cargo_codes:
                try:
                    # Tentar buscar por /cargos/code/{code} primeiro
                    resp = self.api_client.get(f'/cargos/code/{code}', headers=headers)
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        cargo = result.get('data')
                        
                        if cargo:
                            cargo_id = cargo.get('id')
                            cargo_status = cargo.get('status')
                            
                            # Verificar se status permite consolidação
                            consolidable_statuses = ['RECEIVED',  'CHECKED']
                            
                            log_info(f"Busca carga {code}: ID={cargo_id}, status={cargo_status}")
                            
                            if cargo_status in consolidable_statuses:
                                log_info(f"  ✓ Carga {code} apta para consolidação")
                                cargo_ids.append(cargo_id)
                            else:
                                log_info(f"  ✗ Carga {code} com status inválido: {cargo_status}")
                                codes_wrong_status.append({
                                    'code': code,
                                    'status': cargo_status
                                })
                        else:
                            log_info(f"  ✗ Carga {code} não encontrada (data vazio)")
                            codes_not_found.append(code)
                    elif resp.status_code == 404:
                        log_info(f"  ✗ Carga {code} não existe (404)")
                        codes_not_found.append(code)
                    else:
                        # Acumular erro HTTP
                        error_detail = f"HTTP {resp.status_code}"
                        try:
                            error_json = resp.json()
                            error_msg = error_json.get('message', resp.text[:100])
                            error_detail += f": {error_msg}"
                        except:
                            error_detail += f": {resp.text[:100]}"
                        
                        log_error(f"Erro ao buscar carga {code}: {error_detail}")
                        codes_with_errors.append({
                            'code': code,
                            'error': error_detail,
                            'full_response': resp.text[:500]
                        })
                except Exception as e:
                    log_error(f"Erro ao buscar carga {code}: {e}")
                    import traceback
                    log_error(f"Traceback: {traceback.format_exc()}")
                    codes_with_errors.append({
                        'code': code,
                        'error': f"Exceção: {str(e)}",
                        'full_response': traceback.format_exc()
                    })


            # Verificar se houve erros e acumular mensagem
            if codes_not_found or codes_wrong_status or codes_with_errors:
                error_summary = "⚠️ PROBLEMAS ENCONTRADOS ⚠️\n\n"
                error_summary += f"Total de cargas processadas: {len(cargo_codes)}\n"
                error_summary += f"Cargas válidas para consolidação: {len(cargo_ids)}\n\n"
                
                if codes_not_found:
                    error_summary += f"❌ {len(codes_not_found)} carga(s) NÃO ENCONTRADA(S):\n"
                    for c in codes_not_found[:10]:
                        error_summary += f"  • {c}\n"
                    if len(codes_not_found) > 10:
                        error_summary += f"  ... e mais {len(codes_not_found) - 10}\n"
                    error_summary += "\n"
                
                if codes_wrong_status:
                    error_summary += f"⚠️ {len(codes_wrong_status)} carga(s) com STATUS INVÁLIDO:\n"
                    for item in codes_wrong_status[:10]:
                        error_summary += f"  • {item['code']} → status: {item['status']}\n"
                    if len(codes_wrong_status) > 10:
                        error_summary += f"  ... e mais {len(codes_wrong_status) - 10}\n"
                    error_summary += "\n  Status válidos: RECEIVED, CHECKED\n\n"
                
                if codes_with_errors:
                    error_summary += f"🔥 {len(codes_with_errors)} carga(s) com ERRO NO SERVIDOR:\n"
                    for item in codes_with_errors[:5]:
                        error_summary += f"  • {item['code']}\n"
                        error_summary += f"    {item['error']}\n"
                    if len(codes_with_errors) > 5:
                        error_summary += f"  ... e mais {len(codes_with_errors) - 5}\n"
                    error_summary += "\n"
                    
                    # Log detalhado dos erros de servidor
                    log_error("=" * 60)
                    log_error("DETALHES COMPLETOS DOS ERROS DE SERVIDOR:")
                    for item in codes_with_errors:
                        log_error(f"\nCarga: {item['code']}")
                        log_error(f"Erro: {item['error']}")
                        log_error(f"Resposta completa:\n{item['full_response']}")
                        log_error("-" * 40)
                    log_error("=" * 60)
                
                # Exibir resumo na área de resultado
                self.show_result(error_summary, "orange")
                
                # Se não há cargas válidas, não continuar
                if not cargo_ids:
                    messagebox.showerror(
                        "Nenhuma Carga Válida",
                        "Não foi possível encontrar nenhuma carga válida para consolidação.\n\n"
                        "Verifique os erros acima e tente novamente."
                    )
                    return
                
                # Se há cargas válidas E erros, perguntar se quer continuar
                error_summary += "=" * 50 + "\n\n"
                error_summary += f"✅ {len(cargo_ids)} carga(s) podem ser consolidadas.\n\n"
                error_summary += "⚠️ ATENÇÃO: Esta ação NÃO PODERÁ SER DESFEITA!\n\n"
                error_summary += "Deseja continuar com a consolidação das cargas válidas?"
                
                # Perguntar ao usuário
                response = messagebox.askyesno(
                    "Continuar com Erros?",
                    error_summary,
                    icon='warning'
                )
                
                if not response:
                    self.show_result("❌ Consolidação cancelada pelo usuário.", "blue")
                    return

            if not cargo_ids:
                messagebox.showerror("Erro", "Nenhuma carga válida encontrada")
                return

            # Criar consolidador via API
            payload = {
                'warehouse_id': int(warehouse_id),
                'cargo_ids': cargo_ids
            }

            log_info(f"Criando consolidador: {len(cargo_ids)} cargas no galpão {warehouse_id}")
            
            resp = self.api_client.post('/consolidators', data=payload, headers=headers)

            if resp.status_code in (200, 201):
                result = resp.json()
                if result.get('success'):
                    consolidator = result.get('data', {})
                    consolidator_code = consolidator.get('code', 'N/A')
                    
                    # Verificar se há warnings (consolidação parcial)
                    warnings = result.get('warnings')
                    consolidated_count = result.get('consolidated_count', consolidator.get('cargo_count', len(cargo_ids)))
                    total_requested = result.get('total_requested', len(cargo_ids))
                    
                    success_msg = f"✅ Consolidador criado com sucesso!\n\n"
                    success_msg += f"Código: {consolidator_code}\n"
                    success_msg += f"Cargas consolidadas: {consolidated_count}\n"
                    
                    if warnings:
                        success_msg += f"⚠️ Cargas solicitadas: {total_requested}\n"
                        success_msg += f"⚠️ Cargas NÃO consolidadas: {total_requested - consolidated_count}\n\n"
                    
                    success_msg += f"Galpão: {wh_name}\n\n"
                    
                    # Mostrar warnings se houver
                    if warnings:
                        warning_msg = warnings.get('message', '')
                        skipped_cargos = warnings.get('skipped_cargos', [])
                        
                        if warning_msg:
                            success_msg += f"⚠️ {warning_msg}\n\n"
                        
                        if skipped_cargos:
                            success_msg += "Cargas não consolidadas:\n"
                            for skip in skipped_cargos[:5]:
                                cargo_code = skip.get('cargo_code', f"ID:{skip.get('cargo_id')}")
                                errors = skip.get('errors', [])
                                success_msg += f"  • {cargo_code}\n"
                                for err in errors:
                                    err_type = err.get('type', 'erro')
                                    err_msg = err.get('message', 'Erro desconhecido')
                                    success_msg += f"    → {err_type}: {err_msg[:80]}\n"
                            if len(skipped_cargos) > 5:
                                success_msg += f"  ... e mais {len(skipped_cargos) - 5}\n"
                            success_msg += "\n"
                    
                    success_msg += f"Imprimindo {qty} etiqueta(s)..."
                    
                    self.show_result(success_msg, "green" if not warnings else "orange")
                    self.root.update()

                    # Imprimir etiquetas
                    try:
                        self.print_consolidator_label(consolidator, printer_id, qty)
                        final_msg = success_msg.replace("Imprimindo", "✅ Impresso")
                        self.show_result(final_msg, "green" if not warnings else "orange")
                        
                        msg_title = "Sucesso com Avisos" if warnings else "Sucesso"
                        msg_text = f"Consolidador {consolidator_code} criado!\n\n"
                        msg_text += f"✅ {consolidated_count} carga(s) consolidada(s)\n"
                        if warnings:
                            msg_text += f"⚠️ {total_requested - consolidated_count} carga(s) não incluída(s)\n\n"
                        msg_text += f"✅ {qty} etiqueta(s) impressa(s)!"
                        
                        messagebox.showinfo(msg_title, msg_text)
                        
                        # Limpar formulário após sucesso
                        self.clear_form()
                        
                    except Exception as print_error:
                        log_error(f"Erro ao imprimir: {print_error}")
                        error_msg = success_msg + f"\n\n⚠️ Erro ao imprimir:\n{str(print_error)}"
                        self.show_result(error_msg, "orange")
                        messagebox.showwarning("Atenção", 
                            f"Consolidador criado, mas erro ao imprimir:\n{str(print_error)}")
                else:
                    messagebox.showerror("Erro", result.get('message', 'Erro desconhecido'))
            else:
                # Tratar erros da API (incluindo o formato especial de erros de consolidação)
                log_error(f"Erro ao criar consolidador - HTTP {resp.status_code}")
                log_error(f"Resposta completa: {resp.text}")
                
                try:
                    error_data = resp.json()
                    if not error_data.get('success', True):
                        error_msg = f"❌ {error_data.get('message', 'Erro ao consolidar')}\n\n"
                        
                        # Verificar se há erros detalhados (suporta 2 formatos)
                        # Formato 1: "errors" (antigo)
                        # Formato 2: "invalid_cargos" (novo)
                        errors_list = error_data.get('errors') or error_data.get('invalid_cargos', [])
                        
                        if errors_list and isinstance(errors_list, list):
                            error_msg += "Detalhes dos erros:\n\n"
                            for err in errors_list:
                                if isinstance(err, dict):
                                    cargo_code = err.get('cargo_code', 'N/A')
                                    
                                    # Formato antigo: erro direto no objeto
                                    if 'error' in err:
                                        error_type = err.get('error', 'desconhecido')
                                        message = err.get('message', 'Erro desconhecido')
                                        
                                        error_msg += f"📦 Carga: {cargo_code}\n"
                                        error_msg += f"   Tipo: {error_type}\n"
                                        error_msg += f"   {message}\n\n"
                                        
                                        # Informações extras se disponíveis
                                        if err.get('cargo_warehouse'):
                                            error_msg += f"   Galpão atual: {err.get('cargo_warehouse')}\n"
                                        if err.get('target_warehouse'):
                                            error_msg += f"   Galpão destino: {err.get('target_warehouse')}\n"
                                        error_msg += "\n"
                                    
                                    # Formato novo: array de errors dentro do objeto
                                    elif 'errors' in err:
                                        error_msg += f"📦 Carga: {cargo_code}\n"
                                        sub_errors = err.get('errors', [])
                                        for sub_err in sub_errors:
                                            if isinstance(sub_err, dict):
                                                err_type = sub_err.get('type', 'desconhecido')
                                                err_message = sub_err.get('message', 'Erro desconhecido')
                                                error_msg += f"   • {err_type}: {err_message}\n"
                                        error_msg += "\n"
                        
                        self.show_result(error_msg, "red")
                        messagebox.showerror("Erro na Consolidação", error_data.get('message', 'Erro'))
                    else:
                        # Erro sem formato esperado
                        messagebox.showerror(
                            f"Erro HTTP {resp.status_code}",
                            f"Resposta inesperada da API:\n\n{resp.text[:500]}"
                        )
                except Exception as parse_error:
                    log_error(f"Erro ao processar resposta da API: {parse_error}")
                    messagebox.showerror(
                        f"Erro HTTP {resp.status_code}",
                        f"Erro ao criar consolidador:\n\n{resp.text[:500]}"
                    )

        except Exception as e:
            log_error(f"Erro ao consolidar: {e}")
            self.show_result(f"❌ Erro:\n{str(e)}", "red")
            messagebox.showerror("Erro", f"Erro ao consolidar:\n{e}")

    def print_consolidator_label(self, consolidator: Dict[str, Any], printer_id: str, qty: int):
        """Imprime etiqueta do consolidador"""
        code = consolidator.get('code')
        consolidator_data = {
            'cargo_count': consolidator.get('cargo_count'),
            'total_weight': consolidator.get('total_weight'),
            'total_volume': consolidator.get('total_volume'),
            'warehouse_name': (consolidator.get('warehouse') or {}).get('name', ''),
            'status': consolidator.get('status'),
            'created_at': consolidator.get('created_at'),
        }

        zpl = self.zpl_generator.build_consolidator_zpl(code, consolidator_data)
        all_zpl = zpl * qty

        # Configurar impressora
        if printer_id == 'file':
            self.printer.config['output_mode'] = 'file'
        else:
            cfg = self.printer_config.get_printer(printer_id)
            if not cfg:
                raise ValueError("Configuração da impressora não encontrada")
            self.printer.config['printer_id'] = printer_id
            self.printer.config['output_mode'] = 'configured'

        self.printer.send_print_job(all_zpl, qty)

    def clear_form(self):
        """Limpa o formulário"""
        self.cargos_text.delete('1.0', tk.END)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")
        self.show_result("Pronto para nova consolidação.", "black")
        self.cargos_text.focus()


