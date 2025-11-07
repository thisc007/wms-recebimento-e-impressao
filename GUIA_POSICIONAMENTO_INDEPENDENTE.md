# 📐 Guia de Posicionamento Independente dos Indicadores

## 🎯 Visão Geral

Cada indicador especial na etiqueta agora possui **4 parâmetros independentes** que você pode ajustar:

1. **`_x`** - Posição horizontal (distância da borda esquerda)
2. **`_y`** - Posição vertical (distância do topo)
3. **`_font_h`** - Altura da fonte
4. **`_font_w`** - Largura da fonte

---

## 📏 Sistema de Coordenadas

### Unidade de Medida: **DOTS**
- A impressora trabalha com **203 DPI** (dots per inch)
- **1 mm = 8 dots** (aproximadamente)
- Área total da etiqueta: **719 x 559 dots** (90mm x 70mm)

### Origem das Coordenadas
```
(0,0) ────────────────────────────► X (719 dots máximo)
  │
  │
  │
  │
  │
  ▼
  Y (559 dots máximo)
```

---

## 🎨 Configuração dos Indicadores

Abra o arquivo: **`src/printer/zpl_generator.py`**

### 🔴 1. Indicador de PRIORIDADE

```python
# 🔴 INDICADOR DE PRIORIDADE (⚠️)
priority_x = 210        # Posição horizontal (em dots)
priority_y = 365        # Posição vertical (em dots)
priority_font_h = 40    # Altura da fonte (em dots)
priority_font_w = 40    # Largura da fonte (em dots)
priority_text = "⚠️ PRIORITARIA"  # Texto do indicador
```

**Como ajustar:**
- **Mover para direita:** Aumentar `priority_x` (ex: 300, 400, 500)
- **Mover para esquerda:** Diminuir `priority_x` (ex: 150, 100, 50)
- **Mover para baixo:** Aumentar `priority_y` (ex: 400, 450, 500)
- **Mover para cima:** Diminuir `priority_y` (ex: 300, 250, 200)
- **Aumentar tamanho:** Aumentar `priority_font_h` e `priority_font_w` (ex: 50, 60)
- **Diminuir tamanho:** Diminuir `priority_font_h` e `priority_font_w` (ex: 30, 25)
- **Mudar texto:** Editar `priority_text` (ex: "⚠️ URGENTE", "P", "*PRIOR*")

---

### 🟠 2. Indicador de MANUSEIO ESPECIAL

```python
# 🟠 INDICADOR DE MANUSEIO ESPECIAL (🔶)
special_x = 210         # Posição horizontal (em dots)
special_y = 320         # Posição vertical (em dots)
special_font_h = 35     # Altura da fonte (em dots)
special_font_w = 35     # Largura da fonte (em dots)
special_text = "🔶 MAN.ESPECIAL"  # Texto do indicador
```

**Como ajustar:**
- Mesma lógica do indicador de prioridade
- Ajuste `special_x` e `special_y` para posicionar
- Ajuste `special_font_h` e `special_font_w` para redimensionar
- Edite `special_text` para alterar o texto (ex: "! CUIDADO", "FRÁGIL")

---

### 🟡 3. Indicador de DATA DE VALIDADE

```python
# 🟡 INDICADOR DE DATA DE VALIDADE (📅)
expiration_x = 210      # Posição horizontal (em dots)
expiration_y = 275      # Posição vertical (em dots)
expiration_font_h = 30  # Altura da fonte (em dots)
expiration_font_w = 30  # Largura da fonte (em dots)
```

**Como ajustar:**
- Ajuste `expiration_x` e `expiration_y` para posicionar
- Ajuste `expiration_font_h` e `expiration_font_w` para redimensionar
- O texto "Val:DD/MM/YYYY" é gerado automaticamente da data da carga

---

### 🟢 4. Indicador de INSTRUÇÕES

```python
# 🟢 INDICADOR DE INSTRUÇÕES (📋)
instructions_x = 210    # Posição horizontal (em dots)
instructions_y = 230    # Posição vertical (em dots)
instructions_font_h = 25  # Altura da fonte (em dots)
instructions_font_w = 25  # Largura da fonte (em dots)
```

**Como ajustar:**
- Ajuste `instructions_x` e `instructions_y` para posicionar
- Ajuste `instructions_font_h` e `instructions_font_w` para redimensionar
- O texto vem do campo `handling_instructions` da carga (limitado a 30 caracteres)

---

## 🗺️ Áreas Recomendadas na Etiqueta

### Evite sobrepor estas áreas:

#### 📊 Barcode Vertical (esquerda)
- **X:** 10 - 180 dots
- **Y:** 200 - 400 dots

#### 🔢 Número da Carga (centro-superior)
- **X:** 180 - 350 dots
- **Y:** 220 - 280 dots

#### 📊 Barcode Horizontal (inferior)
- **X:** 180 - 650 dots
- **Y:** 380 - 530 dots

### Áreas seguras para indicadores:

#### ✅ Área 1: Superior direita
```python
x = 450 - 650
y = 200 - 300
```

#### ✅ Área 2: Inferior esquerda (padrão atual)
```python
x = 180 - 300
y = 200 - 360
```

#### ✅ Área 3: Centro direita
```python
x = 450 - 650
y = 300 - 400
```

---

## 🔧 Exemplos Práticos

### Exemplo 1: Todos os indicadores à direita (verticalmente empilhados)

```python
# Prioridade - topo
priority_x = 480
priority_y = 200
priority_font_h = 35
priority_font_w = 35

# Manuseio especial - abaixo
special_x = 480
special_y = 250
special_font_h = 30
special_font_w = 30

# Data de validade - abaixo
expiration_x = 480
expiration_y = 295
expiration_font_h = 28
expiration_font_w = 28

# Instruções - abaixo
instructions_x = 480
instructions_y = 335
instructions_font_h = 25
instructions_font_w = 25
```

### Exemplo 2: Indicadores em linha horizontal (acima do barcode horizontal)

```python
# Prioridade - esquerda
priority_x = 180
priority_y = 350
priority_font_h = 30
priority_font_w = 30

# Manuseio especial - centro-esquerda
special_x = 300
special_y = 350
special_font_h = 30
special_font_w = 30

# Data de validade - centro-direita
expiration_x = 420
expiration_y = 350
expiration_font_h = 28
expiration_font_w = 28

# Instruções - direita
instructions_x = 540
instructions_y = 350
instructions_font_h = 25
instructions_font_w = 25
```

### Exemplo 3: Formato compacto (letras pequenas)

```python
# Alterar os textos para versões curtas
priority_text = "P"
special_text = "!"

# E usar fontes menores
priority_x = 160
priority_y = 365
priority_font_h = 25
priority_font_w = 25

special_x = 185
special_y = 365
special_font_h = 25
special_font_w = 25

expiration_x = 210
expiration_y = 365
expiration_font_h = 20
expiration_font_w = 20

instructions_x = 160
instructions_y = 340
instructions_font_h = 18
instructions_font_w = 18
```

---

## 🧪 Como Testar Suas Mudanças

1. **Edite os valores** em `src/printer/zpl_generator.py`

2. **Rode o script de teste:**
   ```bash
   python test_special_indicators.py
   ```

3. **Verifique os arquivos ZPL gerados:**
   - `out/test_indicators/test_1_simple.zpl`
   - `out/test_indicators/test_2_priority.zpl`
   - `out/test_indicators/test_3_special.zpl`
   - `out/test_indicators/test_4_expiration.zpl`
   - `out/test_indicators/test_5_complete.zpl`

4. **Visualize ou imprima** para verificar o posicionamento

5. **Ajuste novamente** se necessário até ficar perfeito

---

## 💡 Dicas de Otimização

### Para evitar sobreposição:
- Mantenha uma distância mínima de **40-50 dots** entre elementos
- Use fontes menores se precisar agrupar muita informação

### Para melhor legibilidade:
- Textos críticos: use fontes **≥ 30 dots**
- Textos secundários: use fontes **20-28 dots**
- Não use fontes **< 18 dots** (difícil de ler)

### Para layout profissional:
- Alinhe indicadores na mesma linha usando o mesmo valor de `y`
- Use valores de `x` múltiplos de 10 para facilitar cálculos
- Agrupe informações relacionadas (ex: todas na mesma região)

---

## 📋 Checklist Rápido

Antes de finalizar seu layout:

- [ ] Testei com todas as combinações de indicadores?
- [ ] Nenhum indicador sobrepõe o barcode vertical?
- [ ] Nenhum indicador sobrepõe o barcode horizontal?
- [ ] Nenhum indicador sobrepõe o número da carga?
- [ ] Todos os textos são legíveis no tamanho escolhido?
- [ ] Imprimi uma etiqueta de teste real?
- [ ] A etiqueta ficou profissional e clara?

---

## 🎓 Conversão Rápida: mm → dots

| Milímetros | Dots (aprox.) |
|------------|---------------|
| 1 mm       | 8 dots        |
| 5 mm       | 40 dots       |
| 10 mm      | 80 dots       |
| 15 mm      | 120 dots      |
| 20 mm      | 160 dots      |
| 25 mm      | 200 dots      |
| 30 mm      | 240 dots      |
| 40 mm      | 320 dots      |
| 50 mm      | 400 dots      |
| 60 mm      | 480 dots      |
| 70 mm      | 560 dots      |
| 80 mm      | 640 dots      |
| 90 mm      | 720 dots      |

**Fórmula:** `dots = mm × 8`

---

## 📞 Suporte

Se tiver dúvidas sobre posicionamento, consulte:
- `GUIA_POSICIONAMENTO_ETIQUETA.md` - Guia visual completo
- `INDICADORES_ESPECIAIS_ETIQUETAS.md` - Funcionalidades dos indicadores

---

**Última atualização:** 05/11/2025
