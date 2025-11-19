# MODELO 03 - Impressão por Bloco Vertical

## Visão Geral

O **MODELO 03** permite imprimir etiquetas de endereçamento organizadas por **posição vertical** através de todos os andares do prédio, ao invés de por andar.

## Conceito

### Organização Tradicional (MODELO 01 - Por Andar):
```
Etiqueta 1: Térreo - Pos 01, 02, 03, 04, 05, 06
Etiqueta 2: 1º Andar - Pos 01, 02, 03, 04, 05, 06  
Etiqueta 3: 2º Andar - Pos 01, 02, 03, 04, 05, 06
```

### Nova Organização (MODELO 03 - Por Bloco):
```
Etiqueta 1: Posição 01 - 2º Andar, 1º Andar, Térreo (do mais alto ao mais baixo)
Etiqueta 2: Posição 02 - 2º Andar, 1º Andar, Térreo
Etiqueta 3: Posição 03 - 2º Andar, 1º Andar, Térreo
```

## Especificações Técnicas

### Layout da Etiqueta
- **Formato:** 150mm x 100mm (1181 x 787 dots @ 203 DPI)
- **Orientação:** Horizontal
- **Grid:** 2 colunas x 3 linhas = até 6 QR codes por etiqueta
- **QR Size:** Magnification 8

### Organização do Grid

```
┌─────────────────────────────────────────────┐
│  Galpão Cotia 1 (COT001) - Prédio A         │
├─────────────────────────────────────────────┤
│                                             │
│   [QR: Pos 01]        [QR: Pos 01]         │
│   3º Andar            2º Andar              │
│                                             │
│   [QR: Pos 01]        [QR: Pos 01]         │
│   1º Andar            Térreo                │
│                                             │
│   [QR: Pos 01]        [QR: Pos 01]         │
│   -1                  -2                    │
│                                             │
└─────────────────────────────────────────────┘
```

### Mapeamento de Posições

O grid é preenchido seguindo esta ordem:
```python
position_map = [
    (1, 0),  # idx 0: coluna direita, linha superior (andar mais alto)
    (0, 0),  # idx 1: coluna esquerda, linha superior
    (1, 1),  # idx 2: coluna direita, linha do meio
    (0, 1),  # idx 3: coluna esquerda, linha do meio
    (1, 2),  # idx 4: coluna direita, linha inferior
    (0, 2),  # idx 5: coluna esquerda, linha inferior (andar mais baixo)
]
```

**Prioridade de preenchimento:**
1. Direita → Esquerda
2. Cima → Baixo (andar mais alto → andar mais baixo)

## Componentes Implementados

### 1. ZplGenerator.build_block_addresses_zpl()

**Arquivo:** `src/printer/zpl_generator.py`

```python
def build_block_addresses_zpl(self, warehouse_code: str, warehouse_name: str,
                               building_name: str, addresses_by_position: list) -> str:
    """
    Gera ZPL para MODELO 03: etiqueta com até 6 QR codes organizados por posição vertical
    
    Args:
        warehouse_code: Código do galpão (ex: COT001)
        warehouse_name: Nome do galpão (ex: Cotia 1)
        building_name: Nome do prédio (ex: Prédio A)
        addresses_by_position: Lista com até 6 dicts contendo:
            - full_address: Endereço completo (COT001-A-03-01)
            - floor_name: Nome do andar (3º Andar)
            Ordenados do andar mais alto para o mais baixo
    
    Returns:
        Código ZPL para impressão
    """
```

**Características:**
- Grid 2x3 com espaçamento otimizado
- QR Code size 8 (165x165 dots)
- Texto do endereço (25pt) abaixo do QR
- Nome do andar (30pt) abaixo do endereço
- Título centralizado com warehouse + building

### 2. AddressManager.organize_addresses_by_block()

**Arquivo:** `src/address_manager.py`

```python
def organize_addresses_by_block(self) -> List[Dict[str, Any]]:
    """
    Organiza endereços por POSIÇÃO VERTICAL (bloco)
    Do andar mais alto para o mais baixo
    
    Returns:
        Lista de dicts com estrutura:
        {
            'warehouse_code': 'COT001',
            'warehouse_name': 'Cotia 1',
            'building_id': 13,
            'building_code': 'A',
            'building_name': 'Prédio A',
            'position_group': 1,  # Número da posição
            'addresses': [
                {'full_address': 'COT001-A-03-01', 'floor_name': '3º Andar'},
                {'full_address': 'COT001-A-02-01', 'floor_name': '2º Andar'},
                {'full_address': 'COT001-A-01-01', 'floor_name': '1º Andar'},
            ]
        }
    """
```

**Lógica:**
1. Ordena andares por `floor_number` (reverse=True) - do mais alto ao mais baixo
2. Determina número máximo de posições em qualquer andar
3. Para cada posição (1, 2, 3...), coleta os endereços de todos os andares
4. Retorna lista agrupada por `position_group`

### 3. Interface de Usuário

**Arquivo:** `src/ui/address_labels_window.py`

**Novos Elementos:**

#### Radio Buttons de Modo
```python
mode_frame = ttk.LabelFrame(main_frame, text="Modo de Impressão")

ttk.Radiobutton(mode_frame, text="🏢 Por Bloco (Posição Vertical) - MODELO 03", 
               variable=self.mode_var, value='block')

ttk.Radiobutton(mode_frame, text="📊 Por Andar (6 QR por Etiqueta) - MODELO 01", 
               variable=self.mode_var, value='floor')
```

#### Método _print_all()
Decide qual método chamar baseado no modo selecionado:
- `mode='block'` → `_print_all_blocks()`
- `mode='floor'` → `_print_all_floors()`

#### Método _print_all_blocks()
```python
def _print_all_blocks(self):
    """Imprime etiquetas de todos os blocos (MODELO 03)"""
    # 1. Valida seleção de galpão e impressora
    # 2. Confirma com usuário
    # 3. Para cada block_data em organized_blocks:
    #    - Divide addresses em grupos de 6
    #    - Gera ZPL com build_block_addresses_zpl()
    #    - Envia para impressora
    # 4. Mostra resultado (sucesso/erros)
```

## Fluxo de Uso

### 1. Seleção do Modo
1. Abrir janela "Etiquetas de Endereçamento"
2. Selecionar **"Por Bloco (Posição Vertical)"** nos radio buttons
3. Seleção padrão é "Por Bloco"

### 2. Configuração
1. Selecionar galpão no dropdown
2. Selecionar impressora
3. Sistema carrega e organiza dados automaticamente

### 3. Impressão
**Opção A - Imprimir Tudo:**
- Clicar em "🖨 Imprimir Todas as Etiquetas"
- Confirmar no diálogo (mostra quantidade de etiquetas e blocos)
- Sistema imprime sequencialmente todos os blocos

**Opção B - Impressão Individual:**
- Ainda usa os botões de andar/palete individuais (MODELO 01 e 02)

## Exemplo Prático

### Cenário: Prédio com 5 andares e 7 posições por andar

**Estrutura:**
```
3º Andar: Pos 01, 02, 03, 04, 05, 06, 07
2º Andar: Pos 01, 02, 03, 04, 05
1º Andar: Pos 01, 02, 03, 04, 05, 06, 07
Térreo:   Pos 01, 02, 03, 04, 05
-1:       Pos 01, 02, 03
```

**Etiquetas Geradas (MODELO 03):**

```
Etiqueta 1: Posição 01
├─ 3º Andar - COT001-A-03-01
├─ 2º Andar - COT001-A-02-01
├─ 1º Andar - COT001-A-01-01
├─ Térreo   - COT001-A-00-01
└─ -1       - COT001-A-N1-01

Etiqueta 2: Posição 02
├─ 3º Andar - COT001-A-03-02
├─ 2º Andar - COT001-A-02-02
├─ 1º Andar - COT001-A-01-02
├─ Térreo   - COT001-A-00-02
└─ -1       - COT001-A-N1-02

Etiqueta 3: Posição 03
├─ 3º Andar - COT001-A-03-03
├─ 2º Andar - COT001-A-02-03
├─ 1º Andar - COT001-A-01-03
├─ Térreo   - COT001-A-00-03
└─ -1       - COT001-A-N1-03

Etiqueta 4: Posição 04
├─ 3º Andar - COT001-A-03-04
├─ 2º Andar - COT001-A-02-04
├─ 1º Andar - COT001-A-01-04
└─ Térreo   - COT001-A-00-04

Etiqueta 5: Posição 05
├─ 3º Andar - COT001-A-03-05
├─ 2º Andar - COT001-A-02-05
├─ 1º Andar - COT001-A-01-05
└─ Térreo   - COT001-A-00-05

Etiqueta 6: Posição 06
├─ 3º Andar - COT001-A-03-06
└─ 1º Andar - COT001-A-01-06

Etiqueta 7: Posição 07
├─ 3º Andar - COT001-A-03-07
└─ 1º Andar - COT001-A-01-07
```

**Total: 7 etiquetas** (uma por posição vertical)

## Comparação com MODELO 01

| Aspecto | MODELO 01 (Por Andar) | MODELO 03 (Por Bloco) |
|---------|----------------------|----------------------|
| **Organização** | Todas posições de um andar | Mesma posição de todos andares |
| **Ordem** | Andar por andar | Posição por posição |
| **Etiquetas (5 andares, 7 pos)** | 5 etiquetas | 7 etiquetas |
| **QR por etiqueta** | Até 6 | Até 6 |
| **Uso ideal** | Organização por andar | Organização vertical/torre |
| **Orientação** | Horizontal | Horizontal |
| **Grid** | 2x3 | 2x3 |

## Arquivos Modificados

1. ✅ `src/printer/zpl_generator.py`
   - Adicionado `build_block_addresses_zpl()`

2. ✅ `src/address_manager.py`
   - Adicionado `organize_addresses_by_block()`

3. ✅ `src/ui/address_labels_window.py`
   - Adicionado `organized_blocks` (variável de instância)
   - Adicionado `mode_var` (radio button state)
   - Adicionado `mode_frame` (radio buttons UI)
   - Adicionado `mode_description_label` (texto explicativo)
   - Adicionado `_on_mode_changed()` (callback)
   - Adicionado `_update_mode_description()` (atualiza texto)
   - Modificado `_load_warehouse_structure()` (carrega ambos os modos)
   - Adicionado `_print_all()` (dispatcher de modo)
   - Adicionado `_print_all_blocks()` (impressão MODELO 03)
   - Modificado botão "Imprimir Todas as Etiquetas" (chama `_print_all()`)

## Teste

### Teste Manual

1. Executar aplicação:
   ```bash
   python src/main.py
   ```

2. Fazer login e abrir "Etiquetas de Endereçamento"

3. Selecionar modo "Por Bloco"

4. Selecionar galpão e impressora

5. Clicar "Imprimir Todas as Etiquetas"

6. Verificar:
   - ✅ Etiquetas impressas por posição vertical
   - ✅ Ordem do andar mais alto ao mais baixo
   - ✅ Grid 2x3 correto
   - ✅ QR codes legíveis
   - ✅ Textos formatados corretamente

### Teste de Validação ZPL

Gerar ZPL de teste:
```python
from src.printer.zpl_generator import ZplGenerator

gen = ZplGenerator()
addresses = [
    {'full_address': 'COT001-A-03-01', 'floor_name': '3º Andar'},
    {'full_address': 'COT001-A-02-01', 'floor_name': '2º Andar'},
    {'full_address': 'COT001-A-01-01', 'floor_name': '1º Andar'},
    {'full_address': 'COT001-A-00-01', 'floor_name': 'Térreo'},
]

zpl = gen.build_block_addresses_zpl('COT001', 'Cotia 1', 'Prédio A', addresses)
print(zpl)
```

Visualizar em: http://labelary.com/viewer.html

## Status

✅ **MODELO 03 IMPLEMENTADO E PRONTO PARA USO**

- ZPL Generator: ✅ Completo
- Address Manager: ✅ Completo  
- UI: ✅ Completo
- Testes: ⏳ Pendente validação em produção
