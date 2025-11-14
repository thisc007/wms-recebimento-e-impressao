# Tela de Consolidação Simplificada

## Mudanças Implementadas

### 1. **Interface Redesenhada**
- Removida listagem/consulta de consolidadores existentes (consulta será feita no sistema PHP)
- Foco exclusivo em **criar consolidadores** e **imprimir etiquetas**
- Layout limpo e direto ao ponto

### 2. **Configuração (Setup)**
- **Galpão**: Select box (combobox) com lista de galpões disponíveis
- **Impressora**: Select box com impressoras configuradas
- **Quantidade**: Campo numérico para quantidade de etiquetas (padrão: 1)

### 3. **Entrada de Cargas**
- Caixa de texto grande para colar ou digitar códigos de cargas
- **Separadores aceitos**: Enter (quebra de linha), vírgula, ponto-e-vírgula, espaços
- Permite colar lista de códigos diretamente do sistema ou planilha

### 4. **Fluxo de Consolidação**
1. Usuário seleciona **Galpão** e **Impressora**
2. Cola ou digita **códigos das cargas** no campo de texto
3. Define **quantidade de etiquetas**
4. Clica em **"Consolidar e Imprimir"**
5. Sistema:
   - Busca os `cargo_ids` pelos códigos informados
   - Valida se as cargas existem e estão disponíveis
   - Cria o consolidador via API (`POST /api/consolidators`)
   - Imprime as etiquetas automaticamente
   - Exibe resultado (sucesso ou erros detalhados)

### 5. **Tratamento de Erros Detalhado**
A API pode retornar erros específicos quando cargas não podem ser consolidadas. Exemplo:

```json
{
  "success": false,
  "message": "Existem cargas que não podem ser consolidadas",
  "errors": [
    {
      "cargo_id": 123,
      "cargo_code": "010000123",
      "error": "galpao_diferente",
      "message": "A carga 010000123 pertence ao galpão 'Galpão Sul'. Para consolidar no galpão 'Galpão Norte', faça a transferência da carga e use o menu 'Reconsolidar'.",
      "cargo_warehouse": "Galpão Sul",
      "target_warehouse": "Galpão Norte"
    }
  ]
}
```

A tela exibe estes erros de forma clara:
- Código da carga problemática
- Tipo do erro
- Mensagem explicativa
- Galpão atual vs. galpão destino

### 6. **Feedback Visual**
- **Caixa de Resultado**: mostra status da operação em tempo real
- **Cores**:
  - 🔵 Azul: Processando
  - 🟢 Verde: Sucesso
  - 🟠 Laranja: Avisos (cargas não encontradas, impressão com erro)
  - 🔴 Vermelho: Erros

### 7. **Correções Aplicadas**
- ❌ Removida janela "tk" avulsa (era o título antigo)
- ❌ Removidas todas as funcionalidades de consulta/listagem de consolidadores
- ✅ Interface focada exclusivamente em criar e imprimir
- ✅ Melhor tratamento de erros da API

## Como Usar

1. Acesse o menu **"🧩 Consolidação"** no sistema
2. Selecione o **Galpão** onde as cargas estão
3. Selecione a **Impressora** para imprimir as etiquetas
4. Cole ou digite os **códigos das cargas** (um por linha ou separados)
5. Defina a **quantidade de etiquetas** desejada
6. Clique em **"✅ Consolidar e Imprimir"**
7. Acompanhe o resultado na caixa de mensagens
8. Clique em **"🔄 Limpar"** para iniciar nova consolidação

## Integração com Sistema PHP

- A **consulta de consolidadores** deve ser feita no sistema PHP principal
- Este módulo Python é dedicado **apenas à consolidação operacional**:
  - Leitura rápida de códigos (leitor de barras ou colagem)
  - Criação do consolidador
  - Impressão imediata das etiquetas ZPL (QR Code)

## API Endpoints Utilizados

- `GET /api/warehouses/select` - Lista galpões disponíveis
- `GET /api/cargos/pending-physical-receipt?code={code}` - Busca cargo por código
- `POST /api/consolidators` - Cria consolidador com payload:
  ```json
  {
    "warehouse_id": 1,
    "cargo_ids": [123, 456, 789]
  }
  ```

## Estrutura da Etiqueta Consolidador

Gerada por `ZplGenerator.build_consolidator_zpl()`:
- **QR Code** com código do consolidador
- Código do consolidador (texto)
- Quantidade de cargas
- Peso total
- Volume total
- Nome do galpão
- Status
- Data/hora de criação
- Posicionamento independente de cada elemento (configurável)
