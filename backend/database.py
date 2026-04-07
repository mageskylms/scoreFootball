from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Obtém a string de conexão via variável de ambiente (prática recomendada para segurança e flexibilidade).
# O valor padrão aponta para o serviço "db" configurado no docker-compose.yml.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@db:5432/scorefootball")

# Cria a "engine", que é o motor principal do SQLAlchemy. 
# Ele gerencia o pool de conexões com o banco de dados PostgreSQL.
engine = create_engine(DATABASE_URL)

# Cria uma fábrica de sessões (SessionLocal) para interagir com o banco.
# autocommit=False: Exige que chamemos db.commit() explicitamente (transações seguras e reversíveis caso haja erro).
# autoflush=False: Evita que o SQLAlchemy envie queries incompletas ao banco automaticamente antes do momento certo.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Retorna uma classe base. Todos os nossos modelos ORM (tabelas) no arquivo models.py vão herdar dela 
# para que o SQLAlchemy saiba como mapear as classes Python para tabelas reais no banco de dados.
Base = declarative_base()

# Função geradora (Dependency Injection) que o FastAPI usa em cada rota.
def get_db():
    # Abre uma nova sessão de banco de dados para a requisição HTTP atual
    db = SessionLocal()
    try:
        # O "yield" pausa a função e entrega a sessão para a rota usar durante o processamento
        yield db
    finally:
        # O bloco "finally" garante que a conexão será fechada e devolvida ao pool ao final da requisição,
        # MESMO se ocorrer algum erro na rota. Isso previne o esgotamento das conexões do banco de dados (connection leak).
        db.close()