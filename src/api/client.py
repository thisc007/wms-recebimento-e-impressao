import requests
import json
import os
from utils.config import load_config

class APIClient:
    def __init__(self):
        # Verificar se está em modo debug
        debug_mode = os.environ.get('WMS_DEBUG', 'false').lower() == 'true'
        config = load_config(debug=debug_mode)
        
        self.base_url = config.get('api_base', 'http://localhost:8000/api')
        self.timeout = config.get('timeout', 30)
        self.debug_mode = config.get('debug_mode', False)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def send_request(self, endpoint, method='GET', data=None, headers=None, **kwargs):
        """Envia uma requisição HTTP para a API"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Mesclar headers padrão com headers customizados
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, timeout=self.timeout, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=self.timeout, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=self.timeout, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=self.timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response
            
        except requests.exceptions.Timeout:
            raise Exception("Request timeout - servidor não responde")
        except requests.exceptions.ConnectionError:
            raise Exception("Erro de conexão - verifique a conectividade com a API")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")

    def get(self, endpoint, headers=None, **kwargs):
        """Realiza uma requisição GET"""
        return self.send_request(endpoint, method='GET', headers=headers, **kwargs)

    def post(self, endpoint, data=None, headers=None, **kwargs):
        """Realiza uma requisição POST"""
        return self.send_request(endpoint, method='POST', data=data, headers=headers, **kwargs)
    
    def put(self, endpoint, data=None, headers=None, **kwargs):
        """Realiza uma requisição PUT"""
        return self.send_request(endpoint, method='PUT', data=data, headers=headers, **kwargs)
    
    def delete(self, endpoint, headers=None, **kwargs):
        """Realiza uma requisição DELETE"""
        return self.send_request(endpoint, method='DELETE', headers=headers, **kwargs)


# Manter compatibilidade com código existente
class ApiClient(APIClient):
    def __init__(self, base_url=None):
        super().__init__()
        if base_url:
            self.base_url = base_url