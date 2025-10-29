class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_request(self, endpoint, method='GET', data=None, headers=None):
        import requests

        url = f"{self.base_url}/{endpoint}"
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError("Unsupported HTTP method")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get(self, endpoint, headers=None):
        return self.send_request(endpoint, method='GET', headers=headers)

    def post(self, endpoint, data, headers=None):
        return self.send_request(endpoint, method='POST', data=data, headers=headers)