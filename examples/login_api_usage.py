"""
Exemplo de como usar e manipular os dados retornados pela API de login
"""

from utils.user_session import UserSession, create_user_session, validate_login_response
from utils.logger import log_info, log_error

# Exemplo 1: Resposta da API de login
exemplo_resposta_api = {
    "token": "125|JwOjvI2FCEXspOOcXinfhGfnVONYOKiqQ7hwWuJcbba15fda",
    "user": {
        "id": 1,
        "uuid": "78e364ab-392b-4631-b720-fc92185bf12c",
        "company_id": 1,
        "name": "Super User",
        "observation": "",
        "is_active": 1,
        "is_blocked": 0,
        "email": "admin@milleniumtransportes.com.br",
        "cpf": "12345678901",
        "registration": 1001,
        "hr_company_id": 1,
        "email_verified_at": None,
        "created_at": "2025-10-08T19:40:26.000000Z",
        "updated_at": "2025-10-08T19:40:26.000000Z"
    }
}

def exemplo_uso_basico():
    """Exemplo básico de como usar os dados do login"""
    
    # 1. Validar a resposta da API
    try:
        validate_login_response(exemplo_resposta_api)
        print("✅ Resposta da API válida")
    except ValueError as e:
        print(f"❌ Erro na validação: {e}")
        return
    
    # 2. Criar sessão do usuário
    session = create_user_session(exemplo_resposta_api)
    
    # 3. Acessar dados do usuário
    print(f"Nome: {session.get_user_name()}")
    print(f"CPF: {session.get_user_cpf()}")
    print(f"Email: {session.get_user_email()}")
    print(f"Matrícula: {session.get_user_registration()}")
    print(f"Token: {session.get_token()}")
    
    # 4. Verificar status do usuário
    if session.is_user_active() and not session.is_user_blocked():
        print("✅ Usuário pode acessar o sistema")
    else:
        print("❌ Usuário bloqueado ou inativo")


def exemplo_uso_interface():
    """Exemplo de como usar na interface gráfica"""
    
    session = create_user_session(exemplo_resposta_api)
    
    # Dados para exibir na tela principal
    titulo_janela = f"WMS - {session.get_user_name()}"
    texto_usuario = f"Usuário: {session.get_user_name()}"
    texto_matricula = f"Matrícula: {session.get_user_registration()}"
    
    print(f"Título da janela: {titulo_janela}")
    print(f"Texto do usuário: {texto_usuario}")
    print(f"Texto da matrícula: {texto_matricula}")


def exemplo_logs_detalhados():
    """Exemplo de como registrar logs detalhados"""
    
    session = create_user_session(exemplo_resposta_api)
    
    # Log de login
    log_info(f"Login realizado - Usuário: {session.get_user_name()} "
             f"(ID: {session.get_user_id()}, CPF: {session.get_user_cpf()})")
    
    # Log de ação
    log_info(f"Usuário {session.get_user_name()} (Matrícula: {session.get_user_registration()}) "
             f"acessou funcionalidade de impressão")


def exemplo_requisicoes_autenticadas():
    """Exemplo de como usar o token em requisições futuras"""
    
    session = create_user_session(exemplo_resposta_api)
    
    # Headers para requisições autenticadas
    headers = {
        'Authorization': f'Bearer {session.get_token()}',
        'Content-Type': 'application/json'
    }
    
    print("Headers para requisições:")
    print(headers)
    
    # Dados do usuário para enviar em requisições
    user_context = {
        'user_id': session.get_user_id(),
        'company_id': session.get_company_id()
    }
    
    print("Contexto do usuário para requisições:")
    print(user_context)


def exemplo_personalizacao_interface():
    """Exemplo de como personalizar a interface baseado no usuário"""
    
    session = create_user_session(exemplo_resposta_api)
    
    # Personalizar saudação
    saudacao = f"Bem-vindo, {session.get_user_name()}!"
    
    # Verificar se pode imprimir (baseado no status do usuário)
    pode_imprimir = session.is_user_active() and not session.is_user_blocked()
    
    # Mostrar informações da empresa (se disponível)
    if session.get_company_id():
        empresa_info = f"Empresa ID: {session.get_company_id()}"
    else:
        empresa_info = "Empresa não definida"
    
    print(f"Saudação: {saudacao}")
    print(f"Pode imprimir: {pode_imprimir}")
    print(f"Info da empresa: {empresa_info}")


if __name__ == "__main__":
    print("=== Exemplo de Uso Básico ===")
    exemplo_uso_basico()
    
    print("\n=== Exemplo de Uso na Interface ===")
    exemplo_uso_interface()
    
    print("\n=== Exemplo de Logs Detalhados ===")
    exemplo_logs_detalhados()
    
    print("\n=== Exemplo de Requisições Autenticadas ===")
    exemplo_requisicoes_autenticadas()
    
    print("\n=== Exemplo de Personalização da Interface ===")
    exemplo_personalizacao_interface()