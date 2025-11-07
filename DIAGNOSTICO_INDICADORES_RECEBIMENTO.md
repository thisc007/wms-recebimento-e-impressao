# 🔍 Diagnóstico: Indicadores Especiais não Aparecem na Impressão

## 📋 Problema Relatado

Quando faz o recebimento físico de uma carga, a etiqueta **NÃO está imprimindo** os indicadores especiais (prioridade, manuseio especial, data de validade, instruções), mesmo que a carga tenha essas informações.

Na **reimpressão** funciona, mas no **recebimento** não.

---

## 🔎 Análise do Código

### ✅ Código de Impressão está CORRETO

O arquivo `receive_load_window.py` **JÁ ESTÁ** preparado para enviar os indicadores:

```python
# Linhas 676-686 do receive_load_window.py
cargo_data = None
if self.current_cargo:
    cargo_data = {
        'is_priority': self.current_cargo.get('is_priority', False),
        'requires_special_handling': self.current_cargo.get('requires_special_handling', False),
        'expiration_date': self.current_cargo.get('expiration_date'),
        'handling_instructions': self.current_cargo.get('handling_instructions')
    }
    log_info(f"Indicadores especiais: priority={cargo_data['is_priority']}, "
            f"special_handling={cargo_data['requires_special_handling']}, "
            f"expiration={cargo_data['expiration_date']}")

zpl = self.zpl_generator.build_zpl(cargo_code, cargo_data)
```

### ❓ Suspeita: API não retorna os campos

O problema **muito provavelmente** é que a **API Laravel não está retornando** esses campos quando busca as cargas pendentes de recebimento.

Quando você chama `/cargos/pending-physical-receipt`, a API está retornando algo como:

```json
{
  "id": 123,
  "code": "010000031",
  "status": "RECEIVED",
  "customer": {...},
  "cargo_type": {...}
  // ❌ FALTAM: is_priority, requires_special_handling, expiration_date, handling_instructions
}
```

---

## 🧪 Como Verificar

Execute o script de teste que criei:

```bash
python test_cargo_fields.py
```

Este script vai:
1. Fazer login na API
2. Buscar cargas pendentes
3. **Verificar se os campos de indicadores especiais estão presentes**
4. Mostrar exatamente quais campos estão faltando

---

## 🛠️ Solução

### Opção 1: Atualizar o Backend Laravel (RECOMENDADO)

No controller que retorna as cargas pendentes (provavelmente `CargoController.php`), você precisa garantir que os campos sejam retornados:

```php
// Exemplo no Laravel
public function pendingPhysicalReceipt(Request $request)
{
    $cargos = Cargo::with(['customer', 'cargo_type'])
        ->select([
            'id',
            'code',
            'status',
            'customer_id',
            'cargo_type_id',
            'is_priority',                    // ← ADICIONAR
            'requires_special_handling',       // ← ADICIONAR
            'expiration_date',                // ← ADICIONAR
            'handling_instructions',          // ← ADICIONAR
            'weight',
            'volume',
            'received_at',
            // ... outros campos
        ])
        ->where('status', 'RECEIVED')  // ou outro critério
        ->paginate($request->input('per_page', 15));

    return response()->json([
        'success' => true,
        'data' => $cargos->items(),
        'pagination' => [...]
    ]);
}
```

**Ou use um Resource para ter mais controle:**

```php
// App/Http/Resources/CargoResource.php
public function toArray($request)
{
    return [
        'id' => $this->id,
        'code' => $this->code,
        'status' => $this->status,
        'customer' => new CustomerResource($this->whenLoaded('customer')),
        'cargo_type' => new CargoTypeResource($this->whenLoaded('cargo_type')),
        
        // Indicadores especiais
        'is_priority' => (bool) $this->is_priority,
        'requires_special_handling' => (bool) $this->requires_special_handling,
        'expiration_date' => $this->expiration_date,
        'handling_instructions' => $this->handling_instructions,
        
        // ... outros campos
    ];
}
```

### Opção 2: Workaround no Frontend (TEMPORÁRIO)

Se não puder alterar o backend imediatamente, você pode fazer uma **segunda chamada** para buscar os detalhes completos da carga:

```python
# No receive_load_window.py, após buscar a carga
def search_cargo(self):
    # ... código existente ...
    
    if cargas:
        self.current_cargo = cargas[0]
        
        # WORKAROUND: Buscar detalhes completos da carga
        cargo_id = self.current_cargo['id']
        detailed_response = self.api_client.get(
            f'/cargos/{cargo_id}',  # Endpoint de detalhes
            headers=headers
        )
        
        if detailed_response.status_code == 200:
            detailed_result = detailed_response.json()
            if detailed_result.get('success'):
                # Substituir com dados completos
                self.current_cargo = detailed_result.get('data', {})
```

**⚠️ PROBLEMA:** Isso faz **2 chamadas à API** por carga, o que é ineficiente.

---

## 📊 Checklist de Verificação

Use este checklist para diagnosticar:

- [ ] Executei `python test_cargo_fields.py` e verifiquei os resultados
- [ ] Campos `is_priority`, `requires_special_handling`, `expiration_date`, `handling_instructions` **estão presentes** na resposta da API?
  - [ ] ✅ SIM → O problema está em outro lugar (verificar logs de impressão)
  - [ ] ❌ NÃO → Precisa atualizar o backend para retornar esses campos

- [ ] Verifiquei os logs durante o recebimento (`logs/` ou console)
  - [ ] O log mostra: `Indicadores especiais: priority=True, special_handling=True...`?
  - [ ] Os valores estão `False` ou `None` quando deveriam ser `True`?

- [ ] Comparei com a reimpressão (que funciona)
  - [ ] Na reimpressão, esses campos aparecem?
  - [ ] Na reimpressão, uso endpoint diferente (`/cargos/code/{code}` ou `/cargos/{id}`)?

---

## 🎯 Solução Definitiva

**Backend (Laravel):**

1. Adicionar os 4 campos ao `SELECT` ou `Resource` do endpoint `/cargos/pending-physical-receipt`
2. Garantir que a tabela `cargos` tem esses campos (migration):

```php
// Migration para adicionar campos se não existem
Schema::table('cargos', function (Blueprint $table) {
    $table->boolean('is_priority')->default(false)->after('status');
    $table->boolean('requires_special_handling')->default(false)->after('is_priority');
    $table->date('expiration_date')->nullable()->after('requires_special_handling');
    $table->text('handling_instructions')->nullable()->after('expiration_date');
});
```

3. Testar endpoint manualmente:
```bash
curl -H "Authorization: Bearer SEU_TOKEN" \
     http://localhost:8000/api/cargos/pending-physical-receipt
```

**Frontend (Python):**

Não precisa alterar nada! O código já está preparado. 🎉

---

## 📝 Logs Úteis para Debug

Ao fazer recebimento, verifique nos logs:

```
INFO: Indicadores especiais: priority=False, special_handling=False, expiration=None
```

Se todos estão `False/None`, significa que a API não está retornando os valores.

Se aparecerem valores `True` mas não imprimem, o problema pode ser:
- Impressora não suporta os caracteres (já corrigimos, agora usa ASCII)
- Posicionamento sobrepondo barcodes (já ajustamos)
- Gerador ZPL com bug (improvável, testamos bastante)

---

## ✅ Teste Final

Após corrigir o backend:

1. Execute `python test_cargo_fields.py` novamente
2. Todos os campos devem aparecer com valores corretos
3. Faça um recebimento real
4. Verifique se a etiqueta imprime com os indicadores

---

**Data:** 06/11/2025
**Arquivo relacionado:** `receive_load_window.py`, linha 676-690
**Scripts de teste:** `test_cargo_fields.py`
