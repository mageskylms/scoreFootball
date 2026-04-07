from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db
import service 
import schemas
from typing import List

# Arquivo de Rotas (Controllers / Endpoints).
# Este arquivo atua como o "garçom" da nossa API: ele recebe a requisição do usuário (ou frontend),
# valida a estrutura de dados esperada de entrada/saída através do Pydantic (schemas.py) 
# e delega o "trabalho pesado" e cálculos (regras de negócio) para o arquivo service.py.
# Essa separação mantém o código extremamente limpo, organizado e facilita a manutenção.

# Rotas relacionadas ao Brasileirão

# Utilização do APIRouter para modularizar a aplicação. 
# O prefixo "/brasileirao" garante que todos os endpoints abaixo comecem com esse caminho padrão.
router = APIRouter(prefix="/brasileirao")

# O parâmetro "response_model" em cada rota garante que a API sempre respeite o contrato de dados.
# O "summary" e as "tags" e a Docstring (""") são capturados magicamente pelo FastAPI para gerar o /docs (Swagger).
@router.get("/", summary="Status da API", tags=["Status"], response_model=schemas.StatusResponse, responses={200: {"description": "A API do ScoreFootball está online! 🚀"}})
def read_root():
    """
    Verifica o status de funcionamento da API.
    Retorna uma mensagem simples confirmando que a aplicação está online.
    """
    return {
        "status": "sucesso", 
        "mensagem": "A API do ScoreFootball está online! 🚀"
    }

@router.get("/jsons", summary="Obter dados brutos (JSON)", tags=["Dados Brutos"], response_model=schemas.JsonsResponse)
def get_jsons(db: Session = Depends(get_db)):
    """
    Faz uma requisição direta para a API do `football-data.org` e retorna os dados brutos 
    da classificação atual e dos próximos jogos agendados da competição.
    """
    return service.get_json(db)

@router.get("/sync/dados", summary="Sincronizar dados do campeonato" , tags=["Sync"], response_model=schemas.SyncResponse)
def sync_classificacao(db: Session = Depends(get_db)):
    """
    Busca a classificação atualizada e a agenda de partidas futuras na API externa.
    Em seguida, limpa os registros antigos e atualiza o banco de dados local (PostgreSQL) 
    com os dados mais recentes.
    """
    return service.sync_dados(db)

@router.get(
            "/proximos-jogos",
            summary="Listar próximos jogos",
            tags=["Jogos"],
            response_model=schemas.ProximosJogosResponse)
def proximos_jogos(db: Session = Depends(get_db)):
    """
    Retorna a lista de todas as partidas futuras agendadas salvas no banco de dados local.
    Os jogos são formatados com data, hora e agrupados automaticamente por rodada.
    """
    return service.get_proximos_jogos(db)

@router.get("/classificacao", summary="Tabela de Classificação", tags=["Classificação"], response_model=schemas.ClassificacaoResponse)
def get_classificacao_local(db: Session = Depends(get_db)):
    """
    Retorna a tabela de classificação atual do campeonato extraída do banco de dados local.
    Inclui estatísticas básicas globais da liga, como total de gols, partidas e a média de gols por partida.
    """
    return service.get_classificacao(db)

@router.get("/tendencia", summary="Análise de Tendência (Média)", tags=["Previsões"], response_model=schemas.TendenciaResponse)
def get_estatisticas_tendencia(db: Session = Depends(get_db)):
    """
    Realiza uma projeção de pontuação final para 38 rodadas baseada na média atual de 
    pontos por partida de cada time. Retorna também os times projetados para ser o campeão, 
    zona de Libertadores (G4/G5), Sul-Americana (G6) e os riscos de rebaixamento (Z4).
    """
    return service.get_tendencia(db)
    
@router.get("/estatisticas/reais", summary="Estatísticas Gerais e Extremos", tags=["Estatísticas"], response_model=schemas.EstatisticasReaisResponse)
def get_estatisticas_reais(db: Session = Depends(get_db)):
    """
    Fornece um panorama geral do campeonato com dados reais do banco.
    Destaca os 'extremos' da competição (maior vitorioso, pior defesa, o que mais perde, etc.),
    os times que ocupam cada zona da tabela e o ranking dos top 4 ataques e defesas.
    """
    return service.get_estatisticas_reais(db)
    
@router.get("/tendencia/frequencia", summary="Tendência por Frequência", tags=["Previsões"], response_model=schemas.TendenciaFrequenciaResponse)
def get_tendencia_frequencia(db: Session = Depends(get_db)):
    """
    Calcula a projeção de pontos esperados ao final de 38 rodadas utilizando a 
    frequência relativa de Vitórias, Empates e Derrotas que cada equipe tem até o momento.
    """
    return service.get_tendencia_frequencia(db)

@router.get("/power-ranking", summary="Power Ranking", tags=["Previsões"], response_model=List[schemas.PowerRankingItem])
def get_power_ranking(db: Session = Depends(get_db)):
    """
    Gera um ranking de força medindo a qualidade de Ataque e Defesa de cada time 
    em comparação com as médias de gols da liga. Retorna um score e a diferença 
    entre a posição real do time na tabela e a sua posição no Power Ranking (delta).
    """
    return service.power_ranking(db)

@router.get("/tendencia/avancada", summary="Previsão Avançada de Resultados", tags=["Previsões"], response_model=schemas.PrevisaoAvancadaResponse)
def get_tendencia_avancada(db: Session = Depends(get_db)):
    """
    Utiliza uma simulação probabilística com base nos gols esperados (Ataque x Defesa) 
    e na vantagem do mando de field para projetar o resultado de todos os jogos restantes 
    e calcular a pontuação final de cada time ao término do campeonato.
    """
    return service.previsao_avancada(db)

@router.get("/previsao/monte-carlo", summary="Simulação de Monte Carlo", tags=["Previsões"], response_model=schemas.PrevisaoMonteCarloResponse)
def get_previsao_monte_carlo(db: Session = Depends(get_db)):
    """
    Executa múltiplas simulações (1000 vezes) das partidas futuras restantes utilizando 
    a distribuição de Poisson para prever as probabilidades estatísticas (em %) de título, 
    classificação para o G4 e chance de rebaixamento para cada equipe.
    """
    return service.previsao_monte_carlo(db)