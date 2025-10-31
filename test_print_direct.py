#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste direto de impressão na Zebra
"""

import socket

# Configuração da sua impressora
IP = "192.168.99.135"
PORT = 9100

# ZPL mais simples possível
zpl_simples = """^XA
^FO50,50^A0N,50,50^FDTESTE^FS
^XZ"""

# ZPL com mais detalhes
zpl_completo = """^XA
^FO50,50^A0N,30,30^FDTESTE DE IMPRESSAO^FS
^FO50,100^A0N,25,25^FDImpressora Zebra^FS
^FO50,140^A0N,20,20^FDIP: 192.168.99.135^FS
^FO50,170^BCN,60,Y,N,N^FD123456^FS
^XZ"""

def test_connection():
    """Testa conexão com a impressora"""
    print(f"\n1. Testando conexão com {IP}:{PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((IP, PORT))
        sock.close()
        
        if result == 0:
            print("   ✓ Conexão bem-sucedida!")
            return True
        else:
            print(f"   ✗ Falha na conexão (código: {result})")
            return False
    except Exception as e:
        print(f"   ✗ Erro: {e}")
        return False

def send_zpl(zpl, description):
    """Envia ZPL para impressora"""
    print(f"\n2. Enviando {description}...")
    print(f"   Tamanho do ZPL: {len(zpl)} bytes")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((IP, PORT))
            
            # Enviar ZPL
            sock.sendall(zpl.encode('utf-8'))
            print("   ✓ ZPL enviado!")
            
            # Tentar receber resposta (algumas impressoras enviam status)
            sock.settimeout(2)
            try:
                response = sock.recv(1024)
                if response:
                    print(f"   Resposta da impressora: {response[:100]}")
            except socket.timeout:
                print("   (Sem resposta da impressora - normal para algumas Zebras)")
            
            return True
            
    except Exception as e:
        print(f"   ✗ Erro ao enviar: {e}")
        return False

def check_printer_status():
    """Verifica status da impressora (comando ~HS)"""
    print("\n3. Verificando status da impressora...")
    status_cmd = "~HS\n"
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((IP, PORT))
            sock.sendall(status_cmd.encode('utf-8'))
            
            sock.settimeout(2)
            try:
                response = sock.recv(1024).decode('utf-8', errors='ignore')
                print(f"   Status: {response}")
                return True
            except socket.timeout:
                print("   (Timeout ao aguardar status)")
                return False
                
    except Exception as e:
        print(f"   ✗ Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTE DIRETO DE IMPRESSÃO - ZEBRA GK420t")
    print("=" * 60)
    
    # Teste 1: Conexão
    if not test_connection():
        print("\n❌ Impressora não está acessível!")
        print("\nVerifique:")
        print("  - A impressora está ligada?")
        print("  - O IP está correto?")
        print("  - Há firewall bloqueando a porta 9100?")
        return
    
    # Teste 2: Status
    check_printer_status()
    
    # Teste 3: Impressão simples
    print("\n" + "=" * 60)
    if send_zpl(zpl_simples, "etiqueta SIMPLES"):
        print("\n✓ Etiqueta simples enviada!")
        print("  -> Verifique se saiu uma etiqueta com 'TESTE'")
        
        input("\nPressione ENTER para enviar etiqueta completa...")
        
        # Teste 4: Impressão completa
        if send_zpl(zpl_completo, "etiqueta COMPLETA"):
            print("\n✓ Etiqueta completa enviada!")
            print("  -> Verifique se saiu uma etiqueta com mais detalhes")
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO:")
    print("=" * 60)
    print("\nSe as mensagens dizem 'enviado' mas não imprimiu:")
    print("  1. Verifique se há papel/etiquetas na impressora")
    print("  2. Verifique se a impressora não está em pausa")
    print("  3. Verifique se há luz de erro piscando")
    print("  4. Tente pressionar o botão FEED da impressora")
    print("  5. Verifique se o sensor de etiqueta está calibrado")
    print("\nPara calibrar o sensor:")
    print("  - Desligue a impressora")
    print("  - Segure o botão FEED e ligue")
    print("  - Solte após as luzes piscarem")
    print("  - A impressora fará calibração automática")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
