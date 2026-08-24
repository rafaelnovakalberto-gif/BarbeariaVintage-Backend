


Backend: Python, FastAPI, SQLite, bcrypt (hash de senha)
Frontend: Python, Streamlit
Automação: n8n (envio de email ao criar agendamento)

## Como rodar o projeto

Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
source venv/bin/activate     

pip install -r requirements.txt
```

Crie o primeiro usuário (funcionário autorizado a acessar o sistema):

```bash
python
>>> import database
>>> database.create_tables()
>>> database.create_user("seu_usuario", "sua_senha")
>>> exit()
```

Ligue o servidor:

```bash
uvicorn main:app --reload
```

A API vai rodar em `http://localhost:8000`.

Frontend:

Em outro terminal:

```bash
cd frontend
python -m venv venv
venv\Scripts\activate
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

O sistema abre automaticamente no navegador, em `http://localhost:8501`.

**Importante**: o backend precisa estar rodando (passo 1) para o frontend funcionar, já que o Streamlit consome a API.

n8n:

O workflow do n8n (arquivo `n8n-workflow.json`, na raiz do repositório) recebe os dados de um agendamento recém-criado e envia um email de confirmação ao cliente.

para utiliza-lo basta importar o arquivo `n8n-workflow.json` dentro da platarforma e executar a partir do production URL 

## Funcionalidades

- Login restrito a funcionários autorizados
- Cadastro, edição e remoção de clientes
- Criação, edição de status e remoção de agendamentos
- Visualização da agenda organizada por data e horário
- Envio automático de email de confirmação ao cliente, via n8n, quando um agendamento é criado

Crie o primeiro usuário (administrador):

python seed.py