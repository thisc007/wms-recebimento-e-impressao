# 🧪 Modo Debug/Teste

Para testar a aplicação sem uma API real funcionando, você pode usar o modo debug.

## 🚀 Como Usar o Modo Debug

### Opção 1: Via Linha de Comando
```bash
python src/main_launcher.py --gui-debug
```

### Opção 2: Editando a Configuração
Edite o arquivo `config/settings.json` e altere:
```json
{
  "debug_mode": true
}
```

## 🔑 Credenciais de Teste

Quando em modo debug, use:
- **CPF**: `12345678901`
- **Senha**: `123`

## ✅ O que o Modo Debug Faz

- ✅ Simula login bem-sucedido com credenciais de teste
- ✅ Não faz chamadas reais para a API
- ✅ Permite testar toda a interface
- ✅ Logs mais detalhados
- ✅ Ideal para desenvolvimento

## 🔧 Voltando ao Modo Normal

Para voltar ao modo normal:
1. Edite `config/settings.json` e altere `"debug_mode": false`
2. Ou use `python src/main_launcher.py --gui-simple`

## 📝 Logs

Os logs ficam em `logs/application.log` e mostram todas as ações realizadas.