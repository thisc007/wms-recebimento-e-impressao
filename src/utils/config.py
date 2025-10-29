def load_config(file_path):
    import json
    with open(file_path, 'r') as f:
        return json.load(f)

def save_config(file_path, config):
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

def get_default_config():
    return {
        "api_base": "http://localhost:5000/api",
        "printer": {
            "type": "windows_printer",
            "share": "\\\\localhost\\MyPrinter"
        },
        "logging": {
            "level": "INFO",
            "file": "logs/app.log"
        }
    }