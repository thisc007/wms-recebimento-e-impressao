-- ============================================
-- FIX: Aumentar tamanho do campo movement_type
-- Tabela: cargo_movements
-- Problema: Valor 'PHYSICAL_RECEIPT' sendo truncado
-- ============================================

-- 1. Verificar estrutura atual
DESCRIBE cargo_movements;

-- 2. Verificar tipos de movimento existentes
SELECT DISTINCT movement_type, LENGTH(movement_type) as tamanho 
FROM cargo_movements 
ORDER BY tamanho DESC;

-- 3. APLICAR CORREÇÃO
-- Aumentar o tamanho da coluna movement_type de VARCHAR(20) para VARCHAR(50)
ALTER TABLE cargo_movements 
MODIFY COLUMN movement_type VARCHAR(50) NOT NULL;

-- 4. Verificar se foi aplicado
DESCRIBE cargo_movements;

-- 5. OPCIONAL: Se o campo for ENUM, use este comando ao invés do ALTER acima:
-- ALTER TABLE cargo_movements 
-- MODIFY COLUMN movement_type VARCHAR(50) NOT NULL;

-- 6. Testar inserção
-- INSERT INTO cargo_movements (cargo_id, movement_type, handled_by, movement_at, created_at, updated_at)
-- VALUES (999, 'PHYSICAL_RECEIPT', 1, NOW(), NOW(), NOW());
-- SELECT * FROM cargo_movements WHERE cargo_id = 999;
-- DELETE FROM cargo_movements WHERE cargo_id = 999;

-- ============================================
-- RESULTADO ESPERADO:
-- movement_type: VARCHAR(50) NOT NULL
-- ============================================
