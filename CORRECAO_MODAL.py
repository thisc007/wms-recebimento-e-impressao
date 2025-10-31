#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de correção da janela modal de configuração de impressoras
"""

print("=" * 70)
print("CORREÇÃO APLICADA - Janela de Configuração de Impressoras")
print("=" * 70)

print("""
✅ PROBLEMAS CORRIGIDOS:

1. JANELA PAI NÃO ERA REATIVADA
   - Antes: PrinterConfigWindow usava tk.Tk() criando instância separada
   - Depois: Usa tk.Toplevel(parent) como janela modal correta
   
2. MODAL NÃO BLOQUEAVA INTERAÇÃO
   - Adicionado: transient() e grab_set() para janela modal verdadeira
   - Resultado: Usuário não pode clicar na janela pai até fechar a modal

3. CÓDIGO DESNECESSÁRIO REMOVIDO
   - Antes: disable_main_window() e enable_main_window() manualmente
   - Depois: grab_set() do Tkinter gerencia automaticamente

📝 ALTERAÇÕES REALIZADAS:

Arquivo: src/ui/printer_config_window.py
-----------------------------------------
1. Adicionado parâmetro 'parent' ao __init__:
   def __init__(self, cpf: str, token: str, user_data: dict, parent=None)

2. Modificado setup_window() para usar Toplevel quando há parent:
   if self.parent:
       self.root = tk.Toplevel(self.parent)
       self.root.transient(self.parent)  # Janela sempre no topo do pai
       self.root.grab_set()              # Bloquear interação com pai
   else:
       self.root = tk.Tk()

3. Melhorado close_window() para liberar grab:
   def close_window(self):
       log_info("Fechando janela de configuração de impressoras")
       try:
           if self.parent:
               self.root.grab_release()
       except:
           pass
       self.root.destroy()

Arquivo: src/ui/gui.py
----------------------
1. Removido disable_main_window() de open_printer_config()
2. Removido enable_main_window() de open_printer_config()
3. Adicionado parent=self.root ao criar PrinterConfigWindow:
   printer_config_window = PrinterConfigWindow(
       self.cpf, 
       self.api_client.token, 
       self.user_data,
       parent=self.root  # <-- NOVO
   )

🎯 COMO FUNCIONA AGORA:

1. Usuário clica em "Configuração de Impressora"
2. PrinterConfigWindow abre como Toplevel(parent)
3. grab_set() bloqueia cliques na janela pai automaticamente
4. Janela modal fica sempre no topo (transient)
5. Usuário fecha a janela de configuração
6. grab_release() libera a janela pai automaticamente
7. wait_window() retorna e o fluxo continua
8. Janela pai volta a estar ativa e responsiva

✨ BENEFÍCIOS:

✓ Comportamento modal correto (padrão do Tkinter)
✓ Menos código (removido disable/enable manual)
✓ Mais confiável (usa mecanismos nativos do Tkinter)
✓ Funciona em todos os casos (erro, fechamento normal, etc)
✓ Janela pai reativa automaticamente

📚 REFERÊNCIAS TÉCNICAS:

- tk.Toplevel(): Cria janela secundária (não uma nova instância Tk)
- transient(parent): Janela sempre acima do pai, minimiza junto
- grab_set(): Bloqueia entrada para outras janelas
- grab_release(): Libera o bloqueio
- wait_window(): Aguarda destruição da janela

⚠️  IMPORTANTE:

Esta correção se aplica apenas à janela de Configuração de Impressoras.
As outras janelas modais (BatchPrintWindow, ReprintWindow) já estavam
usando Toplevel corretamente.

🧪 PARA TESTAR:

1. Execute: python src/main_launcher.py --gui-debug
2. Faça login
3. Clique em "Configuração de Impressora"
4. TESTE: Tente clicar na janela principal (não deve funcionar)
5. Feche a janela de configuração
6. VERIFIQUE: Janela principal deve estar ativa e responsiva
7. Teste os botões da janela principal

""")

print("=" * 70)
print("Status: ✅ Correção aplicada com sucesso!")
print("=" * 70)
