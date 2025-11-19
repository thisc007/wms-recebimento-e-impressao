#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de endereços de armazém para impressão de etiquetas
Processa dados da API de warehouse e organiza paletes por andar
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Tuple
from utils.logger import log_info, log_error

class AddressManager:
    """Gerencia endereços de warehouse e organiza para impressão"""
    
    def __init__(self):
        """Inicializa o gerenciador de endereços"""
        self.warehouse_data = None
        
    def load_warehouse_data(self, warehouse_data: Dict[str, Any]) -> bool:
        """
        Carrega dados do warehouse retornados pela API
        
        Args:
            warehouse_data: Dict com estrutura completa do warehouse da API
            
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            if not warehouse_data or 'data' not in warehouse_data:
                log_error("Dados de warehouse inválidos")
                return False
                
            self.warehouse_data = warehouse_data['data']
            log_info(f"Warehouse carregado: {self.warehouse_data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao carregar warehouse: {str(e)}")
            return False
    
    def get_warehouse_info(self) -> Dict[str, str]:
        """
        Retorna informações básicas do warehouse
        
        Returns:
            Dict com code, name, etc do warehouse
        """
        if not self.warehouse_data:
            return {}
            
        return {
            'code': self.warehouse_data.get('code', ''),
            'name': self.warehouse_data.get('name', ''),
            'id': self.warehouse_data.get('id', 0)
        }
    
    def get_buildings(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de prédios do warehouse
        
        Returns:
            Lista de dicts com informações dos prédios
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return []
            
        buildings = []
        for building in self.warehouse_data['buildings']:
            buildings.append({
                'id': building.get('id'),
                'code': building.get('code'),
                'name': building.get('name'),
                'floors_count': building.get('total_floors', 0)
            })
            
        return buildings
    
    def get_floors_by_building(self, building_id: int) -> List[Dict[str, Any]]:
        """
        Retorna lista de andares de um prédio específico
        
        Args:
            building_id: ID do prédio
            
        Returns:
            Lista de dicts com informações dos andares
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return []
            
        for building in self.warehouse_data['buildings']:
            if building.get('id') == building_id:
                floors = []
                for floor in building.get('floors', []):
                    floors.append({
                        'id': floor.get('id'),
                        'code': floor.get('code'),
                        'name': floor.get('name'),
                        'pallets_count': len(floor.get('pallets', []))
                    })
                return floors
                
        return []
    
    def get_pallets_by_floor(self, building_id: int, floor_id: int) -> List[Dict[str, Any]]:
        """
        Retorna lista de paletes de um andar específico
        
        Args:
            building_id: ID do prédio
            floor_id: ID do andar
            
        Returns:
            Lista de dicts com informações dos paletes
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return []
            
        for building in self.warehouse_data['buildings']:
            if building.get('id') == building_id:
                for floor in building.get('floors', []):
                    if floor.get('id') == floor_id:
                        pallets = []
                        for pallet in floor.get('pallets', []):
                            pallets.append({
                                'id': pallet.get('id'),
                                'code': pallet.get('code'),
                                'name': pallet.get('name'),
                                'full_address': pallet.get('full_address', ''),
                                'short_address': pallet.get('short_address', ''),
                                'status': pallet.get('status', 'LIVRE')
                            })
                        return pallets
                        
        return []
    
    def organize_addresses_by_floor(self) -> List[Dict[str, Any]]:
        """
        Organiza todos os endereços agrupados por andar para impressão em lote
        
        Returns:
            Lista de dicts com estrutura:
            {
                'warehouse_code': 'COT001',
                'warehouse_name': 'Cotia 1',
                'building_id': 13,
                'building_code': 'A',
                'building_name': 'Prédio A',
                'floor_id': 61,
                'floor_code': '01',
                'floor_name': 'Térreo',
                'pallets': [
                    {'full_address': 'COT001-A-01-01', 'name': 'Palete 01', ...},
                    ...
                ]
            }
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return []
            
        organized = []
        warehouse_info = self.get_warehouse_info()
        
        for building in self.warehouse_data['buildings']:
            building_id = building.get('id')
            building_code = building.get('code', '')
            building_name = building.get('name', '')
            
            for floor in building.get('floors', []):
                floor_id = floor.get('id')
                floor_code = floor.get('code', '')
                floor_name = floor.get('name', '')
                
                pallets = []
                for pallet in floor.get('pallets', []):
                    pallets.append({
                        'id': pallet.get('id'),
                        'code': pallet.get('code'),
                        'name': pallet.get('name'),
                        'full_address': pallet.get('full_address', ''),
                        'short_address': pallet.get('short_address', ''),
                        'status': pallet.get('status', 'LIVRE')
                    })
                
                if pallets:  # Só adicionar se houver paletes
                    organized.append({
                        'warehouse_code': warehouse_info['code'],
                        'warehouse_name': warehouse_info['name'],
                        'building_id': building_id,
                        'building_code': building_code,
                        'building_name': building_name,
                        'floor_id': floor_id,
                        'floor_code': floor_code,
                        'floor_name': floor_name,
                        'pallets': pallets
                    })
        
        return organized
    
    def get_floor_labels_data(self, building_id: int, floor_id: int) -> Tuple[Dict[str, str], List[List[Dict[str, str]]]]:
        """
        Retorna dados formatados para gerar etiquetas de um andar (MODELO 01)
        Divide os paletes em grupos de 8 para múltiplas etiquetas se necessário
        
        Args:
            building_id: ID do prédio
            floor_id: ID do andar
            
        Returns:
            Tupla (header_info, groups_of_pallets) onde:
            - header_info: Dict com warehouse_code, warehouse_name, building_name, floor_name
            - groups_of_pallets: Lista de grupos, cada grupo com até 8 paletes
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return ({}, [])
            
        warehouse_info = self.get_warehouse_info()
        
        for building in self.warehouse_data['buildings']:
            if building.get('id') == building_id:
                building_name = building.get('name', '')
                
                for floor in building.get('floors', []):
                    if floor.get('id') == floor_id:
                        floor_name = floor.get('name', '')
                        
                        # Informações do header
                        header = {
                            'warehouse_code': warehouse_info['code'],
                            'warehouse_name': warehouse_info['name'],
                            'building_name': building_name,
                            'floor_name': floor_name
                        }
                        
                        # Paletes para impressão
                        pallets = []
                        for pallet in floor.get('pallets', []):
                            pallets.append({
                                'full_address': pallet.get('full_address', ''),
                                'name': pallet.get('name', '')
                            })
                        
                        # Dividir em grupos de 8
                        groups = []
                        for i in range(0, len(pallets), 8):
                            groups.append(pallets[i:i+8])
                        
                        return (header, groups)
        
        return ({}, [])
    
    def get_pallet_label_data(self, building_id: int, floor_id: int, pallet_id: int) -> Dict[str, str]:
        """
        Retorna dados formatados para gerar etiqueta de um palete individual (MODELO 02)
        
        Args:
            building_id: ID do prédio
            floor_id: ID do andar
            pallet_id: ID do palete
            
        Returns:
            Dict com full_address, pallet_name, building_name, floor_name
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return {}
            
        for building in self.warehouse_data['buildings']:
            if building.get('id') == building_id:
                building_name = building.get('name', '')
                
                for floor in building.get('floors', []):
                    if floor.get('id') == floor_id:
                        floor_name = floor.get('name', '')
                        
                        for pallet in floor.get('pallets', []):
                            if pallet.get('id') == pallet_id:
                                return {
                                    'full_address': pallet.get('full_address', ''),
                                    'pallet_name': pallet.get('name', ''),
                                    'building_name': building_name,
                                    'floor_name': floor_name
                                }
        
        return {}
    
    def organize_addresses_by_block(self) -> List[Dict[str, Any]]:
        """
        Organiza todos os endereços agrupados por POSIÇÃO VERTICAL (bloco)
        Para impressão de MODELO 03: imprime mesma posição de todos os andares
        Do andar mais alto para o mais baixo
        
        Returns:
            Lista de dicts com estrutura:
            {
                'warehouse_code': 'COT001',
                'warehouse_name': 'Cotia 1',
                'building_id': 13,
                'building_code': 'A',
                'building_name': 'Prédio A',
                'position_group': 1,  # Número da posição (1, 2, 3...)
                'addresses': [
                    {'full_address': 'COT001-A-03-01', 'floor_name': '3º Andar', 'position_number': 1},
                    {'full_address': 'COT001-A-02-01', 'floor_name': '2º Andar', 'position_number': 1},
                    {'full_address': 'COT001-A-01-01', 'floor_name': '1º Andar', 'position_number': 1},
                    {'full_address': 'COT001-A-00-01', 'floor_name': 'Térreo', 'position_number': 1},
                ]
            }
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return []
            
        organized = []
        warehouse_info = self.get_warehouse_info()
        
        for building in self.warehouse_data['buildings']:
            building_id = building.get('id')
            building_code = building.get('code', '')
            building_name = building.get('name', '')
            
            # Coletar todos os andares e ordenar do mais alto para o mais baixo
            floors = sorted(
                building.get('floors', []),
                key=lambda f: f.get('floor_number', 0),
                reverse=True  # Andar mais alto primeiro
            )
            
            if not floors:
                continue
            
            # Encontrar número máximo de posições em qualquer andar deste prédio
            max_positions = 0
            for floor in floors:
                pallets = floor.get('pallets', [])
                if pallets:
                    # Assumindo que pallet.code ou position_number indica a posição
                    # Vamos usar o tamanho da lista como indicativo
                    max_positions = max(max_positions, len(pallets))
            
            # Iterar por cada número de posição (1, 2, 3, etc.)
            for pos_idx in range(max_positions):
                block_addresses = []
                
                # Coletar a posição pos_idx de cada andar (do mais alto para o mais baixo)
                for floor in floors:
                    floor_name = floor.get('name', '')
                    pallets = floor.get('pallets', [])
                    
                    # Se este andar tem palete nesta posição
                    if pos_idx < len(pallets):
                        pallet = pallets[pos_idx]
                        block_addresses.append({
                            'full_address': pallet.get('full_address', ''),
                            'floor_name': floor_name,
                            'position_number': pos_idx + 1  # Posição baseada em 1
                        })
                
                # Se encontrou endereços para esta posição, adicionar ao resultado
                if block_addresses:
                    organized.append({
                        'warehouse_code': warehouse_info['code'],
                        'warehouse_name': warehouse_info['name'],
                        'building_id': building_id,
                        'building_code': building_code,
                        'building_name': building_name,
                        'position_group': pos_idx + 1,  # Número da posição (1-based)
                        'addresses': block_addresses
                    })
        
        return organized
    
    def get_all_pallets_flat(self) -> List[Dict[str, Any]]:
        """
        Retorna lista plana de todos os paletes com contexto completo
        Útil para exibição em lista/grid
        
        Returns:
            Lista de dicts com informações completas de cada palete
        """
        if not self.warehouse_data or 'buildings' not in self.warehouse_data:
            return []
            
        all_pallets = []
        warehouse_info = self.get_warehouse_info()
        
        for building in self.warehouse_data['buildings']:
            building_id = building.get('id')
            building_code = building.get('code', '')
            building_name = building.get('name', '')
            
            for floor in building.get('floors', []):
                floor_id = floor.get('id')
                floor_code = floor.get('code', '')
                floor_name = floor.get('name', '')
                
                for pallet in floor.get('pallets', []):
                    all_pallets.append({
                        'warehouse_code': warehouse_info['code'],
                        'warehouse_name': warehouse_info['name'],
                        'building_id': building_id,
                        'building_code': building_code,
                        'building_name': building_name,
                        'floor_id': floor_id,
                        'floor_code': floor_code,
                        'floor_name': floor_name,
                        'pallet_id': pallet.get('id'),
                        'pallet_code': pallet.get('code'),
                        'pallet_name': pallet.get('name'),
                        'full_address': pallet.get('full_address', ''),
                        'short_address': pallet.get('short_address', ''),
                        'status': pallet.get('status', 'LIVRE')
                    })
        
        return all_pallets
