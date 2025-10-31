class LoginManager:
    def __init__(self, api_client):
        self.api_client = api_client
        # Importar config aqui para evitar import circular
        from utils.config import load_config
        self.config = load_config()

    def login(self, cpf, password):
        # Modo debug/teste - útil para desenvolvimento
        if self.config.get('debug_mode', False):
            # Simular login bem-sucedido em modo debug
            if cpf == "12345678901" and password == "123":
                return {
                    'token': 'debug_token_12345',
                    'user': {
                        'id': 999,
                        'name': 'Usuário Debug',
                        'cpf': cpf,
                        'email': 'debug@test.com',
                        'registration': 9999
                    }
                }
            else:
                raise Exception("Credenciais inválidas (modo debug)")
        
        payload = {
            'cpf': cpf,
            'password': password,
            "module":"printing"
        }
        try:
            response = self.api_client.post('/login', data=payload)
            if response.status_code == 200:
                response_data = response.json()
                
                # Validar se a resposta contém os dados esperados
                if 'token' not in response_data:
                    raise Exception("Token não encontrado na resposta da API")
                
                if 'user' not in response_data:
                    raise Exception("Dados do usuário não encontrados na resposta da API")
                
                # Retornar dados completos da API
                return {
                    'token': response_data['token'],
                    'user': response_data['user']
                }
                
            elif response.status_code == 401:
                raise Exception("Credenciais inválidas")
            elif response.status_code == 404:
                raise Exception("Endpoint de login não encontrado")
            else:
                raise Exception(f"Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            # Re-raise a exceção para ser tratada pela interface
            raise e

    def validate_credentials(self, cpf, password):
        # This method can be expanded to include more complex validation logic
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF must be 11 digits long and numeric.")
        if not password:
            raise ValueError("Password cannot be empty.")
        return True