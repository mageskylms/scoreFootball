
from fastapi import FastAPI, Depends
from routes import router as brasileirao_router
import models
from database import engine
from fastapi.middleware.cors import CORSMiddleware

# Ponto de entrada (Entry Point) da aplicação FastAPI.
# O servidor ASGI (Uvicorn) configurado no Dockerfile procura pela instância "app" declarada neste arquivo.

# Inicializa o banco de dados: 
# Verifica se as tabelas definidas em models.py existem no PostgreSQL e as cria caso não existam.
models.Base.metadata.create_all(bind=engine)

# Inicialização e configuração central da API FastAPI.
# Esses metadados são exibidos na documentação interativa gerada automaticamente no endpoint /docs (Swagger UI).
app = FastAPI(
    title="ScoreFootball API",
    description="API para análise e previsões do Brasileirão",
    version="1.4.0",
    debug=True,
)

# Configuração de CORS (Cross-Origin Resource Sharing).
# O CORS é um mecanismo de segurança dos navegadores que bloqueia requisições HTTP feitas 
# de um domínio/porta (frontend) para outro diferente (backend). 
# Aqui, permitimos explicitamente as origens do nosso frontend para evitar o famoso erro de "CORS Policy".
app.add_middleware(
    CORSMiddleware,
    # Permite acesso via Live Server (VS Code) e via container Nginx (Docker)
    allow_origins=["http://127.0.0.1:5500", "http://localhost:3000"], 
    # Permite que o frontend use qualquer método HTTP (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],  
    # Permite o envio de qualquer cabeçalho na requisição (ex: Authorization, Content-Type)
    allow_headers=["*"],  
)

# Inclusão das rotas modulares.
# Em vez de poluir o main.py com dezenas de endpoints, importamos o router configurado no routes.py,
# mantendo o código limpo, organizado e com separação de responsabilidades (Clean Code).
app.include_router(brasileirao_router)