# Printing Service

This project is a printing service application that allows users to authenticate and print labels using ZPL (Zebra Programming Language). The application is structured into several modules for better organization and maintainability.

## Project Structure

# WMS - Sistema de Recebimento e Impressão

Este projeto é um sistema de impressão de etiquetas para WMS (Warehouse Management System) que permite aos usuários fazer login e imprimir etiquetas usando ZPL (Zebra Programming Language). A aplicação oferece duas interfaces: gráfica (GUI) e linha de comando (CLI).

## 🖥️ Interfaces Disponíveis

### Interface Gráfica (GUI) - Recomendada
- **Tela de Login**: CPF com formatação automática e validação + Senha
- **Menu Principal**: Botões para Impressão em Lote, Reimpressão e Logout
- **Validação**: CPF automaticamente validado e formatado
- **Design moderno**: Interface intuitiva e amigável

### Interface de Linha de Comando (CLI)
- Interface tradicional via terminal
- Opções de menu baseadas em texto

## 📁 Estrutura do Projeto

```
printing-service/
├── src/
│   ├── main.py              # Ponto de entrada original
│   ├── main_launcher.py     # Launcher para escolher interface
│   ├── auth/
│   │   ├── __init__.py
│   │   └── login.py         # Gerenciamento de login
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py        # Cliente da API
│   ├── printer/
│   │   ├── __init__.py
│   │   ├── label_printer.py
│   │   └── zpl_generator.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── menu.py          # Interface CLI
│   │   └── gui.py           # Interface Gráfica
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # Sistema de logging
│       ├── config.py        # Gerenciamento de configuração
│       └── validators.py    # Validadores (CPF, etc.)
├── config/
│   └── settings.json        # Configurações da aplicação
├── logs/                    # Logs da aplicação
├── requirements.txt         # Dependências Python
├── start.bat               # Script de inicialização Windows
└── README.md
```

## 🚀 Como Executar

### Opção 1: Script de Conveniência (Recomendado)
```batch
# Windows
start.bat
```

### Opção 2: Interface Gráfica Diretamente
```bash
python src/main_launcher.py --gui
```

### Opção 3: Interface de Linha de Comando
```bash
python src/main_launcher.py --cli
```

### Opção 4: Padrão (Interface Gráfica)
```bash
python src/main_launcher.py
```

## 📋 Pré-requisitos

1. **Python 3.7+**
2. **Dependências Python** (instalar com pip):
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Instalação

1. Clone o repositório:
   ```bash
   git clone <repository-url>
   cd printing-service
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as settings em `config/settings.json`:
   ```json
   {
     "api_base": "http://localhost:8000/api",
     "log_level": "INFO",
     "printer": {
       "type": "windows_printer",
       "share": "\\\\localhost\\MyPrinter"
     },
     "default_qty": 1,
     "timeout": 30
   }
   ```

4. Execute a aplicação:
   ```batch
   start.bat
   ```

## 🎯 Funcionalidades

### ✅ Implementadas
- **Login seguro**: Autenticação via CPF e senha
- **Validação de CPF**: Validação matemática completa
- **Formatação automática**: CPF formatado durante digitação
- **Interface dupla**: GUI moderna + CLI tradicional
- **Sistema de logs**: Registros detalhados de ações
- **Gerenciamento de configuração**: Settings centralizadas

### 🚧 Em Desenvolvimento
- **Impressão em lote**: Listagem e impressão de múltiplas etiquetas
- **Reimpressão**: Digitalização e reimpressão de etiquetas existentes
- **Gerenciamento de impressoras**: Configuração avançada de impressoras

## 🛠️ Configuração da API

O sistema se conecta a uma API REST. Configure em `config/settings.json`:

- `api_base`: URL base da API do WMS
- `timeout`: Timeout das requisições (segundos)

## 📝 Logging

Os logs são salvos em `logs/application.log` e incluem:
- Tentativas de login (sucesso/falha)
- Ações dos usuários
- Erros de sistema
- Comunicação com API

## 🎨 Interface Gráfica

### Tela de Login
- Campo CPF com formatação automática (000.000.000-00)
- Validação em tempo real
- Campo senha protegido
- Feedback visual de status

### Menu Principal
- Botões grandes e intuitivos
- Ícones visuais para cada função
- Informações do usuário logado
- Opção de logout seguro

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/application.log`
2. Confirme as configurações em `config/settings.json`
3. Teste a conectividade com a API

## 🔧 Desenvolvimento

Para contribuir com o projeto:

1. Certifique-se de que os testes passam
2. Mantenha o padrão de código existente
3. Documente novas funcionalidades
4. Atualize este README se necessário

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Features

- User authentication with login functionality.
- API client for managing requests and responses.
- Label printing capabilities using ZPL.
- User interface for interacting with the application.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd printing-service
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config/settings.json`.

4. Set up environment variables as needed in the `.env` file.

## Usage

To start the application, run the following command:
```
python src/main.py
```

Follow the on-screen instructions to log in and print labels.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.