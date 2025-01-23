# Aplicação Flask

Este é um projeto simples desenvolvido em Flask.

## **Pré-requisitos**

Certifique-se de que você possui os seguintes itens instalados em sua máquina:
- Python 3.7 ou superior
- `pip` (gerenciador de pacotes do Python)
- Git

## **Passos para execução**

### 1. Clone o repositório
Abra um terminal e execute o comando abaixo para clonar o repositório:
```bash
git clone https://github.com/KauanHK/blog.git
```

### 2. Navegue até o diretório do projeto
Entre no diretório clonado:
```bash
cd blog
```

### 3. Crie e ative um ambiente virtual (opcional)
Crie um ambiente virtual para isolar as dependências do projeto:
```bash
python -m venv .venv
```

Ative o ambiente virtual:
- **Windows**:
    ```bash
    .venv\Scripts\activate
    ```
- **Linux/Mac**:
    ```bash
    source .venv/bin/activate
    ```

### 4. Instale as dependências
Com o ambiente virtual ativo, instale as dependências listadas abaixo:
```bash
pip install flask
pip install pytest  # opcional, para rodar os testes
```

### 6. Execute a aplicação
Execute o seguinte comando para inicializar o banco de dados.
```bash
flask --app blog init-db
```
Agora, você já pode executar a aplicação:
```bash
flask --app blog run
```

Se tudo estiver configurado corretamente, a aplicação estará rodando em [http://127.0.0.1:5000](http://127.0.0.1:5000).
