#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de Configuração de Impressoras
Gerencia configurações das impressoras Zebra GK420t (USB e Rede)
"""

import json
import os
import socket
import subprocess
from typing import Dict, List, Optional, Any
import sys

# Adicionar o diretório src ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import log_info, log_error, log_warning

class PrinterConfigManager:
    """Gerenciador de configurações de impressoras"""
    
    def __init__(self, config_file: str = None):
        """
        Inicializa o gerenciador de configurações
        
        Args:
            config_file: Caminho para o arquivo de configuração
        """
        if config_file is None:
            # Subir dois níveis do src/utils para chegar à raiz do projeto
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.config_file = os.path.join(project_root, 'config', 'printer_config.json')
        else:
            self.config_file = config_file
            
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carrega configurações do arquivo JSON
        
        Returns:
            Dicionário com configurações das impressoras
        """
        try:
            if not os.path.exists(self.config_file):
                log_warning(f"Arquivo de configuração não encontrado: {self.config_file}")
                return self._get_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                log_info("Configurações de impressora carregadas com sucesso")
                return config
                
        except Exception as e:
            log_error(f"Erro ao carregar configurações: {str(e)}")
            return self._get_default_config()
    
    def save_config(self) -> bool:
        """
        Salva configurações no arquivo JSON
        
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                
            log_info("Configurações salvas com sucesso")
            return True
            
        except Exception as e:
            log_error(f"Erro ao salvar configurações: {str(e)}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retorna configuração padrão
        
        Returns:
            Configuração padrão
        """
        return {
            "default_printer": "usb_printer",
            "printers": {
                "usb_printer": {
                    "id": "usb_printer",
                    "name": "Zebra GK420t USB",
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
            },
            "global_settings": {
                "test_pattern": True,
                "auto_calibrate": False,
                "label_format": "zpl",
                "encoding": "utf-8"
            }
        }
    
    def get_default_printer(self) -> Optional[Dict[str, Any]]:
        """
        Retorna configuração da impressora padrão
        
        Returns:
            Configuração da impressora padrão ou None
        """
        default_id = self.config.get('default_printer')
        if default_id and default_id in self.config.get('printers', {}):
            return self.config['printers'][default_id]
        return None
    
    def set_default_printer(self, printer_id: str) -> bool:
        """
        Define impressora padrão
        
        Args:
            printer_id: ID da impressora
            
        Returns:
            True se definiu com sucesso, False caso contrário
        """
        if printer_id in self.config.get('printers', {}):
            self.config['default_printer'] = printer_id
            return self.save_config()
        return False
    
    def get_printer(self, printer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna configuração de uma impressora específica
        
        Args:
            printer_id: ID da impressora
            
        Returns:
            Configuração da impressora ou None
        """
        return self.config.get('printers', {}).get(printer_id)
    
    def get_all_printers(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna todas as configurações de impressoras
        
        Returns:
            Dicionário com todas as impressoras
        """
        return self.config.get('printers', {})
    
    def get_enabled_printers(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna apenas impressoras habilitadas
        
        Returns:
            Dicionário com impressoras habilitadas
        """
        printers = self.config.get('printers', {})
        return {pid: config for pid, config in printers.items() 
                if config.get('enabled', False)}
    
    def add_printer(self, printer_config: Dict[str, Any]) -> bool:
        """
        Adiciona nova impressora
        
        Args:
            printer_config: Configuração da impressora
            
        Returns:
            True se adicionou com sucesso, False caso contrário
        """
        try:
            printer_id = printer_config.get('id')
            if not printer_id:
                log_error("ID da impressora é obrigatório")
                return False
            
            if 'printers' not in self.config:
                self.config['printers'] = {}
                
            self.config['printers'][printer_id] = printer_config
            return self.save_config()
            
        except Exception as e:
            log_error(f"Erro ao adicionar impressora: {str(e)}")
            return False
    
    def update_printer(self, printer_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza configuração de impressora
        
        Args:
            printer_id: ID da impressora
            updates: Atualizações a aplicar
            
        Returns:
            True se atualizou com sucesso, False caso contrário
        """
        try:
            if printer_id not in self.config.get('printers', {}):
                log_error(f"Impressora {printer_id} não encontrada")
                return False
            
            # Atualizar recursivamente
            self._deep_update(self.config['printers'][printer_id], updates)
            return self.save_config()
            
        except Exception as e:
            log_error(f"Erro ao atualizar impressora: {str(e)}")
            return False
    
    def enable_printer(self, printer_id: str) -> bool:
        """
        Habilita impressora
        
        Args:
            printer_id: ID da impressora
            
        Returns:
            True se habilitou com sucesso, False caso contrário
        """
        return self.update_printer(printer_id, {'enabled': True})
    
    def disable_printer(self, printer_id: str) -> bool:
        """
        Desabilita impressora
        
        Args:
            printer_id: ID da impressora
            
        Returns:
            True se desabilitou com sucesso, False caso contrário
        """
        return self.update_printer(printer_id, {'enabled': False})
    
    def remove_printer(self, printer_id: str) -> bool:
        """
        Remove impressora
        
        Args:
            printer_id: ID da impressora
            
        Returns:
            True se removeu com sucesso, False caso contrário
        """
        try:
            if printer_id not in self.config.get('printers', {}):
                log_error(f"Impressora {printer_id} não encontrada")
                return False
            
            del self.config['printers'][printer_id]
            
            # Se era a padrão, resetar
            if self.config.get('default_printer') == printer_id:
                remaining = list(self.config.get('printers', {}).keys())
                self.config['default_printer'] = remaining[0] if remaining else None
            
            return self.save_config()
            
        except Exception as e:
            log_error(f"Erro ao remover impressora: {str(e)}")
            return False
    
    def test_connection(self, printer_id: str, send_test_pattern: bool = False) -> bool:
        """
        Testa conexão com impressora
        
        Args:
            printer_id: ID da impressora
            send_test_pattern: Se deve enviar um padrão de teste
            
        Returns:
            True se conectou com sucesso, False caso contrário
        """
        printer = self.get_printer(printer_id)
        if not printer:
            log_error(f"Impressora {printer_id} não encontrada")
            return False
        
        connection = printer.get('connection', {})
        mode = connection.get('mode')
        
        try:
            # Primeiro teste básico de conectividade
            connection_ok = False
            if mode == 'network':
                connection_ok = self._test_network_connection(connection)
            elif mode == 'usb':
                connection_ok = self._test_usb_connection(connection)
            else:
                log_error(f"Modo de conexão desconhecido: {mode}")
                return False
            
            # Se conectividade básica OK e solicitado teste de padrão
            if connection_ok and send_test_pattern:
                return self._send_test_pattern(printer_id, connection, mode)
            
            return connection_ok
                
        except Exception as e:
            log_error(f"Erro ao testar conexão: {str(e)}")
            return False
    
    def _test_network_connection(self, connection: Dict[str, Any]) -> bool:
        """
        Testa conexão de rede
        
        Args:
            connection: Configuração de conexão
            
        Returns:
            True se conectou, False caso contrário
        """
        ip_address = connection.get('ip_address')
        port = connection.get('port', 9100)
        timeout = connection.get('timeout', 5)
        
        if not ip_address:
            log_error("Endereço IP não configurado")
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            
            if result == 0:
                log_info(f"Conexão de rede bem-sucedida: {ip_address}:{port}")
                return True
            else:
                log_warning(f"Falha na conexão de rede: {ip_address}:{port}")
                return False
                
        except Exception as e:
            log_error(f"Erro na conexão de rede: {str(e)}")
            return False
    
    def _test_usb_connection(self, connection: Dict[str, Any]) -> bool:
        """
        Testa conexão USB
        
        Args:
            connection: Configuração de conexão
            
        Returns:
            True se conectou, False caso contrário
        """
        device_name = connection.get('device_name')
        
        if not device_name:
            log_error("Nome do dispositivo USB não configurado")
            return False
        
        try:
            # Verificar se impressora USB está disponível (Windows)
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['wmic', 'printer', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and device_name in result.stdout:
                    log_info(f"Impressora USB encontrada: {device_name}")
                    return True
                else:
                    log_warning(f"Impressora USB não encontrada: {device_name}")
                    return False
            else:
                # Para Linux/Mac, implementar verificação específica
                log_warning("Teste de conexão USB não implementado para este sistema")
                return True
                
        except Exception as e:
            log_error(f"Erro na verificação USB: {str(e)}")
            return False
    
    def _send_test_pattern(self, printer_id: str, connection: Dict[str, Any], mode: str) -> bool:
        """
        Envia padrão de teste para a impressora
        
        Args:
            printer_id: ID da impressora
            connection: Configuração de conexão
            mode: Modo de conexão (network/usb)
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            # Gerar ZPL de teste simples
            test_zpl = self._generate_test_zpl()
            
            if mode == 'network':
                return self._send_zpl_network(test_zpl, connection)
            elif mode == 'usb':
                return self._send_zpl_usb(test_zpl, connection)
            else:
                log_error(f"Modo não suportado para teste: {mode}")
                return False
                
        except Exception as e:
            log_error(f"Erro ao enviar padrão de teste: {str(e)}")
            return False
    
    def _generate_test_zpl(self) -> str:
        """
        Gera código ZPL para teste de impressão
        
        Returns:
            Código ZPL de teste
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        zpl = f"""^XA
^FO50,50^GFA,300,300,15,,:::::P03FC,O01FFFE,N07FFFF8,M01FFFFFC,M07FFFFF,M0FFFFFF8,L01FFFFFFC,L03FFFFFFE,L07FFFFFFE,L0FFFFFFFF,L1FFFFFFFF,L3FFFFFFFF,L7FFFFFFFF,LFFFFFFFF8,M7FFFFFFF,M3FFFFFFC,M1FFFFFF8,M07FFFFF,N01FFFFE,N007FFC,P01F8,::::^FS
^FO50,130^A0N,25,25^FDTeste de Impressora^FS
^FO50,170^A0N,20,20^FDData/Hora: {timestamp}^FS
^FO50,200^A0N,20,20^FDImpressora: TESTE^FS
^FO50,230^A0N,15,15^FDSe voce pode ler isto,^FS
^FO50,250^A0N,15,15^FDa impressora esta funcionando!^FS
^FO50,280^BCN,60,Y,N,N^FD123456789^FS
^XZ"""
        
        return zpl
    
    def _send_zpl_network(self, zpl: str, connection: Dict[str, Any]) -> bool:
        """
        Envia ZPL via rede
        
        Args:
            zpl: Código ZPL
            connection: Configuração de conexão
            
        Returns:
            True se enviou com sucesso
        """
        ip_address = connection.get('ip_address')
        port = connection.get('port', 9100)
        timeout = connection.get('timeout', 5)
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((ip_address, port))
                sock.sendall(zpl.encode('utf-8'))
                log_info(f"Padrão de teste enviado para {ip_address}:{port}")
                return True
                
        except Exception as e:
            log_error(f"Erro ao enviar ZPL via rede: {str(e)}")
            return False
    
    def _send_zpl_usb(self, zpl: str, connection: Dict[str, Any]) -> bool:
        """
        Envia ZPL via USB
        
        Args:
            zpl: Código ZPL  
            connection: Configuração de conexão
            
        Returns:
            True se enviou com sucesso
        """
        device_name = connection.get('device_name')
        
        try:
            if os.name == 'nt':  # Windows
                # Tentar enviar via spooler do Windows
                import tempfile
                import subprocess
                
                # Criar arquivo temporário
                with tempfile.NamedTemporaryFile(mode='w', suffix='.zpl', delete=False) as f:
                    f.write(zpl)
                    temp_file = f.name
                
                # Enviar para impressora via copy
                result = subprocess.run(
                    ['copy', temp_file, f'\\\\localhost\\"{device_name}"'],
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                # Limpar arquivo temporário
                os.unlink(temp_file)
                
                if result.returncode == 0:
                    log_info(f"Padrão de teste enviado para USB: {device_name}")
                    return True
                else:
                    log_error(f"Erro ao enviar para USB: {result.stderr}")
                    return False
            else:
                # Para Linux/Mac - implementar conforme necessário
                log_warning("Envio de teste USB não implementado para este sistema")
                return True
                
        except Exception as e:
            log_error(f"Erro ao enviar ZPL via USB: {str(e)}")
            return False
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """
        Atualização recursiva de dicionários
        
        Args:
            target: Dicionário alvo
            source: Dicionário fonte
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

# Instância global
printer_config = PrinterConfigManager()