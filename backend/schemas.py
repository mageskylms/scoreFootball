from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Arquivo responsável por definir os esquemas (schemas) de validação de dados usando a biblioteca Pydantic.
# Esses modelos garantem que a API receba e retorne estritamente os tipos de dados esperados.
# Além disso, o FastAPI usa essas classes para gerar a documentação interativa (Swagger UI) automaticamente.

# --- STATUS E JSONS BRUTOS ---

class StatusResponse(BaseModel):
    status: str
    mensagem: str

# O tipo "Any" é usado aqui pois os dados brutos da API externa podem ter formatos variáveis e complexos
class JsonsResponse(BaseModel):
    classificacao: Any
    jogos: Any

class SyncResponse(BaseModel):
    status: str
    mensagem: str
    # O 'alias' permite que a chave real no JSON retornado seja "Dados usados: ", 
    # enquanto no código Python usamos o nome válido "dados_usados".
    dados_usados: Optional[Any] = Field(None, alias="Dados usados: ")

# --- CLASSIFICAÇÃO ---

class TimeClassificacao(BaseModel):
    id: int
    posicao: int
    nome_time: str
    pontos: int
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    saldo_gols: int
    temporada: str
    gols_feitos: int
    gols_sofridos: int

    class Config:
        # Configuração crucial: Permite que o Pydantic leia dados diretamente de objetos ORM do SQLAlchemy 
        # (e não apenas de dicionários Python originais), convertendo-os perfeitamente para JSON.
        from_attributes = True 

class ClassificacaoResponse(BaseModel):
    status: str
    fonte: str
    gols_campeonato: float
    partidas_registradas: float
    # Mapeia a variável Python sem acento para a chave com acento desejada no JSON final
    media_gols_por_partida: float = Field(..., alias="média_gols_por_partida")
    classificacao: List[TimeClassificacao]

# --- PRÓXIMOS JOGOS ---

class Jogo(BaseModel):
    data: str
    hora: str
    rodada: int
    mandante: str
    visitante: str

class ProximosJogosResponse(BaseModel):
    status: str
    total_jogos: int
    rodadas: Dict[str, List[Jogo]]

# --- TENDÊNCIA BÁSICA ---

class InsightTendencia(BaseModel):
    mensagem: str
    campeao_previsto: str

class DestaquesAtuais(BaseModel):
    mais_vitorias_reais: str
    melhor_ataque_saldo: str

class AnaliseDetalhada(BaseModel):
    posicao_atual: int
    time: str
    aproveitamento: str
    media_atual: str
    tendencia_final_38_rodadas: float
    status_projetado: str

class TendenciaResponse(BaseModel):
    insight_de_tendencia: InsightTendencia
    analise_detalhada: List[AnaliseDetalhada]
    destaques_atuais: DestaquesAtuais

# --- ESTATÍSTICAS REAIS ---

class PanoramaGeral(BaseModel):
    total_partidas_registradas: float
    rodada_media_atual: float
    total_gols: float

class ExtremoValor(BaseModel):
    time: str
    valor: int

class ExtremoGols(BaseModel):
    time: str
    gols: int

class ExtremosCampeonato(BaseModel):
    maior_vitorioso: ExtremoValor
    o_que_mais_empata: ExtremoValor
    o_que_mais_perdeu: ExtremoValor
    melhor_ataque: ExtremoGols
    pior_defesa: ExtremoGols
    lider: str
    lanterna: str

class ZonasAtuais(BaseModel):
    G4_Libertadores: List[str]
    G5_Pre_Libertadores: List[str]
    G6_Sul_Americana: List[str]
    Z4_Rebaixamento: List[str]

class TopEstatistica(BaseModel):
    nome: str
    gols_feitos: Optional[int] = None
    gols_sofridos: Optional[int] = None
    media_gol_por_partida: str

class Rankings(BaseModel):
    top_4_goleadores: List[TopEstatistica]
    top_4_mais_tomam_gols: List[TopEstatistica]

class EstatisticasReaisResponse(BaseModel):
    panorama_geral: PanoramaGeral
    extremos_do_campeonato: ExtremosCampeonato
    zonas_atuais: ZonasAtuais
    rankings: Rankings

# --- TENDÊNCIA POR FREQUÊNCIA ---

class TabelaProjetada(BaseModel):
    time: str
    jogos_atuais: int
    frequencia_vitoria: str
    expectativa_pts_pj: str
    pontos_atuais: int
    projecao_final_38_rodadas: str
    # Mapeia a string com espaço ("ranking atual") para uma variável Python válida
    ranking_atual: int = Field(..., alias="ranking atual")
    ranking_projetado: int

class TendenciaFrequenciaResponse(BaseModel):
    status: str
    metodologia: str
    previsao_campeao: str
    tabela_projetada: List[TabelaProjetada]

# --- PREVISÕES AVANÇADAS E POWER RANKING ---

class PowerRankingItem(BaseModel):
    time: str
    posicao_real: int
    ataque: float
    defesa: float
    score: float
    posicao_forca: int
    delta: int

class PrevisaoAvancadaItem(BaseModel):
    time: str
    pontos_atuais: int
    projecao_final: float
    posicao_real: int
    posicao_projetada: int
    delta: int

class PrevisaoAvancadaResponse(BaseModel):
    metodologia: str
    previsao: List[PrevisaoAvancadaItem]

class PrevisaoMonteCarloItem(BaseModel):
    time: str
    pontos_medios: float
    # O caractere '%' é ilegal em nomes de variáveis no Python, por isso o uso obrigatório do alias aqui.
    chance_titulo_perc: float = Field(..., alias="chance_titulo_%")
    chance_g4_perc: float = Field(..., alias="chance_g4_%")
    chance_rebaixamento_perc: float = Field(..., alias="chance_rebaixamento_%")

class PrevisaoMonteCarloResponse(BaseModel):
    metodologia: str
    previsao: List[PrevisaoMonteCarloItem]