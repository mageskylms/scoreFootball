# 🌐 ScoreFootball - Backend API (FastAPI)

Este diretório contém o coração da lógica de negócio e da API REST do projeto ScoreFootball, desenvolvida com FastAPI. Ela é responsável por interagir com o banco de dados (PostgreSQL), consumir dados de APIs externas e realizar todos os cálculos e simulações preditivas.

---

## 🚀 Tecnologias e Ferramentas

- **[FastAPI](https://fastapi.tiangolo.com/):** Framework web assíncrono de alta performance para a construção da API.
- **[Uvicorn](https://www.uvicorn.org/):** Servidor ASGI utilizado para rodar a aplicação FastAPI.
- **[SQLAlchemy](https://www.sqlalchemy.org/):** ORM (Object-Relational Mapper) para manipulação do banco de dados.
- **[Pydantic](https://pydantic-docs.helpmanual.io/):** Biblioteca para validação de dados e serialização/desserialização, integrada nativamente ao FastAPI.
- **[PostgreSQL](https://www.postgresql.org/):** Banco de dados relacional para persistência de dados.
- **[Requests](https://docs.python-requests.org/):** Biblioteca para requisições HTTP (para consumir a API externa football-data.org).
- **[NumPy](https://numpy.org/):** Biblioteca essencial para computação numérica, utilizada nos modelos de simulação (Poisson, Monte Carlo).
- **[Python ZoneInfo]:** Módulo para gerenciamento preciso de fusos horários.
- **[python-dotenv]:** (Opcional, para rodar sem Docker) Biblioteca para carregar variáveis de ambiente de um arquivo `.env`.

---

## ⚙️ Como Executar Localmente (Sem Docker)

Se você deseja desenvolver ou testar apenas o backend sem usar o Docker Compose, siga os passos abaixo:

### 1. Pré-requisitos
- Python 3.11 instalado na sua máquina.
- `pip` (gerenciador de pacotes do Python).

### 2. Ambiente Virtual
É altamente recomendável usar um ambiente virtual para gerenciar as dependências do projeto.

```bash
# Navegue até a pasta do backend
> cd backend

# Crie o ambiente virtual
> python -m venv venv

# Ative o ambiente virtual
# No Windows:
> .\venv\Scripts\activate
# No macOS/Linux:
> source venv/bin/activate
```

### 3. Instalar Dependências
Com o ambiente virtual ativado, instale as bibliotecas listadas no `requirements.txt`:

```bash
(venv) > pip install -r requirements.txt
```

### 4. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do diretório `backend/` para configurar a chave da API externa e a URL do banco de dados (se não estiver usando o Docker Compose para o banco):

```env
# .env (dentro de backend/)
API_KEY=sua_chave_da_api_aqui
DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/scorefootball # Ou a URL do seu DB local
```

**Nota:** Se for usar um PostgreSQL local, certifique-se de que ele esteja rodando e acessível. Caso contrário, o `docker-compose.yml` da raiz é o método recomendado para subir o banco de dados.

### 5. Iniciar o Servidor
Com todas as dependências instaladas e o ambiente virtual ativado, inicie a API:

```bash
(venv) > uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`.

### 6. Documentação da API (Swagger UI)
Acesse a documentação interativa da API em `http://localhost:8000/docs`. Lá você encontrará todos os endpoints, modelos de dados e poderá testar as requisições.

---

## 📂 Estrutura do Diretório

- `main.py`: Ponto de entrada da aplicação FastAPI, configurações globais e middlewares (CORS).
- `routes.py`: Define todos os endpoints da API (`/brasileirao/...`), utilizando o `APIRouter` para modularização.
- `service.py`: Contém a lógica de negócio principal, integração com a API externa e os algoritmos preditivos (tendências, Power Ranking, Monte Carlo).
- `models.py`: Modelos de dados do SQLAlchemy que mapeiam as classes Python para tabelas no PostgreSQL.
- `schemas.py`: Schemas Pydantic para validação de entrada/saída e documentação da API.
- `database.py`: Configurações de conexão com o banco de dados (SQLAlchemy Engine e SessionLocal).
- `requirements.txt`: Lista de todas as dependências Python do projeto.
- `Dockerfile`: Instruções para construir a imagem Docker do backend.
