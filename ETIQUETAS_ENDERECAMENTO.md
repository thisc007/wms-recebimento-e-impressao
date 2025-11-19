# Sistema de Etiquetas de Endereçamento

## 📋 Resumo da Implementação

Foi criado um sistema completo para impressão de etiquetas de endereçamento de warehouse, com duas modalidades de etiquetas conforme especificado.

---

## 🏗️ Arquivos Criados/Modificados

### **Novos Arquivos:**

1. **`src/address_manager.py`**
   - Gerenciador de endereços de warehouse
   - Processa dados da API e organiza paletes por andar
   - Métodos para obter prédios, andares e paletes
   - Organiza dados para impressão em lote

2. **`src/ui/address_labels_window.py`**
   - Interface gráfica para impressão de etiquetas
   - Seleção de galpão e impressora
   - Botão "Imprimir Tudo" para impressão por andar
   - Botões individuais para cada palete
   - Scrollbar para grande quantidade de endereços

3. **`test_address_labels.py`**
   - Script de teste para validar funcionalidades
   - Gera arquivos ZPL de exemplo
   - Testa AddressManager e ZplGenerator

### **Arquivos Modificados:**

1. **`src/printer/zpl_generator.py`**
   - Adicionado método `build_floor_addresses_zpl()` para MODELO 01
   - Adicionado método `build_single_address_zpl()` para MODELO 02

2. **`src/ui/gui.py`**
   - Adicionado botão "📍 Etiquetas de Endereçamento" no menu principal
   - Adicionado método `open_address_labels()` para abrir a nova janela

---

## 🏷️ Modelos de Etiquetas

### **MODELO 01 - Etiquetas por Andar**
- **Formato:** 150mm x 100mm
- **Layout:** Grid 2x3 (até 6 QR codes por etiqueta)
- **Conteúdo:**
  - Título: Galpão + Prédio + Andar
  - 6 QR codes com endereços completos
  - Texto do endereço abaixo de cada QR code
- **Uso:** Impressão em lote de todos os endereços de um andar

### **MODELO 02 - Etiqueta Individual Vertical**
- **Formato:** 150mm x 100mm (vertical)
- **Layout:** QR code grande à esquerda, informações à direita
- **Conteúdo:**
  - QR code grande com endereço
  - Endereço completo (grande)
  - Nome do palete
  - Prédio
  - Andar
- **Uso:** Impressão individual de um palete específico

---

## 🎯 Funcionalidades

### **Interface Principal:**
1. **Seleção de Galpão:** ComboBox com lista de galpões da API
2. **Seleção de Impressora:** ComboBox com impressoras disponíveis
3. **Botão "Imprimir Tudo":** Imprime todas as etiquetas por andar (MODELO 01)
4. **Lista de Endereços:** Organizada por prédio e andar
   - Botão para imprimir andar completo
   - Grid de botões individuais para cada palete

### **Fluxo de Uso:**
1. Usuário seleciona galpão
2. Sistema carrega estrutura completa (prédios/andares/paletes)
3. Exibe todos os endereços organizados
4. Usuário pode:
   - Imprimir todas as etiquetas de uma vez
   - Imprimir etiquetas de um andar específico
   - Imprimir etiqueta individual de um palete

---

## 📡 Integração com API

### **Endpoint Utilizado:**
```
GET /api/warehouses/{id}
```

### **Estrutura de Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "code": "COT001",
    "name": "Cotia 1",
    "buildings": [
      {
        "id": 13,
        "code": "A",
        "name": "Prédio A",
        "floors": [
          {
            "id": 61,
            "code": "01",
            "name": "Térreo",
            "pallets": [
              {
                "id": 611,
                "full_address": "COT001-A-01-01-01",
                "name": "Palete 01"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 🧪 Como Testar

### **1. Teste dos Geradores ZPL:**
```bash
cd c:\xampp\htdocs\wms-recebimento-e-impressao\printing-service
python test_address_labels.py
```

Este teste irá:
- Validar geração de ZPL para ambos os modelos
- Salvar arquivos `test_modelo_01.zpl` e `test_modelo_02.zpl`
- Mostrar informações detalhadas no console

### **2. Visualizar ZPL Gerado:**
Acesse http://labelary.com/viewer.html e cole o conteúdo dos arquivos `.zpl` gerados.

### **3. Teste na Interface Gráfica:**
```bash
python src/main_launcher.py --gui-simple
```

1. Faça login
2. Clique em "📍 Etiquetas de Endereçamento"
3. Selecione um galpão e impressora
4. Teste as funcionalidades de impressão

---

## 🎨 Layout das Etiquetas

### **MODELO 01 (Por Andar):**
```
------------------------------------------------------
| Galpão Cotia (COT01) - Prédio A - Andar Térreo     |
|                                                    |
|  [QR CODE]              [QR CODE]                  |
| COT001-A-01-01        COT001-A-01-02               |
|                                                    |
|  [QR CODE]              [QR CODE]                  |
| COT001-A-01-03        COT001-A-01-04               |
|                                                    |
|  [QR CODE]              [QR CODE]                  |
| COT001-A-01-05        COT001-A-01-06               |
------------------------------------------------------
```

### **MODELO 02 (Individual - Vertical):**
```
--------------------------
|                        |
| [QR CODE]  COT001-A-01-01 |
| GRANDE     (grande)    |
|                        |
|            Nome: Palete 03 |
|            Prédio: A   |
|            Andar: Térreo |
|                        |
--------------------------
```

---

## 🔧 Configuração Técnica

### **Dimensões ZPL:**
- Etiqueta: 150mm x 100mm
- DPI: 203
- Width: ~1181 dots
- Height: ~787 dots

### **QR Codes:**
- MODELO 01: Magnification 6
- MODELO 02: Magnification 10
- Formato: QR Code Model 2
- Encoding: QA (byte mode)

---

## 📝 Notas Importantes

1. **Múltiplas Etiquetas:** Se um andar tiver mais de 6 paletes, serão geradas múltiplas etiquetas automaticamente (grupos de 6).

2. **Scrollbar:** A lista de endereços possui scrollbar para suportar grande quantidade de paletes.

3. **Validação:** O sistema valida se galpão e impressora foram selecionados antes de imprimir.

4. **Logs:** Todas as ações são registradas no sistema de logs.

5. **API Client:** Utiliza o `APIClient` existente com autenticação por token.

---

## 🚀 Próximos Passos (Opcional)

- [ ] Adicionar filtro por prédio/andar na interface
- [ ] Exportar ZPL para arquivo
- [ ] Preview da etiqueta antes de imprimir
- [ ] Histórico de impressões
- [ ] Impressão em PDF para arquivamento

---

## ✅ Checklist de Implementação

- [x] Gerador ZPL para MODELO 01 (6 QR codes)
- [x] Gerador ZPL para MODELO 02 (individual vertical)
- [x] AddressManager para processar dados da API
- [x] Interface gráfica com seleção de galpão/impressora
- [x] Botão "Imprimir Tudo"
- [x] Botões individuais para cada palete
- [x] Scrollbar para lista de endereços
- [x] Integração com menu principal
- [x] Script de teste
- [x] Documentação

---

**Sistema pronto para uso! 🎉**
