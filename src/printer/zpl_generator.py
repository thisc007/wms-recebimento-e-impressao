#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerador de códigos ZPL para impressora Zebra GK400t
Baseado no código PHP original
"""

import json
import os
from typing import Dict, Any

class ZplGenerator:
    """Gerador de códigos ZPL para etiquetas"""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o gerador ZPL
        
        Args:
            config_path: Caminho para arquivo de configuração (opcional)
        """
        self.defaults = self._load_defaults(config_path)
        self.zpl_commands = []  # Manter compatibilidade com código existente
    
    def _load_defaults(self, config_path: str = None) -> Dict[str, Any]:
        """Carrega configurações padrão das etiquetas"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('label_defaults', self._get_builtin_defaults())
            except Exception:
                pass
        
        return self._get_builtin_defaults()
    
    def _get_builtin_defaults(self) -> Dict[str, Any]:
        """Retorna configurações padrão embutidas - corresponde ao config.php"""
        return {
            # Dimensões da etiqueta
            'width_mm': 90,
            'height_mm': 70,
            'dpi': 203,
            
            # Margens (dots)
            'margin_left': 32,   # ~4mm
            'margin_top': 240,   # 30mm
            
            # Ajustes finos
            'top_offset_dots': 0,
            'left_shift_dots': 0,
            
            # Configurações de código de barras
            'barcode_module_width': 3,
            'barcode_ratio': 2,
            'barcode_vertical_module_width': 2,
            'barcode_vertical_ratio': 2,
            'barcode_horizontal_module_width': 3,
            'barcode_horizontal_ratio': 2,
            'pad_length': 8,
            
            # Texto (número)
            'text': {
                'font': 'A',
                'height': 30,
                'width': 30,
                'x': 200,
                'y': 250
            },
            
            # Barcode horizontal
            'barcode_horizontal': {
                'orientation': 'N',
                'height': 90,
                'x': 220,
                'y': 430
            },
            
            # Barcode vertical
            'barcode_vertical': {
                'orientation': 'R',
                'height': 120,
                'x': 42,
                'y': 250
            }
        }
    
    def pad8(self, n: int) -> str:
        """Formata número com 8 dígitos com zeros à esquerda"""
        return str(n).zfill(8)
    
    def build_zpl(self, code: str, cargo_data: Dict[str, Any] = None) -> str:
        """
        Gera código ZPL para uma etiqueta
        
        Args:
            code: Código a ser impresso na etiqueta
            cargo_data: Dados opcionais da carga (priority, special_handling, expiration, etc)
            
        Returns:
            Código ZPL completo
        """
        # Configurações
        t = self.defaults['text']
        bh = self.defaults['barcode_horizontal']
        bv = self.defaults['barcode_vertical']
        
        dpi = int(self.defaults.get('dpi', 203))
        mm_to_dots = dpi / 25.4  # 1mm em dots
        
        width_dots = int(round((self.defaults.get('width_mm', 90)) * mm_to_dots))
        height_dots = int(round((self.defaults.get('height_mm', 70)) * mm_to_dots))
        
        lt = int(self.defaults.get('top_offset_dots', 0))
        ls = int(self.defaults.get('left_shift_dots', 0))
        
        # Largura do módulo e razão
        bw_global = int(self.defaults.get('barcode_module_width', 3))
        br_global = int(self.defaults.get('barcode_ratio', 2))
        
        bw_v = int(self.defaults.get('barcode_vertical_module_width', bw_global))
        br_v = int(self.defaults.get('barcode_vertical_ratio', br_global))
        
        bw_h = int(self.defaults.get('barcode_horizontal_module_width', bw_global))
        br_h = int(self.defaults.get('barcode_horizontal_ratio', br_global))
        
        font_cmd = f"^A{t['font']},{t['height']},{t['width']}"
        
        # Construir ZPL
        zpl = "^XA\n"
        zpl += "^CI28\n"  # UTF-8
        
        # Dimensões e alinhamento
        zpl += f"^PW{width_dots}\n"    # Largura de impressão
        zpl += f"^LL{height_dots}\n"   # Altura da etiqueta
        zpl += f"^LT{lt}\n"            # Offset superior
        zpl += "^LH0,0\n"              # Label Home no 0,0
        zpl += f"^LS{ls}\n"            # Deslocamento horizontal
        zpl += "^MNW\n"                # Media tracking por gap
        
        # Barcode 128 Vertical à esquerda
        zpl += f"^FO{bv['x']},{bv['y']}\n"
        zpl += f"^BY{bw_v},{br_v}\n"
        zpl += f"^BC{bv['orientation']},{bv['height']},N,N,N\n"
        zpl += f"^FD{code}^FS\n"
        
        # Texto (número)
        zpl += f"^FO{t['x']},{t['y']}\n"
        zpl += f"{font_cmd}\n"
        zpl += f"^FD{code}^FS\n"
        
        # Barcode 128 Horizontal
        zpl += f"^FO{bh['x']},{bh['y']}\n"
        zpl += f"^BY{bw_h},{br_h}\n"
        zpl += f"^BC{bh['orientation']},{bh['height']},N,N,N\n"
        zpl += f"^FD{code}^FS\n"
        
        # Adicionar indicadores especiais se cargo_data fornecido
        if cargo_data:
            zpl += self._add_special_indicators(cargo_data)
        
        zpl += "^XZ\n"
        
        return zpl
    
    def _add_special_indicators(self, cargo_data: Dict[str, Any]) -> str:
        """
        Adiciona indicadores visuais especiais na etiqueta
        
        Args:
            cargo_data: Dados da carga com flags especiais
            
        Returns:
            Código ZPL com indicadores
        """
        indicators_zpl = ""
        
        # ═══════════════════════════════════════════════════════════════════
        # ⚙️ CONFIGURAÇÃO INDEPENDENTE DE CADA INDICADOR
        # ═══════════════════════════════════════════════════════════════════
        # Ajuste as posições X, Y e tamanhos de fonte de cada indicador
        # Coordenadas em dots (203 DPI = 8 dots por mm)
        # Área da etiqueta: 719 x 559 dots (90mm x 70mm)
        
        # 🔴 INDICADOR DE PRIORIDADE (⚠️)
        priority_x = 560        # Posição horizontal (em dots)
        priority_y = 240        # Posição vertical (em dots)
        priority_font_h = 80    # Altura da fonte (em dots)
        priority_font_w = 80    # Largura da fonte (em dots)
        priority_text = "P"  # Texto do indicador
        
        # 🟠 INDICADOR DE MANUSEIO ESPECIAL (🔶)
        special_x = 610         # Posição horizontal (em dots)
        special_y = 240         # Posição vertical (em dots)
        special_font_h = 80     # Altura da fonte (em dots)
        special_font_w = 80     # Largura da fonte (em dots)
        special_text = "M"  # Texto do indicador
        
        # 🟡 INDICADOR DE DATA DE VALIDADE (📅)
        expiration_x = 210      # Posição horizontal (em dots)
        expiration_y = 300      # Posição vertical (em dots)
        expiration_font_h = 30  # Altura da fonte (em dots)
        expiration_font_w = 30  # Largura da fonte (em dots)
        
        # 🟢 INDICADOR DE INSTRUÇÕES (📋)
        instructions_x = 210    # Posição horizontal (em dots)
        instructions_y = 380    # Posição vertical (em dots)
        instructions_font_h = 25  # Altura da fonte (em dots)
        instructions_font_w = 25  # Largura da fonte (em dots)
        
        # ═══════════════════════════════════════════════════════════════════
        
        # ⚠️ CARGA PRIORITÁRIA
        if cargo_data.get('is_priority'):
            indicators_zpl += f"^FO{priority_x},{priority_y}\n"
            indicators_zpl += f"^A0N,{priority_font_h},{priority_font_w}\n"
            indicators_zpl += f"^FD{priority_text}^FS\n"
        
        # 🔶 MANUSEIO ESPECIAL
        if cargo_data.get('requires_special_handling'):
            indicators_zpl += f"^FO{special_x},{special_y}\n"
            indicators_zpl += f"^A0N,{special_font_h},{special_font_w}\n"
            indicators_zpl += f"^FD{special_text}^FS\n"
        
        # 📅 DATA DE VALIDADE
        expiration_date = cargo_data.get('expiration_date')
        if expiration_date:
            # Formatar data (assumindo formato ISO ou brasileiro)
            try:
                from datetime import datetime
                if 'T' in expiration_date:
                    # ISO format
                    dt = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%d/%m/%Y')
                else:
                    # Já está formatado
                    formatted_date = expiration_date[:10]
                
                indicators_zpl += f"^FO{expiration_x},{expiration_y}\n"
                indicators_zpl += f"^A0N,{expiration_font_h},{expiration_font_w}\n"
                indicators_zpl += f"^FDVal:{formatted_date}^FS\n"
            except:
                pass  # Se falhar, não adiciona
        
        # 📋 INSTRUÇÕES DE MANUSEIO (se houver)
        handling_instructions = cargo_data.get('handling_instructions')
        if handling_instructions and len(handling_instructions) > 0:
            # Truncar se muito longo
            instructions_short = handling_instructions[:30]
            if len(handling_instructions) > 30:
                instructions_short += "..."
            
            indicators_zpl += f"^FO{instructions_x},{instructions_y}\n"
            indicators_zpl += f"^A0N,{instructions_font_h},{instructions_font_w}\n"
            indicators_zpl += f"^FD{instructions_short}^FS\n"
        
        return indicators_zpl
    
    def build_batch_zpl(self, start_code: int, quantity: int) -> str:
        """
        Gera ZPL para múltiplas etiquetas sequenciais
        
        Args:
            start_code: Código inicial da sequência
            quantity: Quantidade de etiquetas
            
        Returns:
            Código ZPL para todas as etiquetas
        """
        all_zpl = ''
        for n in range(start_code, start_code + quantity):
            code = self.pad8(n)
            zpl = self.build_zpl(code)
            all_zpl += zpl
        
        return all_zpl

    def build_consolidator_zpl(self, consolidator_code: str, consolidator_data: Dict[str, Any] = None) -> str:
        """
        Gera ZPL específico para etiquetas de consolidadores usando QR Code

        Args:
            consolidator_code: Código do consolidador (ex: 900001)
            consolidator_data: Dict com valores opcionais: cargo_count, total_weight, total_volume,
                               warehouse_name, status, created_at, additional_text

        Returns:
            Código ZPL para etiqueta do consolidador
        """
        # valores padrão
        data = consolidator_data or {}
        cargo_count = data.get('cargo_count', '')
        total_weight = data.get('total_weight', '')
        total_volume = data.get('total_volume', '')
        warehouse_name = data.get('warehouse_name', '')
        status = data.get('status', '')
        created_at = data.get('created_at', '')
        additional_text = data.get('additional_text', '')

        # Posicionamento independente (ajuste conforme necessário)
        qr_x = 40
        qr_y = 300
        qr_model = '2'    # modelo 2
        qr_magnification = 10

        code_x = 280
        code_y = 310
        code_font_h = 60
        code_font_w = 60

        info1_x = 280
        info1_y = 380
        info1_h = 28
        info1_w = 28

        info2_x = 280
        info2_y = 415
        info2_h = 28
        info2_w = 28

        info3_x = 280
        info3_y = 450
        info3_h = 28
        info3_w = 28

        footer_x = 70
        footer_y = 250
        footer_h = 40
        footer_w = 40

        # Construir ZPL
        zpl = "^XA\n"
        zpl += "^CI28\n"  # UTF-8

        dpi = int(self.defaults.get('dpi', 203))
        mm_to_dots = dpi / 25.4
        width_dots = int(round((self.defaults.get('width_mm', 90)) * mm_to_dots))
        height_dots = int(round((self.defaults.get('height_mm', 70)) * mm_to_dots))

        zpl += f"^PW{width_dots}\n"
        zpl += f"^LL{height_dots}\n"
        zpl += "^LH0,0\n"

        # QR Code (ZPL1/2). Usamos BQN (modelo QR) com modo QA (alimentação do dado) - formato: ^BQN,2,5 then ^FDQA,data^FS
        # Aqui usamos magnification variável
        zpl += f"^FO{qr_x},{qr_y}\n"
        zpl += f"^BQN,2,{qr_magnification}\n"
        # prefix QA to indicate byte mode
        zpl += f"^FDQA,{consolidator_code}^FS\n"

        # Código do consolidador (texto grande)
        zpl += f"^FO{code_x},{code_y}\n"
        zpl += f"^A0N,{code_font_h},{code_font_w}\n"
        zpl += f"^FD{consolidator_code}^FS\n"

        # Informações - cargo_count / weight / volume
        if cargo_count != '':
            zpl += f"^FO{info1_x},{info1_y}\n"
            zpl += f"^A0N,{info1_h},{info1_w}\n"
            zpl += f"^FDCargas: {cargo_count}^FS\n"

        if total_weight not in (None, ''):
            zpl += f"^FO{info2_x},{info2_y}\n"
            zpl += f"^A0N,{info2_h},{info2_w}\n"
            zpl += f"^FDPeso: {total_weight} kg^FS\n"

        if total_volume not in (None, ''):
            zpl += f"^FO{info3_x},{info3_y}\n"
            zpl += f"^A0N,{info3_h},{info3_w}\n"
            zpl += f"^FDVol: {total_volume} m3^FS\n"

        # Warehouse / Status
        footer_texts = []
        if warehouse_name:
            footer_texts.append(f"Galpão: {warehouse_name}")
        

        if footer_texts or additional_text:
            y = footer_y
            for t in footer_texts:
                zpl += f"^FO{footer_x},{y}\n"
                zpl += f"^A0N,{footer_h},{footer_w}\n"
                zpl += f"^FD{t}^FS\n"
                y += 24

            if additional_text:
                zpl += f"^FO{footer_x},{y}\n"
                zpl += f"^A0N,{footer_h},{footer_w}\n"
                zpl += f"^FD{additional_text}^FS\n"

        zpl += "^XZ\n"
        return zpl

    # Métodos da classe original (manter compatibilidade)
    def add_text(self, x, y, text, font='0', rotation='0', width='1', height='1'):
        command = f'^FO{x},{y}^A{font},{height},{width}^FD{text}^FS'
        self.zpl_commands.append(command)

    def add_barcode(self, x, y, barcode_type, data, height='50', width='2'):
        command = f'^FO{x},{y}^BY{width}^B{barcode_type},{height},Y,N^FD{data}^FS'
        self.zpl_commands.append(command)

    def add_graphic(self, x, y, graphic_data):
        command = f'^FO{x},{y}^GFA,{len(graphic_data)},{len(graphic_data) // 2},{len(graphic_data) // 8},{graphic_data}^FS'
        self.zpl_commands.append(command)

    def generate_zpl(self):
        return '\n'.join(self.zpl_commands)

    def clear_commands(self):
        self.zpl_commands = []