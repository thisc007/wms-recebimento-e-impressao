#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para impressão de etiquetas em diferentes modos
Integrado com sistema de configuração de impressoras Zebra GK420t
"""

import socket
import os
import tempfile
import subprocess
from datetime import datetime
from typing import Optional
from utils.logger import log_info, log_error, log_warning
from utils.printer_config import printer_config

class LabelPrinter:
    """Classe para impressão de etiquetas ZPL com suporte a impressoras configuradas"""
    
    def __init__(self, printer_id: str = None, config: dict = None):
        """
        Inicializa o printer
        
        Args:
            printer_id: ID da impressora configurada (ou None para usar padrão)
            config: Configurações de impressão (opcional, sobrescreve configurações salvas)
        """
        self.printer_id = printer_id
        
        # Inicializar config primeiro para compatibilidade
        self.config = {}
        
        # Carregar configuração da impressora
        if printer_id:
            self.printer_config = printer_config.get_printer(printer_id)
            if not self.printer_config:
                log_error(f"Impressora {printer_id} não encontrada, usando padrão")
                self.printer_config = printer_config.get_default_printer()
        else:
            self.printer_config = printer_config.get_default_printer()
        
        # Se ainda não tem configuração, usar fallback
        if not self.printer_config:
            log_error("Nenhuma impressora configurada, usando configuração de fallback")
            self.printer_config = self._get_fallback_config()
        
        # Sobrescrever com config fornecida se existir
        if config:
            self.legacy_config = config
        else:
            self.legacy_config = self._convert_to_legacy_config()
        
        # Alias para compatibilidade com código existente
        self.config = self.legacy_config
        
        log_info(f"LabelPrinter inicializada: {self.printer_config.get('name', 'Desconhecida')}")
    
    def _get_fallback_config(self) -> dict:
        """Retorna configuração de fallback quando não há impressoras configuradas"""
        return {
            "id": "fallback",
            "name": "Fallback Printer",
            "type": "usb",
            "enabled": True,
            "connection": {
                "mode": "usb",
                "device_name": "ZDesigner GK420t",
                "port": None
            },
            "settings": {
                "print_speed": "2",
                "darkness": "8",
                "print_width": "104mm",
                "label_width": "100mm",
                "label_height": "50mm",
                "dpi": "203"
            }
        }
    
    def _convert_to_legacy_config(self) -> dict:
        """Converte configuração nova para formato legado"""
        connection = self.printer_config.get('connection', {})
        mode = connection.get('mode', 'usb')
        
        if mode == 'network':
            output_mode = 'printer'
            host = connection.get('ip_address', '127.0.0.1')
            port = connection.get('port', 9100)
            timeout = connection.get('timeout', 10)
        elif mode == 'usb':
            output_mode = 'windows_printer'
            host = '127.0.0.1'
            port = 9100
            timeout = 10
        else:
            output_mode = 'file'
            host = '127.0.0.1'
            port = 9100
            timeout = 10
        
        return {
            'output_mode': output_mode,
            'printer_host': host,
            'printer_port': port,
            'windows_printer_share': connection.get('device_name'),
            'output_dir': './out',
            'timeout': timeout
        }
    
    def set_printer(self, printer_id: str) -> bool:
        """
        Altera impressora ativa
        
        Args:
            printer_id: ID da nova impressora
            
        Returns:
            True se alterou com sucesso
        """
        new_config = printer_config.get_printer(printer_id)
        if new_config:
            self.printer_id = printer_id
            self.printer_config = new_config
            self.legacy_config = self._convert_to_legacy_config()
            log_info(f"Impressora alterada para: {new_config.get('name')}")
            return True
        else:
            log_error(f"Impressora {printer_id} não encontrada")
            return False
    
    def get_printer_info(self) -> dict:
        """
        Retorna informações da impressora atual
        
        Returns:
            Dicionário com informações da impressora
        """
        return {
            "id": self.printer_config.get('id'),
            "name": self.printer_config.get('name'),
            "type": self.printer_config.get('type'),
            "enabled": self.printer_config.get('enabled'),
            "connection": self.printer_config.get('connection'),
            "settings": self.printer_config.get('settings')
        }
    
    def is_printer_available(self) -> bool:
        """
        Verifica se a impressora está disponível
        
        Returns:
            True se disponível
        """
        if not self.printer_config.get('enabled', False):
            log_warning("Impressora está desabilitada")
            return False
        
        return printer_config.test_connection(self.printer_id or 'fallback')
    
    def send_to_socket_printer(self, host: str, port: int, data: str) -> bool:
        """
        Envia ZPL para impressora via socket TCP
        
        Args:
            host: IP da impressora
            port: Porta da impressora (normalmente 9100)
            data: Dados ZPL para imprimir
            
        Returns:
            True se enviado com sucesso
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.legacy_config.get('timeout', 10))
                sock.connect((host, port))
                sock.sendall(data.encode('utf-8'))
                log_info(f"ZPL enviado para impressora {host}:{port}")
                return True
                
        except socket.timeout:
            log_error(f"Timeout ao conectar na impressora {host}:{port}")
            raise RuntimeError(f"Timeout ao conectar na impressora {host}:{port}")
        except ConnectionRefusedError:
            log_error(f"Conexão recusada pela impressora {host}:{port}")
            raise RuntimeError(f"Não foi possível conectar na impressora {host}:{port}")
        except Exception as e:
            log_error(f"Erro ao enviar para impressora {host}:{port}: {str(e)}")
            raise RuntimeError(f"Erro ao enviar para impressora: {str(e)}")
    
    def send_to_windows_printer(self, printer_share: str, data: str) -> bool:
        """
        Envia ZPL para impressora Windows compartilhada
        
        Args:
            printer_share: Caminho da impressora compartilhada (ex: \\\\localhost\\Zebra)
            data: Dados ZPL para imprimir
            
        Returns:
            True se enviado com sucesso
        """
        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.zpl', delete=False) as tmp_file:
                tmp_file.write(data)
                tmp_path = tmp_file.name
            
            # Usar comando copy /b para enviar para fila de impressão
            cmd = ['cmd', '/c', 'copy', '/b', f'"{tmp_path}"', f'"{printer_share}"']
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            # Limpar arquivo temporário
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            if result.returncode != 0:
                log_error(f"Erro ao enviar para impressora Windows: {result.stderr}")
                raise RuntimeError(f"Erro ao enviar para impressora Windows (exit {result.returncode})")
            
            log_info(f"ZPL enviado para impressora Windows: {printer_share}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao enviar para impressora Windows: {str(e)}")
            raise RuntimeError(f"Erro ao enviar para impressora Windows: {str(e)}")
    
    def save_to_file(self, output_dir: str, filename: str, data: str) -> str:
        """
        Salva ZPL em arquivo
        
        Args:
            output_dir: Diretório de saída
            filename: Nome do arquivo
            data: Dados ZPL
            
        Returns:
            Caminho completo do arquivo salvo
        """
        try:
            output_path = self.legacy_config.get('output_path', './output')
            os.makedirs(output_path, exist_ok=True)
            
            filename = f"label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zpl"
            file_path = os.path.join(output_path, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            
            log_info(f"ZPL salvo em {file_path}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao salvar arquivo: {str(e)}")
            raise RuntimeError(f"Erro ao salvar arquivo: {str(e)}")
    
    def send_print_job(self, zpl_data: str, quantity: int = 1) -> bool:
        """
        Envia job de impressão de acordo com a configuração
        
        Args:
            zpl_data: Dados ZPL para imprimir
            quantity: Quantidade de etiquetas
            
        Returns:
            True se enviado com sucesso
        """
        mode = self.legacy_config.get('output_mode', 'printer')
        
        try:
            log_info(f"Enviando job de impressão: {quantity} etiqueta(s) via {mode}")
            log_info(f"Impressora: {self.printer_config.get('name', 'Desconhecida')}")
            
            # Modo "configured" usa as configurações da impressora selecionada
            if mode == 'configured':
                printer_id = self.legacy_config.get('printer_id')
                if printer_id:
                    # Recarregar configuração da impressora
                    self.set_printer(printer_id)
                
                # Detectar tipo de conexão
                connection = self.printer_config.get('connection', {})
                conn_mode = connection.get('mode', 'usb')
                
                if conn_mode == 'network':
                    host = connection.get('ip_address', '127.0.0.1')
                    port = connection.get('port', 9100)
                    log_info(f"Usando impressora de rede: {host}:{port}")
                    return self.send_to_socket_printer(host, port, zpl_data)
                    
                elif conn_mode == 'usb':
                    device_name = connection.get('device_name', 'ZDesigner GK420t')
                    log_info(f"Usando impressora USB: {device_name}")
                    return self.send_to_windows_printer(device_name, zpl_data)
                else:
                    raise RuntimeError(f"Modo de conexão não suportado: {conn_mode}")
            
            elif mode == 'printer':
                host = self.legacy_config.get('printer_host', '127.0.0.1')
                port = self.legacy_config.get('printer_port', 9100)
                return self.send_to_socket_printer(host, port, zpl_data)
                
            elif mode == 'windows_printer':
                printer_share = self.legacy_config.get('windows_printer_share')
                if not printer_share:
                    raise RuntimeError("windows_printer_share não configurado")
                return self.send_to_windows_printer(printer_share, zpl_data)
                
            elif mode == 'file':
                output_dir = self.legacy_config.get('output_dir', './out')
                import datetime
                filename = f"labels_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{quantity}.zpl"
                self.save_to_file(output_dir, filename, zpl_data)
                return True
                
            else:
                raise RuntimeError(f"Modo de saída inválido: {mode}")
                
        except Exception as e:
            log_error(f"Erro no job de impressão: {str(e)}")
            raise
    
    def print_label(self, label_data: dict) -> bool:
        """
        Imprime uma etiqueta (método de compatibilidade)
        
        Args:
            label_data: Dados da etiqueta
            
        Returns:
            True se impresso com sucesso
        """
        zpl = self.generate_zpl(label_data)
        return self.send_print_job(zpl)
    
    def generate_zpl(self, label_data: dict) -> str:
        """
        Gera ZPL simples (método de compatibilidade)
        
        Args:
            label_data: Dados da etiqueta
            
        Returns:
            Código ZPL
        """
        text = label_data.get('text', 'TESTE')
        zpl_commands = f"^XA\n^FO50,50\n^ADN,36,20\n^FD{text}^FS\n^XZ"
        return zpl_commands