#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para configurar e diagnosticar impressora Zebra
"""

import socket
import time

IP = "192.168.99.135"
PORT = 9100

def send_command(command, description, wait_response=True):
    """Envia comando para impressora"""
    print(f"\n{description}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((IP, PORT))
            sock.sendall(command.encode('utf-8'))
            
            if wait_response:
                time.sleep(0.5)
                try:
                    response = sock.recv(2048).decode('utf-8', errors='ignore')
                    print(f"Resposta: {response}")
                    return response
                except socket.timeout:
                    print("(Sem resposta)")
            else:
                print("✓ Comando enviado")
            
            return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def main():
    print("=" * 70)
    print("CONFIGURAÇÃO E DIAGNÓSTICO - ZEBRA GK420t")
    print("=" * 70)
    
    # 1. Status Host
    print("\n1. VERIFICANDO STATUS DA IMPRESSORA")
    send_command("~HS\n", "Status do Host", wait_response=True)
    
    # 2. Informações da impressora
    print("\n2. INFORMAÇÕES DA IMPRESSORA")
    send_command("~HI\n", "Informações de Hardware", wait_response=True)
    
    # 3. Configuração atual
    print("\n3. CONFIGURAÇÃO ATUAL")
    send_command("^XA^HH^XZ\n", "Dump de Configuração", wait_response=True)
    
    # 4. Comandos de configuração
    print("\n" + "=" * 70)
    print("COMANDOS DE CONFIGURAÇÃO DISPONÍVEIS:")
    print("=" * 70)
    
    while True:
        print("\nEscolha uma opção:")
        print("  1 - Calibrar sensor de mídia (RECOMENDADO)")
        print("  2 - Imprimir etiqueta de configuração")
        print("  3 - Modo de detecção: GAP (etiquetas com espaço)")
        print("  4 - Modo de detecção: CONTINUOUS (papel contínuo)")
        print("  5 - Modo de detecção: WEB (etiquetas em rolo)")
        print("  6 - Ajustar escuridão (darkness)")
        print("  7 - Resetar impressora para padrões de fábrica")
        print("  8 - Imprimir etiqueta de teste")
        print("  9 - Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == "1":
            # Calibração automática
            print("\n⚠️  ATENÇÃO: A impressora irá calibrar o sensor.")
            print("    Certifique-se de que há etiquetas carregadas!")
            confirm = input("Continuar? (S/N): ").strip().upper()
            if confirm == "S":
                send_command("~JC\n", "Calibrando sensor", wait_response=False)
                time.sleep(3)
                print("✓ Calibração concluída!")
                print("  Teste agora a impressão.")
        
        elif choice == "2":
            # Imprimir configuração
            send_command("~WC\n", "Imprimindo etiqueta de configuração", wait_response=False)
            print("✓ Verifique se saiu uma etiqueta com as configurações.")
        
        elif choice == "3":
            # Modo GAP
            cmd = "^XA^MMD^XZ\n"
            send_command(cmd, "Configurando modo GAP (etiquetas com espaço)", wait_response=False)
            print("✓ Modo GAP configurado. Execute calibração (opção 1).")
        
        elif choice == "4":
            # Modo CONTINUOUS
            cmd = "^XA^MNC^XZ\n"
            send_command(cmd, "Configurando modo CONTINUOUS (papel contínuo)", wait_response=False)
            print("✓ Modo CONTINUOUS configurado.")
        
        elif choice == "5":
            # Modo WEB
            cmd = "^XA^MMT^XZ\n"
            send_command(cmd, "Configurando modo WEB (etiquetas em rolo)", wait_response=False)
            print("✓ Modo WEB configurado. Execute calibração (opção 1).")
        
        elif choice == "6":
            # Ajustar darkness
            darkness = input("Digite o valor de escuridão (0-30, recomendado: 10-15): ").strip()
            if darkness.isdigit():
                cmd = f"^XA^MD{darkness}^XZ\n"
                send_command(cmd, f"Ajustando escuridão para {darkness}", wait_response=False)
                print(f"✓ Escuridão ajustada para {darkness}.")
        
        elif choice == "7":
            # Reset
            print("\n⚠️  ATENÇÃO: Isso vai resetar TODAS as configurações!")
            confirm = input("Tem certeza? (S/N): ").strip().upper()
            if confirm == "S":
                send_command("^XA^JUF^XZ\n", "Resetando para padrões de fábrica", wait_response=False)
                time.sleep(2)
                print("✓ Reset concluído. Calibre o sensor (opção 1).")
        
        elif choice == "8":
            # Teste de impressão
            zpl = """^XA
^FO50,50^A0N,40,40^FDTESTE OK!^FS
^FO50,120^A0N,25,25^FDImpressora funcionando^FS
^FO50,160^BCN,60,Y,N,N^FD123456^FS
^XZ"""
            send_command(zpl, "Enviando etiqueta de teste", wait_response=False)
            print("✓ Etiqueta enviada. Verifique a saída!")
        
        elif choice == "9":
            break
        
        else:
            print("Opção inválida!")
    
    print("\n" + "=" * 70)
    print("RESUMO DE PROBLEMAS COMUNS:")
    print("=" * 70)
    print("""
1. ETIQUETA NÃO SAI:
   - Execute calibração (opção 1)
   - Verifique se há etiquetas na impressora
   - Pressione o botão FEED manualmente

2. ETIQUETA SAI EM BRANCO:
   - Aumente a escuridão (opção 6) para 12-15
   - Verifique se o ribbon está instalado (se usar ribbon)

3. ETIQUETA DESALINHADA:
   - Execute calibração (opção 1)
   - Verifique o modo de detecção (opções 3-5)
   - Para etiquetas com espaço: use GAP (opção 3)

4. IMPRESSORA NÃO RESPONDE:
   - Verifique cabo de rede
   - Verifique se IP está correto
   - Reinicie a impressora

5. LUZ VERMELHA PISCANDO:
   - Tampa aberta: feche a tampa
   - Sem papel: coloque etiquetas
   - Ribbon acabou: substitua o ribbon (se aplicável)
""")

if __name__ == "__main__":
    main()
