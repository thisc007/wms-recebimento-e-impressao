class LoginManager:
    def __init__(self, api_client):
        self.api_client = api_client

    def login(self, cpf, password):
        payload = {
            'cpf': cpf,
            'password': password
        }
        response = self.api_client.post('/login', json=payload)
        if response.status_code == 200:
            return response.json().get('token')
        else:
            raise Exception("Login failed: " + response.text)

    def validate_credentials(self, cpf, password):
        # This method can be expanded to include more complex validation logic
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF must be 11 digits long and numeric.")
        if not password:
            raise ValueError("Password cannot be empty.")
        return True