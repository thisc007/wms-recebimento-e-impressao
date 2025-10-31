"""
Utilitários para manipular dados do usuário retornados pela API
"""

class UserSession:
    """Classe para gerenciar a sessão do usuário"""
    
    def __init__(self, token, user_data):
        self.token = token
        self.user_data = user_data
    
    def get_user_id(self):
        """Retorna o ID do usuário"""
        return self.user_data.get('id')
    
    def get_user_name(self):
        """Retorna o nome do usuário"""
        return self.user_data.get('name', 'Usuário')
    
    def get_user_cpf(self):
        """Retorna o CPF do usuário"""
        return self.user_data.get('cpf')
    
    def get_user_email(self):
        """Retorna o email do usuário"""
        return self.user_data.get('email')
    
    def get_user_registration(self):
        """Retorna a matrícula do usuário"""
        return self.user_data.get('registration')
    
    def get_company_id(self):
        """Retorna o ID da empresa do usuário"""
        return self.user_data.get('company_id')
    
    def get_hr_company_id(self):
        """Retorna o ID da empresa de RH"""
        return self.user_data.get('hr_company_id')
    
    def is_user_active(self):
        """Verifica se o usuário está ativo"""
        return self.user_data.get('is_active', 0) == 1
    
    def is_user_blocked(self):
        """Verifica se o usuário está bloqueado"""
        return self.user_data.get('is_blocked', 0) == 1
    
    def get_user_uuid(self):
        """Retorna o UUID do usuário"""
        return self.user_data.get('uuid')
    
    def get_token(self):
        """Retorna o token de autenticação"""
        return self.token
    
    def get_user_info_summary(self):
        """Retorna um resumo das informações do usuário"""
        return {
            'id': self.get_user_id(),
            'name': self.get_user_name(),
            'cpf': self.get_user_cpf(),
            'email': self.get_user_email(),
            'registration': self.get_user_registration(),
            'is_active': self.is_user_active(),
            'is_blocked': self.is_user_blocked()
        }
    
    def to_dict(self):
        """Retorna todos os dados como dicionário"""
        return {
            'token': self.token,
            'user': self.user_data
        }


def create_user_session(login_result):
    """Cria uma sessão de usuário a partir do resultado do login"""
    if isinstance(login_result, dict):
        token = login_result.get('token')
        user_data = login_result.get('user', {})
        return UserSession(token, user_data)
    else:
        # Para compatibilidade com versões antigas que retornam apenas token
        return UserSession(login_result, {})


def validate_login_response(response_data):
    """Valida se a resposta da API contém os dados necessários"""
    if not isinstance(response_data, dict):
        raise ValueError("Resposta da API deve ser um dicionário")
    
    if 'token' not in response_data:
        raise ValueError("Token não encontrado na resposta da API")
    
    if 'user' not in response_data:
        raise ValueError("Dados do usuário não encontrados na resposta da API")
    
    user_data = response_data['user']
    required_fields = ['id', 'name', 'cpf']
    
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Campo obrigatório '{field}' não encontrado nos dados do usuário")
    
    return True


def extract_user_permissions(user_data):
    """Extrai permissões do usuário (pode ser expandido no futuro)"""
    permissions = []
    
    # Verificar se o usuário está ativo e não bloqueado
    if user_data.get('is_active', 0) == 1 and user_data.get('is_blocked', 0) == 0:
        permissions.append('login')
        permissions.append('print_labels')
        permissions.append('reprint_labels')
    
    return permissions