# Implementação do MODELO 03 - Impressão por Bloco Vertical

## Método build_block_addresses_zpl

Adicionar ao final da classe `ZplGenerator` em `src/printer/zpl_generator.py`:

```python
    def build_block_addresses_zpl(self, warehouse_code: str, warehouse_name: str,
                                   building_name: str, addresses_by_position: list) -> str:
        """
        Gera ZPL para MODELO 03: etiqueta com até 6 QR codes organizados por posição vertical
        Layout: 2 colunas x 3 linhas = 6 posições (do andar mais alto para o mais baixo)
        Etiqueta: 150mm x 100mm (1181 x 787 dots @ 203 DPI)
        
        Args:
            warehouse_code: Código do galpão (ex: COT001)
            warehouse_name: Nome do galpão (ex: Cotia 1)
            building_name: Nome do prédio (ex: Prédio A)
            addresses_by_position: Lista com até 6 dicts contendo 'full_address', 'floor_name'
                                   Ordenados do andar mais alto para o mais baixo
            
        Returns:
            Código ZPL para etiqueta de endereços por bloco vertical
        """
        # Dimensões da etiqueta 150mm x 100mm
        dpi = 203
        mm_to_dots = dpi / 25.4
        width_dots = int(round(150 * mm_to_dots))  # ~1181 dots
        height_dots = int(round(100 * mm_to_dots))  # ~787 dots
        
        zpl = "^XA\n"
        zpl += "^CI28\n"  # UTF-8
        zpl += f"^PW{width_dots}\n"
        zpl += f"^LL{height_dots}\n"
        zpl += "^LH0,0\n"
        
        # Título no topo: Galpão + Prédio
        title = f"{warehouse_name} ({warehouse_code}) - {building_name}"
        title_x = 50
        title_y = 40
        title_font_h = 50
        title_font_w = 40
        
        zpl += f"^FO{title_x},{title_y}\n"
        zpl += f"^A0N,{title_font_h},{title_font_w}\n"
        zpl += f"^FD{title}^FS\n"
        
        # Grid de QR codes: 2 colunas x 3 linhas
        qr_start_x = 120
        qr_start_y = 120
        qr_spacing_x = 550  # Espaço entre colunas
        qr_spacing_y = 210  # Espaço entre linhas
        qr_size = 8  # Magnification do QR code
        
        # Posição do texto abaixo do QR
        text_offset_y = 165
        floor_offset_y = 195
        text_font_h = 25
        text_font_w = 25
        floor_font_h = 30
        floor_font_w = 30
        
        # Mapear índice para posição no grid (direita para esquerda, cima para baixo)
        position_map = [
            (1, 0),  # idx 0: direita, linha 0 (andar mais alto)
            (0, 0),  # idx 1: esquerda, linha 0
            (1, 1),  # idx 2: direita, linha 1
            (0, 1),  # idx 3: esquerda, linha 1
            (1, 2),  # idx 4: direita, linha 2
            (0, 2),  # idx 5: esquerda, linha 2 (andar mais baixo)
        ]
        
        # Processar até 6 endereços
        for idx, addr_data in enumerate(addresses_by_position[:6]):
            col, row = position_map[idx]
            
            qr_x = qr_start_x + (col * qr_spacing_x)
            qr_y = qr_start_y + (row * qr_spacing_y)
            
            full_address = addr_data.get('full_address', '')
            floor_name = addr_data.get('floor_name', '')
            
            # QR Code
            zpl += f"^FO{qr_x},{qr_y}\n"
            zpl += f"^BQN,2,{qr_size}\n"
            zpl += f"^FDQA,{full_address}^FS\n"
            
            # Texto do endereço
            text_x = qr_x - 20
            text_y = qr_y + text_offset_y
            zpl += f"^FO{text_x},{text_y}\n"
            zpl += f"^A0N,{text_font_h},{text_font_w}\n"
            zpl += f"^FD{full_address}^FS\n"
            
            # Nome do andar
            floor_y = qr_y + floor_offset_y
            zpl += f"^FO{text_x},{floor_y}\n"
            zpl += f"^A0N,{floor_font_h},{floor_font_w}\n"
            zpl += f"^FD{floor_name}^FS\n"
        
        zpl += "^XZ\n"
        return zpl
```

## Adicionar método organize_by_block no AddressManager

```python
def organize_addresses_by_block(self) -> list:
    """
    Organiza endereços por posição vertical (bloco)
    Do andar mais alto para o mais baixo, mesma posição
    """
    if not self.warehouse_data:
        return []
    
    blocks = []
    buildings_data = self.warehouse_data.get('data', {}).get('buildings', [])
    
    for building in buildings_data:
        # Coletar todos os andares e ordenar por número (do mais alto para o mais baixo)
        floors = sorted(building.get('floors', []), 
                       key=lambda f: f.get('floor_number', 0), 
                       reverse=True)
        
        if not floors:
            continue
        
        # Encontrar número máximo de paletes em qualquer andar
        max_positions = max(len(floor.get('positions', [])) for floor in floors)
        
        # Iterar por cada posição
        for pos_idx in range(max_positions):
            block_positions = []
            
            # Coletar posição de cada andar (do mais alto para o mais baixo)
            for floor in floors:
                positions = floor.get('positions', [])
                if pos_idx < len(positions):
                    position = positions[pos_idx]
                    block_positions.append({
                        'full_address': position.get('full_address', ''),
                        'floor_name': floor.get('name', ''),
                        'position_number': position.get('position_number', 0)
                    })
            
            if block_positions:
                blocks.append({
                    'building_name': building.get('name', ''),
                    'building_code': building.get('code', ''),
                    'position_group': pos_idx + 1,
                    'addresses': block_positions
                })
    
    return blocks
```
