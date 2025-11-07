# 📐 GUIA DE AJUSTE DE POSIÇÕES - ETIQUETA ZEBRA

## 🎯 Layout Atual da Etiqueta (90mm x 70mm, 203 DPI)

```
┌─────────────────────────────────────────────────────────────────┐
│ 0,0                                                             │
│                                                                 │
│     │                                                           │
│     │ Barcode                    X=550, Y=250 → *PRIORITARIA*  │
│     │ Vertical                   X=550, Y=310 → MAN.ESPECIAL   │
│     │ (Rotação R)               X=550, Y=370 → Val:31/12/2025  │
│     │                            X=550, Y=430 → Instruções...   │
│     │                                                           │
│     │                                                           │
│     │                                                           │
│                                                                 │
│              X=210, Y=250                                       │
│              010000031  (texto do código)                       │
│                                                                 │
│              X=200, Y=400                                       │
│              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  (barcode horizontal)           │
│              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                  │
│              010000031                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
     Largura: 719 dots (90mm)
     Altura: 559 dots (70mm)
```

## 🔧 Parâmetros Atuais (linha 180-184)

```python
# Posições para indicadores (canto superior direito)
indicator_x = 550  # Próximo à borda direita
indicator_y = 250  # Topo
line_height = 60   # Espaçamento entre linhas
```

## 🎨 Opções de Ajuste

### **Opção 1: Mover para BAIXO (abaixo do barcode horizontal)**
```python
indicator_x = 200  # Alinhado com barcode horizontal
indicator_y = 540  # Abaixo do barcode (ajustar conforme necessário)
line_height = 45   # Espaçamento menor
```

### **Opção 2: Mover para ESQUERDA (não sobrepor)**
```python
indicator_x = 450  # Mais à esquerda
indicator_y = 250  # Manter no topo
line_height = 60   # Manter espaçamento
```

### **Opção 3: Empilhar na PARTE INFERIOR**
```python
indicator_x = 100  # Lado esquerdo
indicator_y = 540  # Parte inferior
line_height = -50  # Empilhar para CIMA (negativo)
```

### **Opção 4: Entre os BARCODES (área central)**
```python
indicator_x = 200  # Centro
indicator_y = 300  # Entre texto e barcode horizontal
line_height = 50   # Compacto
```

## 📏 Sistema de Coordenadas ZPL

```
(0,0) ────────────► X (horizontal)
  │
  │     ┌─────────────────┐
  │     │    Etiqueta     │
  │     │                 │
  ▼     │                 │
  Y     └─────────────────┘
(vertical)

• Origem: Canto superior esquerdo (0,0)
• X aumenta para DIREITA
• Y aumenta para BAIXO
• Unidade: DOTS (203 DPI = 8 dots por mm)
```

## 🔢 Conversões Úteis

### Milímetros → Dots (203 DPI):
```
1mm = 8 dots
5mm = 40 dots
10mm = 80 dots
20mm = 160 dots
```

### Largura da etiqueta: 90mm = 719 dots
### Altura da etiqueta: 70mm = 559 dots

## 🛠️ Como Ajustar

### **Arquivo:** `src/printer/zpl_generator.py`
### **Método:** `_add_special_indicators()` (linha ~180)

```python
def _add_special_indicators(self, cargo_data: Dict[str, Any]) -> str:
    indicators_zpl = ""
    
    # ⚙️ AJUSTE AQUI ⚙️
    indicator_x = 550  # ← Altere este valor (horizontal)
    indicator_y = 250  # ← Altere este valor (vertical)
    line_height = 60   # ← Altere o espaçamento entre linhas
    current_y = indicator_y
    
    # ... resto do código ...
```

## 📋 Elementos Existentes (NÃO ALTERAR)

### Barcode Vertical (esquerda):
```python
x = 42
y = 250
orientation = 'R'  # Rotação 90° (vertical)
height = 120
```

### Texto do Código (centro):
```python
x = 210
y = 250
font = 'A'
height = 30
width = 30
```

### Barcode Horizontal (centro-baixo):
```python
x = 200
y = 400
orientation = 'N'  # Normal (horizontal)
height = 120
```

## 💡 Recomendações

### **Evite Sobreposição:**
1. Barcode vertical está em `x=42` até ~`x=162` (largura ~120)
2. Texto está em `y=250`, ocupa ~30 de altura
3. Barcode horizontal está em `y=400`, ocupa ~120 de altura

### **Áreas Seguras para Indicadores:**

#### ✅ **Opção A: Lado direito (atual, ajustar X)**
- `x = 450-550` (longe do barcode vertical)
- `y = 250-530` (flexível)

#### ✅ **Opção B: Abaixo do barcode horizontal**
- `x = 200-600` (toda largura disponível)
- `y = 540+` (após barcode)

#### ✅ **Opção C: Entre barcodes**
- `x = 200-600`
- `y = 300-380` (entre texto e barcode horizontal)

## 🧪 Testar Alterações

Após modificar os valores:

```bash
# 1. Gerar novos exemplos
python test_special_indicators.py

# 2. Ver arquivos gerados em:
out/test_indicators/etiqueta_completa.zpl

# 3. Testar no sistema
python src/main_launcher.py --gui-debug
```

## 📸 Visualizar ZPL Online

Use: http://labelary.com/viewer.html
- Cole o código ZPL
- Ajuste DPI para 203
- Veja preview da etiqueta

## ⚡ Ajuste Rápido Recomendado

Se estiver encavalando com o texto ou barcode:

```python
# MOVER PARA BAIXO E MAIS À ESQUERDA
indicator_x = 400  # Mais à esquerda (era 550)
indicator_y = 320  # Mais para baixo (era 250)
line_height = 50   # Mais compacto (era 60)
```

Ou para área totalmente livre:

```python
# ÁREA INFERIOR LIVRE
indicator_x = 100   # Lado esquerdo
indicator_y = 540   # Parte inferior
line_height = 40    # Compacto
```
