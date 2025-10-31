import json
import os

def load_config(file_path=None, debug=False):
    """Carrega a configuração do arquivo JSON"""
    if file_path is None:
        # Caminho padrão relativo ao arquivo config
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if debug:
            file_path = os.path.join(current_dir, 'config', 'settings_debug.json')
        else:
            file_path = os.path.join(current_dir, 'config', 'settings.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado: {file_path}")
        return get_default_config()
    except json.JSONDecodeError:
        print(f"Erro ao ler arquivo de configuração: {file_path}")
        return get_default_config()

def save_config(config, file_path=None):
    """Salva a configuração no arquivo JSON"""
    if file_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(current_dir, 'config', 'settings.json')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_default_config():
    """Retorna configuração padrão"""
    return {
        "api_base": "http://localhost:8000/api",
        "log_level": "INFO",
        "printer": {
            "type": "windows_printer",
            "share": "\\\\localhost\\MyPrinter"
        },
        "default_qty": 1,
        "timeout": 30,
        "debug_mode": False
    }