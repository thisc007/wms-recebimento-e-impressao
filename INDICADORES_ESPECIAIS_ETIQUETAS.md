# 📋 INDICADORES ESPECIAIS NAS ETIQUETAS

## ✅ Funcionalidade Implementada

As etiquetas agora exibem **indicadores visuais** automaticamente quando a carga possui características especiais.

## 🎯 Indicadores Disponíveis

### 1. ⚠️ **CARGA PRIORITÁRIA**
- **Campo:** `is_priority = true`
- **Exibição:** `*PRIORITARIA*`
- **Fonte:** 40x40 (destaque máximo)
- **Posição:** Canto superior direito

### 2. 🔶 **MANUSEIO ESPECIAL**
- **Campo:** `requires_special_handling = true`
- **Exibição:** `MAN.ESPECIAL`
- **Fonte:** 35x35
- **Posição:** Abaixo da prioridade (se houver)

### 3. 📅 **DATA DE VALIDADE**
- **Campo:** `expiration_date` (formato ISO ou brasileiro)
- **Exibição:** `Val:DD/MM/YYYY`
- **Fonte:** 30x30
- **Exemplo:** `Val:31/12/2025`

### 4. 📝 **INSTRUÇÕES DE MANUSEIO**
- **Campo:** `handling_instructions`
- **Exibição:** Truncado em 15 caracteres + "..."
- **Fonte:** 25x25
- **Exemplo:** `Manter refriger...`

## 📐 Layout da Etiqueta

```
╔════════════════════════════════════════════╗
║  |         010000031      *PRIORITARIA*   ║
║  |                        MAN.ESPECIAL    ║
║  |                        Val:31/12/2025  ║
║  |                        Manter refri... ║
║  |                                        ║
║  |                                        ║
║  |                                        ║
║  |         [BARCODE]                      ║
║  |         010000031                      ║
║  |                                        ║
╚════════════════════════════════════════════╝
```

## 🔧 Implementação Técnica

### **Arquivos Modificados:**

#### 1. `src/printer/zpl_generator.py`
```python
def build_zpl(self, code: str, cargo_data: Dict[str, Any] = None) -> str:
    # ... código existente ...
    
    # Adicionar indicadores especiais se cargo_data fornecido
    if cargo_data:
        zpl += self._add_special_indicators(cargo_data)
    
    return zpl

def _add_special_indicators(self, cargo_data: Dict[str, Any]) -> str:
    """Gera código ZPL para indicadores especiais"""
    # Posições no canto superior direito
    indicator_x = 550
    indicator_y = 250
    line_height = 60
    
    # Adiciona cada indicador sequencialmente
```

#### 2. `src/ui/receive_load_window.py`
```python
def print_label_after_receive(self, cargo_code: str):
    # Preparar dados da carga atual
    cargo_data = {
        'is_priority': self.current_cargo.get('is_priority', False),
        'requires_special_handling': self.current_cargo.get('requires_special_handling', False),
        'expiration_date': self.current_cargo.get('expiration_date'),
        'handling_instructions': self.current_cargo.get('handling_instructions')
    }
    
    # Gerar ZPL com indicadores
    zpl = self.zpl_generator.build_zpl(cargo_code, cargo_data)
```

#### 3. `src/ui/reprint_window.py`
```python
def reprint_label(self):
    # Mesma lógica: passa cargo_data para build_zpl()
    zpl = self.zpl_generator.build_zpl(code_to_print, cargo_data)
```

## 📊 Exemplo de Resposta da API

```json
{
  "data": {
    "code": "010000031",
    "is_priority": true,
    "requires_special_handling": true,
    "expiration_date": "2025-12-31T23:59:59.000000Z",
    "handling_instructions": "Manter refrigerado entre 2°C e 8°C"
  }
}
```

## 🎨 Exemplo de Código ZPL Gerado

### Etiqueta com TODOS os indicadores:
```zpl
^XA
^CI28
^PW719
^LL559
... (configurações básicas) ...

^FO42,250
^BY2,2
^BCR,120,N,N,N
^FD010000031^FS

^FO210,250
^AA,30,30
^FD010000031^FS

^FO200,400
^BY4,2
^BCN,120,N,N,N
^FD010000031^FS

^FO550,250          ← Indicador 1
^A0N,40,40
^FD*PRIORITARIA*^FS

^FO550,310          ← Indicador 2
^A0N,35,35
^FDMAN.ESPECIAL^FS

^FO550,370          ← Indicador 3
^A0N,30,30
^FDVal:31/12/2025^FS

^FO550,430          ← Indicador 4
^A0N,25,25
^FDManter refriger...^FS
^XZ
```

## 🧪 Teste

Execute o script de teste:
```bash
python test_special_indicators.py
```

Isso gera 5 exemplos em `out/test_indicators/`:
- ✅ `etiqueta_simples.zpl` - Sem indicadores
- ✅ `etiqueta_prioritaria.zpl` - Com prioridade
- ✅ `etiqueta_manuseio_especial.zpl` - Com manuseio especial
- ✅ `etiqueta_validade.zpl` - Com validade
- ✅ `etiqueta_completa.zpl` - Com TODOS os indicadores

## 📝 Notas Importantes

1. **Retrocompatível:** Se `cargo_data` não for passado ou for `None`, a etiqueta é gerada normalmente sem indicadores

2. **Posicionamento:** Os indicadores são empilhados verticalmente no canto superior direito

3. **Truncamento:** Instruções longas são truncadas em 15 caracteres + "..."

4. **Formato de Data:** Aceita tanto ISO (`2025-12-31T23:59:59.000000Z`) quanto brasileiro (`31/12/2025`)

5. **Logs:** O sistema registra quais indicadores foram adicionados para debug

## ✨ Benefícios

- ✅ **Identificação Visual Imediata** de cargas especiais
- ✅ **Reduz Erros** de manuseio
- ✅ **Alertas de Validade** visíveis na etiqueta
- ✅ **Instruções de Manuseio** sempre à vista
- ✅ **Priorização** visual no estoque

## 🚀 Uso no Sistema

A funcionalidade é **automática**:

1. **No Recebimento:** Ao aceitar uma carga, se ela tiver características especiais, a etiqueta impressa incluirá os indicadores

2. **Na Reimpressão:** Ao reimprimir uma etiqueta, o sistema busca os dados atuais da carga na API e adiciona os indicadores se aplicável

**Nenhuma ação adicional é necessária do operador!** 🎉
