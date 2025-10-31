#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de Labels da API
Baseado no código PHP original
"""

from typing import List, Dict, Any, Optional, Tuple
from api.client import APIClient
from utils.logger import log_info, log_error

class LabelManager:
    """Gerenciador de labels da API"""
    
    def __init__(self, api_client: APIClient, token: str):
        """
        Inicializa o gerenciador
        
        Args:
            api_client: Cliente da API
            token: Token de autenticação
        """
        self.api_client = api_client
        self.token = token
    
    def list_labels(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista labels disponíveis
        
        Args:
            user_id: Filtrar por user_id (opcional)
            
        Returns:
            Lista de labels
        """
        try:
            # Montar headers
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Montar parâmetros da query
            params = {}
            if user_id:
                params['user_id'] = user_id
            
            # Fazer requisição
            response = self.api_client.get('/labels', headers=headers, params=params)
            
            if response.status_code == 200:
                labels = response.json()
                log_info(f"Listadas {len(labels)} labels da API")
                return labels
            else:
                log_error(f"Erro ao listar labels: HTTP {response.status_code}")
                raise RuntimeError(f"Falha ao listar labels. HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao listar labels: {str(e)}")
            raise
    
    def get_label_by_id(self, label_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca label por ID
        
        Args:
            label_id: ID da label
            
        Returns:
            Dados da label ou None se não encontrada
        """
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.get(f'/labels/{label_id}', headers=headers)
            
            if response.status_code == 200:
                label = response.json()
                log_info(f"Label ID {label_id} encontrada: {label.get('name', 'N/A')}")
                return label
            elif response.status_code == 404:
                log_info(f"Label ID {label_id} não encontrada")
                return None
            else:
                log_error(f"Erro ao buscar label {label_id}: HTTP {response.status_code}")
                raise RuntimeError(f"Erro ao buscar label. HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao buscar label {label_id}: {str(e)}")
            raise
    
    def create_label(self, name: str, user_id: int, last_number: int = 0) -> Dict[str, Any]:
        """
        Cria uma nova label
        
        Args:
            name: Nome da label
            user_id: ID do usuário dono da label
            last_number: Último número usado (padrão 0)
            
        Returns:
            Dados da label criada
        """
        try:
            data = {
                'name': name,
                'user_id': user_id,
                'last_number': last_number
            }
            
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.post('/labels', data=data, headers=headers)
            
            if response.status_code == 201:
                label = response.json()
                log_info(f"Label criada: {name} (ID: {label.get('id', 'N/A')})")
                return label
            else:
                log_error(f"Erro ao criar label: HTTP {response.status_code}")
                raise RuntimeError(f"Falha ao criar label. HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao criar label: {str(e)}")
            raise
    
    def update_last_number(self, label_id: int, last_number: int) -> bool:
        """
        Atualiza o último número de uma label
        
        Args:
            label_id: ID da label
            last_number: Novo último número
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            data = {'last_number': last_number}
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.api_client.put(f'/labels/{label_id}', data=data, headers=headers)
            
            if response.status_code == 200:
                log_info(f"Label {label_id}: last_number atualizado para {last_number}")
                return True
            else:
                log_error(f"Erro ao atualizar label {label_id}: HTTP {response.status_code}")
                raise RuntimeError(f"Falha ao atualizar last_number. HTTP {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro ao atualizar label {label_id}: {str(e)}")
            raise
    
    def find_existing_label(self, name: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Procura label existente por nome e user_id
        
        Args:
            name: Nome da label
            user_id: ID do usuário
            
        Returns:
            Label encontrada ou None
        """
        try:
            labels = self.list_labels(user_id)
            
            for label in labels:
                if (label.get('name', '').lower() == name.lower() and 
                    int(label.get('user_id', 0)) == int(user_id)):
                    return label
            
            return None
            
        except Exception as e:
            log_error(f"Erro ao procurar label existente: {str(e)}")
            raise
    
    def get_or_create_label(self, name: str, user_id: int) -> Dict[str, Any]:
        """
        Busca label existente ou cria uma nova
        
        Args:
            name: Nome da label
            user_id: ID do usuário
            
        Returns:
            Dados da label (existente ou nova)
        """
        try:
            # Primeiro, tentar encontrar existente
            existing = self.find_existing_label(name, user_id)
            if existing:
                log_info(f"Usando label existente: {name} (ID: {existing.get('id', 'N/A')})")
                return existing
            
            # Se não existe, criar nova
            log_info(f"Criando nova label: {name}")
            return self.create_label(name, user_id)
            
        except Exception as e:
            log_error(f"Erro ao obter/criar label: {str(e)}")
            raise
    
    def pad8(self, n: int) -> str:
        """Formata número com 8 dígitos com zeros à esquerda"""
        return str(n).zfill(8)
    
    def calculate_sequence(self, label: Dict[str, Any], quantity: int) -> Tuple[int, int, int]:
        """
        Calcula sequência de impressão
        
        Args:
            label: Dados da label
            quantity: Quantidade a imprimir
            
        Returns:
            Tupla (last_number, start, end)
        """
        last = int(label.get('last_number', 0))
        start = last + 1
        end = last + quantity
        
        return last, start, end
    
    def format_label_display(self, labels: List[Dict[str, Any]]) -> str:
        """
        Formata labels para exibição
        
        Args:
            labels: Lista de labels
            
        Returns:
            String formatada para exibição
        """
        if not labels:
            return "(nenhuma label cadastrada)"
        
        lines = []
        for i, label in enumerate(labels):
            last_number = self.pad8(label.get('last_number', 0))
            name = label.get('name', f'label {i+1}')
            user_id = label.get('user_id', 'N/A')
            lines.append(f"[{i+1}] {name}\t(last: {last_number}, user_id: {user_id})")
        
        return "\n".join(lines)