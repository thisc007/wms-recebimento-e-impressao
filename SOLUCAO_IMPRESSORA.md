# ✅ SOLUÇÃO - Impressora Não Imprime Etiquetas

## 📊 Diagnóstico Realizado

### Status da Impressora
```
✓ Conexão: OK (192.168.99.135:9100)
✓ Comunicação: OK
✓ ZPL sendo enviado: OK
✓ Modelo: GK420t-200dpi
✓ Firmware: V61.17.16Z
```

### Configuração Atual
```
DARKNESS:      15.0
PRINT SPEED:   5 IPS
SENSOR TYPE:   WEB (sensor de etiqueta)
MEDIA TYPE:    GAP/NOTCH (detecção por espaço)
LABEL LENGTH:  58mm
```

## 🔧 Problema Identificado

O código está funcionando corretamente. O ZPL está sendo enviado para a impressora com sucesso. 

**O problema é físico/configuração da impressora**, não do software.

## ✨ SOLUÇÃO (Escolha uma opção)

### Opção 1: Calibração Rápida via Script ⭐ RECOMENDADO

1. Execute o script de configuração:
   ```bash
   python fix_printer_setup.py
   ```

2. Digite a opção **1** para calibrar
3. Aguarde 3-5 segundos
4. Digite a opção **8** para testar impressão
5. Verifique se a etiqueta saiu

### Opção 2: Calibração Manual na Impressora

1. **Desligue** a impressora
2. **Segure** o botão FEED (botão na frente)
3. **Ligue** a impressora (ainda segurando o botão)
4. **Solte** o botão quando as luzes começarem a piscar
5. A impressora vai:
   - Avançar várias etiquetas
   - Fazer medições
   - Parar automaticamente
6. Teste novamente a impressão

### Opção 3: Calibração via Comando ZPL

1. Execute:
   ```bash
   python -c "import socket; s=socket.socket(); s.connect(('192.168.99.135', 9100)); s.send(b'~JC\n'); s.close()"
   ```

2. Aguarde a impressora calibrar (3-5 segundos)
3. Teste novamente

## 📝 Verificações Antes de Calibrar

Certifique-se de que:

- [ ] **Há etiquetas** carregadas na impressora
- [ ] As etiquetas estão **alinhadas** corretamente
- [ ] A **tampa está fechada**
- [ ] **Não há luz vermelha** piscando
- [ ] O **sensor** está posicionado corretamente (pequeno sensor móvel embaixo das etiquetas)

## 🎯 Depois da Calibração

### Teste no Sistema

1. Abra a aplicação:
   ```bash
   python src/main_launcher.py --gui-debug
   ```

2. Faça login
3. Vá em **Configuração de Impressora**
4. Clique em **"Test with Pattern"**
5. Deve sair uma etiqueta com:
   - Logo
   - Texto "Teste de Impressora"
   - Data/hora
   - Código de barras

## 🔍 Se Ainda Não Funcionar

### Problema: Etiqueta sai em branco
**Solução:**
```bash
python fix_printer_setup.py
# Digite opção 6
# Digite: 20 (aumentar escuridão)
```

### Problema: Etiqueta desalinhada
**Solução:**
1. Verifique se o sensor móvel está alinhado com o espaço entre etiquetas
2. Execute calibração novamente (opção 1)

### Problema: Impressora não responde
**Solução:**
1. Verifique o cabo de rede
2. Teste o ping:
   ```bash
   ping 192.168.99.135
   ```
3. Reinicie a impressora

### Problema: Luz vermelha piscando
**Causas:**
- Tampa aberta → Feche a tampa
- Sem papel → Coloque etiquetas
- Ribbon acabou → Substitua (se usar ribbon)

## 📚 Comandos Úteis ZPL

### Imprimir Configuração da Impressora
```bash
python -c "import socket; s=socket.socket(); s.connect(('192.168.99.135', 9100)); s.send(b'~WC\n'); s.close()"
```

### Ver Status
```bash
python -c "import socket; s=socket.socket(); s.connect(('192.168.99.135', 9100)); s.send(b'~HS\n'); print(s.recv(1024)); s.close()"
```

### Teste Simples
```bash
python test_print_direct.py
```

## 💡 Dicas Importantes

1. **Sempre calibre** após trocar o tipo de etiqueta
2. **Ajuste a escuridão** se a impressão estiver muito clara/escura
3. **Posicione o sensor** móvel no meio do espaço entre etiquetas
4. **Limpe o cabeçote** regularmente (a cada 2-3 rolos)

## 📞 Suporte Zebra

Se nada funcionar, pode ser problema de hardware:
- Telefone: 0800 591 0597
- Site: www.zebra.com/br
- Verifique garantia do equipamento

---

## ✅ Checklist Final

Após calibrar, verifique:

- [ ] Teste via script (`test_print_direct.py`) ✓
- [ ] Teste na interface (`Test with Pattern`) ✓
- [ ] Impressão de lote (batch) ✓
- [ ] Reimpressão ✓

---

**Data:** 30/10/2025  
**Impressora:** Zebra GK420t (IP: 192.168.99.135)  
**Status:** Comunicação OK - Necessita Calibração
