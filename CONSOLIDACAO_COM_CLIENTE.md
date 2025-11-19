# Consolidação com Cliente - Implementação Completa

## ✅ Alterações Implementadas

### 1. **Novo Campo no Payload**
```python
payload = {
    'warehouse_id': int(warehouse_id),
    'customer_id': int(customer_id),  # ← ADICIONADO
    'cargo_ids': cargo_ids
}
```

### 2. **Select Box de Clientes na Interface**
- Campo obrigatório entre Galpão e Impressora
- Carrega clientes via endpoint `/api/customers`
- Headers: `Authorization: Bearer {token}` + `Accept: application/json`
- Suporta retorno direto (array) ou dentro de `data`
- Mapeia `name` ou `company_name` para exibição

### 3. **Validação**
- Verifica se cliente foi selecionado
- Valida ID do cliente antes de enviar
- Exibe mensagem de erro se inválido

### 4. **Novo Erro Suportado**
```json
{
  "success": false,
  "message": "Existem cargas que não podem ser consolidadas",
  "invalid_cargos": [
    {
      "cargo_id": 999,
      "cargo_code": "010000999",
      "errors": [
        {
          "type": "cliente_diferente",
          "message": "A carga 010000999 pertence ao cliente 'Cliente A'..."
        }
      ]
    }
  ]
}
```

**Exibição:**
```
📦 Carga: 010000999
   • cliente_diferente: A carga 010000999 pertence ao cliente 'Cliente A'...
```

## 🔄 Fluxo de Consolidação Atualizado

1. Usuário seleciona **Galpão** (obrigatório)
2. Usuário seleciona **Cliente** (obrigatório) ← NOVO
3. Usuário seleciona **Impressora** (obrigatório)
4. Usuário define **Quantidade** de etiquetas
5. Usuário cola/digita **códigos das cargas**
6. Sistema valida **status das cargas** (RECEIVED, CHECKED)
7. Sistema verifica **erros** (não encontradas, status inválido, servidor)
8. Se houver erros MAS cargas válidas → **Pergunta se quer continuar**
9. Envia para API: `POST /api/consolidators` com `warehouse_id`, `customer_id`, `cargo_ids`
10. API valida se todas as cargas são do mesmo cliente
11. Se houver **warnings** (consolidação parcial) → exibe e imprime
12. **Imprime etiqueta** do consolidador com QR Code

## 📋 Erros Tratados

### **Frontend (antes de enviar)**
- ❌ Cargas não encontradas (404)
- ⚠️ Status inválido (não RECEIVED/CHECKED)
- 🔥 Erros de servidor (500, etc.)

### **Backend (resposta da API)**
- 🔴 `galpao_diferente` - Carga pertence a outro galpão
- 🔴 `cliente_diferente` - Carga pertence a outro cliente ← NOVO
- 🔴 `ja_consolidada` - Carga já está em consolidador
- 🔴 Outros erros (formato flexível suportado)

## 🎯 Interface Atualizada

```
┌─────────────────────────────────────────────┐
│  🔗 Consolidação de Cargas                  │
│  Super User | CPF: 123.456.789-01           │
├─────────────────────────────────────────────┤
│ 1. Configuração                             │
│                                             │
│ Galpão:*                                    │
│ [Galpão Osasco 1         ▼]                │
│                                             │
│ Cliente:*                      ← NOVO       │
│ [Cliente XYZ Ltda        ▼]                │
│                                             │
│ Impressora:*                                │
│ [⭐ Zebra (USB)          ▼]                │
│                                             │
│ Qtd Etiquetas:* [1]                         │
├─────────────────────────────────────────────┤
│ 2. Cargas (Cole ou Digite os Códigos)      │
│                                             │
│ ┌─────────────────────────────────────┐    │
│ │ 010000031                           │    │
│ │ 040000029                           │    │
│ │ 050000028                           │    │
│ └─────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│ 📋 Resultado                                │
│ ┌─────────────────────────────────────┐    │
│ │ Pronto para nova consolidação.      │    │
│ └─────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│ [✅ Consolidar e Imprimir] [🧹 Limpar]     │
│                              [❌ Fechar]    │
└─────────────────────────────────────────────┘
```

## 🧪 Teste Sugerido

1. Execute a aplicação: `python src/main_launcher.py --gui-debug`
2. Faça login
3. Clique em "🧩 Consolidação"
4. Verifique se os 3 select boxes aparecem:
   - ✅ Galpão
   - ✅ Cliente ← NOVO
   - ✅ Impressora
5. Teste consolidação com cargas de clientes diferentes
6. Verifique se o erro `cliente_diferente` é exibido corretamente

## 📝 Logs Esperados

```
2025-11-14 XX:XX:XX - INFO - Carregados 2 galpões para consolidação
2025-11-14 XX:XX:XX - INFO - Carregados X clientes para consolidação  ← NOVO
2025-11-14 XX:XX:XX - INFO - Busca carga 010000031: ID=56, status=RECEIVED
2025-11-14 XX:XX:XX - INFO -   ✓ Carga 010000031 apta para consolidação
2025-11-14 XX:XX:XX - INFO - Criando consolidador: 3 cargas no galpão 1 para cliente 5  ← NOVO
```

## ✅ Checklist de Implementação

- [x] Adicionar atributos `self.customers` e `self.customer_dict`
- [x] Criar método `load_customers()` com endpoint `/api/customers`
- [x] Adicionar select box de clientes na interface (entre galpão e impressora)
- [x] Validar seleção de cliente antes de consolidar
- [x] Incluir `customer_id` no payload para API
- [x] Atualizar mensagem de processamento com nome do cliente
- [x] Suportar erro `cliente_diferente` no tratamento de invalid_cargos
- [x] Testar sintaxe e imports

## 🚀 Pronto para Uso!

O sistema agora está completo para consolidação com validação de cliente.
