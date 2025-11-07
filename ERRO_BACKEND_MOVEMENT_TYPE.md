# 🐛 Erro no Backend - movement_type Truncado

## 📋 Descrição do Problema

Ao tentar registrar o recebimento físico de uma carga, ocorre o seguinte erro no banco de dados:

```
SQLSTATE[01000]: Warning: 1265 Data truncated for column 'movement_type' at row 1
```

### SQL Tentado:
```sql
INSERT INTO `cargo_movements` (
    `cargo_id`, 
    `movement_type`,  -- ❌ PROBLEMA AQUI
    `from_address`, 
    `to_address`, 
    `from_area`, 
    `to_area`, 
    `old_status`, 
    `new_status`, 
    `notes`, 
    `metadata`, 
    `handled_by`, 
    `movement_at`, 
    `updated_at`, 
    `created_at`
) VALUES (
    56, 
    PHYSICAL_RECEIPT,  -- ❌ Valor sendo truncado (17 caracteres)
    ...
)
```

## 🔍 Causa Raiz

O campo `movement_type` na tabela `cargo_movements` está definido com um tipo que não comporta o valor `PHYSICAL_RECEIPT` (17 caracteres).

Possíveis causas:
1. Campo definido como `VARCHAR(10)` ou similar (muito pequeno)
2. Campo definido como `ENUM` sem incluir `PHYSICAL_RECEIPT`
3. Campo definido com limite de caracteres insuficiente

## ✅ Solução

### Opção 1: Alterar o Tipo da Coluna (Recomendado)

Se o campo for `VARCHAR`, aumentar o tamanho:

```sql
ALTER TABLE `cargo_movements` 
MODIFY COLUMN `movement_type` VARCHAR(50) NOT NULL;
```

### Opção 2: Se for ENUM, Adicionar o Valor

```sql
ALTER TABLE `cargo_movements` 
MODIFY COLUMN `movement_type` ENUM(
    'RECEIVING',
    'STORING', 
    'PICKING',
    'EXPEDITION',
    'PHYSICAL_RECEIPT',  -- ← Adicionar este valor
    -- ... outros valores existentes
) NOT NULL;
```

### Opção 3: Usar Migration Laravel

Criar uma migration no Laravel:

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::table('cargo_movements', function (Blueprint $table) {
            // Opção A: Se for VARCHAR
            $table->string('movement_type', 50)->change();
            
            // OU
            
            // Opção B: Se for ENUM (altere conforme necessário)
            DB::statement("ALTER TABLE cargo_movements MODIFY COLUMN movement_type VARCHAR(50)");
        });
    }

    public function down()
    {
        Schema::table('cargo_movements', function (Blueprint $table) {
            $table->string('movement_type', 20)->change(); // Valor anterior
        });
    }
};
```

Execute a migration:
```bash
php artisan migrate
```

## 📊 Valores de movement_type Conhecidos

Baseado no erro, os seguintes valores são usados:
- `PHYSICAL_RECEIPT` (17 chars) ← **Causando o erro**
- `RECEIVING` (9 chars)
- `CHECKING` (8 chars)
- `STORAGE` (7 chars)
- `PICKING` (7 chars)
- `EXPEDITION` (10 chars)
- Outros possíveis...

**Recomendação:** Usar `VARCHAR(50)` para suportar valores futuros.

## 🎯 Status

- ❌ **Bloqueador:** O recebimento físico não funciona
- 🔧 **Prioridade:** ALTA - Funcionalidade crítica
- 👨‍💻 **Responsável:** Equipe Backend/DBA
- 📍 **Arquivo afetado:** `cargo_movements` table no banco de dados

## ✔️ Checklist de Verificação Após Correção

- [ ] Executar migration/ALTER TABLE
- [ ] Verificar estrutura da tabela: `DESCRIBE cargo_movements;`
- [ ] Testar recebimento físico via API
- [ ] Testar recebimento físico via sistema Python
- [ ] Verificar outros campos similares que possam ter o mesmo problema

## 📞 Contato

Se precisar de mais informações, verifique os logs em:
- `logs/app.log` (aplicação Python)
- Logs do Laravel
- Logs do MySQL

---

**Data do Erro:** 2025-11-03 17:46:33  
**Carga ID:** 56  
**Ação:** accept  
**Warehouse ID:** 2  
**Area ID:** 2
