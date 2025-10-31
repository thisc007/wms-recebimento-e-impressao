#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de Cargos da API para reimpressão
Baseado no código PHP/PowerShell original
"""

from typing import Dict, Any, Optional
from api.client import APIClient
from utils.logger import log_info, log_error

class CargoManager:
    """Gerenciador de cargos da API"""
    
    def __init__(self, api_client: APIClient, token: str):
        """
        Inicializa o gerenciador
        
        Args:
            api_client: Cliente da API
            token: Token de autenticação
        """
        self.api_client = api_client
        self.token = token
    
    def get_cargo_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Busca cargo por código
        
        Args:
            code: Código da etiqueta (8 ou 9 dígitos)
            
        Returns:
            Dados do cargo ou None se não encontrado
        """
        try:
            # Validar formato do código
            if not self.validate_code_format(code):
                raise ValueError("Código inválido. Use 8 ou 9 dígitos numéricos.")
            
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.get(f'/cargos/code/{code}', headers=headers)
            
            if response.status_code == 200:
                cargo_response = response.json()
                cargo = cargo_response.get('data')
                
                if cargo:
                    log_info(f"Cargo encontrado: código {code}")
                    return cargo
                else:
                    log_info(f"Cargo não encontrado: código {code}")
                    return None
                    
            elif response.status_code == 404:
                log_info(f"Cargo não encontrado: código {code}")
                return None
            elif response.status_code == 422:
                log_error(f"Código inválido ou não encontrado: {code}")
                return None
            else:
                log_error(f"Erro ao buscar cargo {code}: HTTP {response.status_code}")
                raise RuntimeError(f"Erro ao buscar cargo. HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao buscar cargo {code}: {str(e)}")
            raise
    
    def validate_code_format(self, code: str) -> bool:
        """
        Valida formato do código
        
        Args:
            code: Código a validar
            
        Returns:
            True se válido
        """
        # Aceita apenas códigos numéricos de 8 ou 9 dígitos
        return code.isdigit() and len(code) in [8, 9]
    
    def get_code_to_print(self, cargo: Dict[str, Any]) -> str:
        """
        Extrai código para impressão do cargo
        
        Args:
            cargo: Dados do cargo
            
        Returns:
            Código para impressão
        """
        code = cargo.get('code') or cargo.get('label_code')
        if not code:
            raise ValueError("Cargo não possui código válido para impressão")
        return str(code)
    
    def format_cargo_details(self, cargo: Dict[str, Any]) -> str:
        """
        Formata detalhes do cargo para exibição
        
        Args:
            cargo: Dados do cargo
            
        Returns:
            String formatada com detalhes
        """
        details = []
        details.append(f"Código: {cargo.get('code', 'N/A')}")
        details.append(f"Código de etiqueta: {cargo.get('label_code', 'N/A')}")
        details.append(f"Status: {cargo.get('status', 'N/A')}")
        
        # Dados da etiqueta se disponíveis
        label_data = cargo.get('label_data', {})
        if label_data:
            details.append(f"Tipo: {label_data.get('cargo_type', 'N/A')}")
            details.append(f"Cliente: {label_data.get('customer', 'N/A')}")
            details.append(f"Peso: {label_data.get('weight', 'N/A')} kg")
            details.append(f"Volume: {label_data.get('volume', 'N/A')} m³")
            details.append(f"Criado em: {label_data.get('created_at', 'N/A')}")
        
        return "\n".join(f"  - {detail}" for detail in details)