from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

# Arquivo responsável por definir os modelos de dados (ORM - Object-Relational Mapping).
# O SQLAlchemy traduzirá essas classes Python para tabelas e colunas reais no PostgreSQL.

class Classificacao(Base):
    # Nome exato da tabela que será criada no banco de dados
    __tablename__ = "classificacao"

    # Chave primária (ID único). index=True cria um índice no banco para acelerar buscas por esse campo.
    id = Column(Integer, primary_key=True, index=True)
    posicao = Column(Integer)
    # Criamos um índice no nome_time pois fazemos muitas filtragens/buscas específicas por time nos serviços preditivos
    nome_time = Column(String, index=True)
    pontos = Column(Integer)
    jogos = Column(Integer)
    vitorias = Column(Integer)
    empates = Column(Integer)
    derrotas = Column(Integer)
    saldo_gols = Column(Integer)
    temporada = Column(String)
    gols_feitos = Column(Integer) 
    gols_sofridos = Column(Integer) 
    
class Atualizacao(Base):
    # Tabela simples de auditoria/controle para sabermos quando ocorreu a última sincronização com a API externa
    __tablename__ = "atualizacao"

    id = Column(Integer, primary_key=True, index=True)
    # O server_default=func.now() delega ao próprio motor do PostgreSQL a tarefa de preencher 
    # a data e hora exatas no momento da inserção, garantindo precisão independente do fuso do servidor Python.
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    
class PartidaFutura(Base):
    # Tabela para armazenar a agenda de jogos pendentes do campeonato.
    # É a base fundamental para rodarmos as projeções avançadas e as simulações de Monte Carlo.
    __tablename__ = "partida_futura"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(DateTime(timezone=True))
    rodada = Column(Integer)
    time_mandante = Column(String)
    time_visitante = Column(String)