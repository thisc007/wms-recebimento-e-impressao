# Printing Service

This project is a printing service application that allows users to authenticate and print labels using ZPL (Zebra Programming Language). The application is structured into several modules for better organization and maintainability.

## Project Structure

```
printing-service
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── auth
│   │   ├── __init__.py
│   │   └── login.py
│   ├── api
│   │   ├── __init__.py
│   │   └── client.py
│   ├── printer
│   │   ├── __init__.py
│   │   ├── label_printer.py
│   │   └── zpl_generator.py
│   ├── ui
│   │   ├── __init__.py
│   │   └── menu.py
│   └── utils
│       ├── __init__.py
│       ├── logger.py
│       └── config.py
├── config
│   └── settings.json
├── logs
│   └── .gitkeep
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

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