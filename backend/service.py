import os
from datetime import datetime
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import cast
import models
import numpy as np
from zoneinfo import ZoneInfo
from collections import defaultdict

# Arquivo de Serviço (Service Layer).
# Concentra toda a regra de negócio, integrações com APIs externas e algoritmos matemáticos preditivos.
# Essa separação evita que o arquivo routes.py fique poluído com cálculos, facilitando manutenções e testes.

# --- CONFIGURAÇÕES DA API ---
# Chave de acesso e código do campeonato para a API externa football-data.org
API_KEY = os.getenv("API_KEY")
COMPETITION = "BSA" # Código do Brasileirão Série A

def get_json(db: Session):
    url_classificacao = f"https://api.football-data.org/v4/competitions/{COMPETITION}/standings"
    url_jogos = f"https://api.football-data.org/v4/competitions/{COMPETITION}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": API_KEY}
    
    try:
        resp_class = requests.get(url_classificacao, headers=headers)
        if resp_class.status_code != 200:
            raise HTTPException(status_code=resp_class.status_code, detail="Erro ao buscar classificação.")
            
        dados_class = resp_class.json()
        
        resp_jogos = requests.get(url_jogos, headers=headers)
        if resp_jogos.status_code != 200:
            raise HTTPException(status_code=resp_jogos.status_code, detail="Erro ao buscar próximos jogos.")
        
        dados_jogos = resp_jogos.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {str(e)}")    
        
    return {"classificacao": dados_class, "jogos": dados_jogos}

def sync_dados(db: Session):
    # Função orquestradora que atualiza o banco de dados local com as informações mais recentes da web.
    url_classificacao = f"https://api.football-data.org/v4/competitions/{COMPETITION}/standings"
    url_jogos = f"https://api.football-data.org/v4/competitions/{COMPETITION}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": API_KEY}
    print(f"[DEBUG] Sincronizando dados da API... {API_KEY}")
    try:
        # 1. Puxa a Classificação
        resp_class = requests.get(url_classificacao, headers=headers)
        if resp_class.status_code != 200:
            raise HTTPException(status_code=resp_class.status_code, detail="Erro ao buscar classificação.")
            
        dados_class = resp_class.json()
        tabela_bruta = dados_class["standings"][0]["table"]
        temporada_atual = str(dados_class["season"]["startDate"][:4])
        
        # Limpa os dados antigos para evitar duplicidade.
        # Uma alternativa em bancos maiores seria usar UPSERT (Update/Insert) com merge.
        db.query(models.Classificacao).delete()
        db.query(models.Atualizacao).delete()
        
        for time in tabela_bruta:
            novo_time = models.Classificacao(
                posicao=time["position"], nome_time=time["team"]["shortName"],
                pontos=time["points"], jogos=time["playedGames"],
                vitorias=time["won"], empates=time["draw"], derrotas=time["lost"],
                gols_feitos=time["goalsFor"], gols_sofridos=time["goalsAgainst"],
                saldo_gols=time["goalDifference"], temporada=temporada_atual
            )
            db.add(novo_time)
            
        # 2. Puxa a Agenda de Jogos
        resp_jogos = requests.get(url_jogos, headers=headers)
        if resp_jogos.status_code == 200:
            dados_jogos = resp_jogos.json()
            db.query(models.PartidaFutura).delete()
            
        for match in dados_jogos.get("matches", []):
            # A API retorna o horário em UTC. Salvamos o timezone exato para garantir
            # que não haverá problemas de exibição independente de onde o servidor estiver hospedado.
            data_convertida = datetime.fromisoformat(
                match["utcDate"].replace("Z", "+00:00")
            )

            nova_partida = models.PartidaFutura(
                data=data_convertida,
                rodada=match.get("matchday", 0),
                time_mandante=match["homeTeam"]["shortName"],
                time_visitante=match["awayTeam"]["shortName"]
            )

            db.add(nova_partida)

        db.add(models.Atualizacao())
        # Efetiva as transações no banco de dados todas de uma vez (segurança transacional)
        db.commit() 
        
        return {"status": "sucesso", "mensagem": "Classificação e Agenda atualizadas!"}
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {str(e)}")

def get_classificacao(db: Session):
    times = db.query(models.Classificacao).order_by(models.Classificacao.posicao.asc()).all()
    
    if not times:
        raise HTTPException(status_code=404, detail="Banco de dados vazio. Acesse /sync/classificacao para puxar os dados da internet primeiro.")
    
    gols_campeonato: float = 0
    partidas_campeonato: float = 0
    
    for t in times:
        gols_campeonato += cast(float, t.gols_feitos)
        partidas_campeonato += cast(float, t.jogos / 2)
        
    # Calcula a média da liga para ser usada nas projeções estatísticas.
    media_gols_por_partida = round(gols_campeonato / partidas_campeonato, 2) if partidas_campeonato > 0 else 0
        
    return {
        "status": "sucesso",
        "fonte": "Banco de Dados Local (PostgreSQL)",
        "gols_campeonato": gols_campeonato,
        "partidas_registradas": partidas_campeonato,
        "média_gols_por_partida": media_gols_por_partida,
        "classificacao": times,
    }
    
def get_proximos_jogos(db: Session):
    partidas = db.query(models.PartidaFutura)\
        .order_by(models.PartidaFutura.rodada.asc())\
        .all()
    
    if not partidas:
        raise HTTPException(status_code=404, detail="Sem jogos futuros cadastrados.")

    rodadas_map = defaultdict(list)

    for p in partidas:
        data_local = p.data.astimezone(ZoneInfo("America/Sao_Paulo"))

        jogo = {
            "data": data_local.date().strftime("%d-%m-%Y"),
            "hora": data_local.time().strftime("%H:%M"),
            "rodada": p.rodada,
            "mandante": p.time_mandante,
            "visitante": p.time_visitante
        }

        rodadas_map[p.rodada].append(jogo)

    rodadas = [
        {
            "numero": rodada,
            "jogos": jogos
        }
        for rodada, jogos in sorted(rodadas_map.items())
    ]

    return {
        "status": "sucesso",
        "total_jogos": sum(len(j) for j in rodadas_map.values()),
        "rodadas": rodadas
    }
    
def get_tendencia(db: Session):
    # Projeção linear simples (Regra de Três): Assume que o time manterá exatamente o mesmo aproveitamento até a rodada 38.
    times = db.query(models.Classificacao).order_by(models.Classificacao.posicao.asc()).all()
    
    if not times:
        raise HTTPException(status_code=404, detail="Sem dados no banco. Sincronize primeiro.")

    relatorio_completo = []
    RODADAS_TOTAIS: int = 38

    for t in times:
        pontos_possiveis = t.jogos * 3
        aproveitamento = (t.pontos / pontos_possiveis) * 100 
        media_pontos = t.pontos / t.jogos 
        
        projecao_final = media_pontos * RODADAS_TOTAIS
        
        relatorio_completo.append({
            "posicao_atual": t.posicao,
            "time": t.nome_time,
            "aproveitamento": f"{aproveitamento:.2f}%",
            "media_atual": f"{media_pontos:.2f}",
            "tendencia_final_38_rodadas": projecao_final,
            "status_projetado": "" 
        })

    relatorio_completo.sort(key=lambda x: x["tendencia_final_38_rodadas"], reverse=True)

    for i, time_proj in enumerate(relatorio_completo):
        if i == 0:
            time_proj["status_projetado"] = "🏆 Campeão Projetado"
        elif i < 4:
            time_proj["status_projetado"] = "🔵 G4 (Libertadores)"
        elif i == 4:
            time_proj["status_projetado"] = "🟡 G5 (Pré-Libertadores)"
        elif i < 11:
            time_proj["status_projetado"] = "🟠 G6 (Sul-Americana)"
        elif i >= 16:
            time_proj["status_projetado"] = "⚠️ Risco de Rebaixamento (Z4)"
        else:
            time_proj["status_projetado"] = "⚪ Meio de Tabela"

    relatorio_completo.sort(key=lambda x: x["posicao_atual"])

    mais_vitorias = max(times, key=lambda x: x.vitorias)
    melhor_projecao = max(relatorio_completo, key=lambda x: x["tendencia_final_38_rodadas"])

    return {
        "insight_de_tendencia": {
            "mensagem": f"Baseado na média atual de pontos/partida, o campeão deve atingir aprox. {melhor_projecao['tendencia_final_38_rodadas']} pontos.",
            "campeao_previsto": melhor_projecao["time"]
        },
        "analise_detalhada": relatorio_completo,
        "destaques_atuais": {
            "mais_vitorias_reais": mais_vitorias.nome_time,
            "melhor_ataque_saldo": max(times, key=lambda x: x.saldo_gols).nome_time
        }
    }

def get_estatisticas_reais(db: Session):
    # Extrai insights rápidos varrendo a base de dados (melhores/piores da competição).
    times = db.query(models.Classificacao).order_by(models.Classificacao.posicao.asc()).all()
    if not times:
        raise HTTPException(status_code=404, detail="Sincronize os dados primeiro.")
    
    mais_vitorioso = max(times, key=lambda x: x.vitorias)
    mais_empata = max(times, key=lambda x: x.empates)
    mais_perdeu = max(times, key=lambda x: x.derrotas)
    melhor_ataque = max(times, key=lambda x: x.gols_feitos)
    pior_defesa = max(times, key=lambda x: x.gols_sofridos)
    mais_pontos = times[0] 
    menos_pontos = times[-1]
    gols = sum(t.gols_feitos for t in times)
    
    ranking_4_goleadores = sorted(times, key=lambda x: x.gols_feitos, reverse=True)[:4]
    ranking_4_mais_tomam_gols = sorted(times, key=lambda x: x.gols_sofridos, reverse=True)[:4]
    
    g4 = [t.nome_time for t in times[:4]]
    g5 = [t.nome_time for t in times[4:5]]
    g6 = [t.nome_time for t in times[6:11]]
    z4 = [t.nome_time for t in times[-4:]]

    return {
        "panorama_geral": {
            "total_partidas_registradas": (sum(t.jogos for t in times) / 2),
            "rodada_media_atual": max(t.jogos for t in times),
            "total_gols": gols
        },
        "extremos_do_campeonato": {
            "maior_vitorioso": {"time": mais_vitorioso.nome_time, "valor": mais_vitorioso.vitorias},
            "o_que_mais_empata": {"time": mais_empata.nome_time, "valor": mais_empata.empates},
            "o_que_mais_perdeu": {"time": mais_perdeu.nome_time, "valor": mais_perdeu.derrotas},
            "melhor_ataque": {"time": melhor_ataque.nome_time, "gols": melhor_ataque.gols_feitos},
            "pior_defesa": {"time": pior_defesa.nome_time, "gols": pior_defesa.gols_sofridos},
            "lider": mais_pontos.nome_time,
            "lanterna": menos_pontos.nome_time
        },
        "zonas_atuais": {
            "G4_Libertadores": g4,
            "G5_Pre_Libertadores": g5,
            "G6_Sul_Americana": g6,
            "Z4_Rebaixamento": z4
        },
        "rankings": {
            "top_4_goleadores": [{"nome": t.nome_time, "gols_feitos": t.gols_feitos, "media_gol_por_partida": f"{(t.gols_feitos / t.jogos):.2f}"} for t in ranking_4_goleadores],
            "top_4_mais_tomam_gols": [{"nome": t.nome_time, "gols_sofridos": t.gols_sofridos, "media_gol_por_partida": f"{(t.gols_sofridos / t.jogos):.2f}"} for t in ranking_4_mais_tomam_gols]
        }
    }

def get_tendencia_frequencia(db: Session):
    # Projeção baseada em Expectância: Multiplica a frequência de V/E/D pelos pontos correspondentes (3/1/0).
    times = db.query(models.Classificacao).all()
    if not times:
        raise HTTPException(status_code=404, detail="Sincronize os dados primeiro.")

    RODADAS_TOTAIS = 38
    projecao_lista = []

    for t in times:
        jogos_restantes = RODADAS_TOTAIS - t.jogos
        
        freq_vitoria = t.vitorias / t.jogos 
        freq_empate = t.empates / t.jogos 
        
        expectativa_pontos_por_jogo = (freq_vitoria * 3) + (freq_empate * 1)
        pontos_projetados_finais = t.pontos + (jogos_restantes * expectativa_pontos_por_jogo)
        
        projecao_lista.append({
            "time": t.nome_time,
            "jogos_atuais": t.jogos,
            "frequencia_vitoria": f"{(freq_vitoria * 100):.2f}%",
            "expectativa_pts_pj": f"{expectativa_pontos_por_jogo:.2f}",
            "pontos_atuais": t.pontos,
            "projecao_final_38_rodadas": f"{pontos_projetados_finais:.1f}",
            "ranking atual": t.posicao
        })

    projecao_lista.sort(key=lambda x: x["projecao_final_38_rodadas"], reverse=True)

    for i, item in enumerate(projecao_lista):
        item["ranking_projetado"] = i + 1

    return {
        "status": "sucesso",
        "metodologia": "Frequência Relativa de Resultados (V/E/D)",
        "previsao_campeao": projecao_lista[0]["time"] if projecao_lista else "N/A",
        "tabela_projetada": projecao_lista
    }
    
def power_ranking(db: Session):
    # Cria um índice de força isolando o desempenho do time da posição na tabela.
    # Ajuda a identificar se um time está com "sorte" (posição alta, índice baixo) ou "azar" (posição baixa, índice alto).
    times = db.query(models.Classificacao).all()

    total_gols = sum(t.gols_feitos for t in times)
    total_jogos = sum(t.jogos for t in times) / 2
    media_liga = total_gols / total_jogos

    ranking = []

    for t in times:
        ataque = (t.gols_feitos / t.jogos)
        defesa = t.gols_sofridos / t.jogos

        forca_ataque = ataque / media_liga
        forca_defesa = defesa / media_liga

        # Score: Razão entre a força ofensiva e a vulnerabilidade defensiva.
        score = forca_ataque / forca_defesa

        ranking.append({
            "time": t.nome_time,
            "posicao_real": t.posicao,
            "ataque": round(ataque, 2),
            "defesa": round(defesa, 2),
            "score": round(score, 2)
        })

    ranking.sort(key=lambda x: x["score"], reverse=True)

    # Calcula o 'Delta': Indica quantas posições o time está "devendo" ou "lucrando" 
    # em relação à sua qualidade técnica comprovada em campo.
    for i, t in enumerate(ranking):
        t["posicao_forca"] = i + 1
        t["delta"] = t["posicao_real"] - t["posicao_forca"]

    return ranking

def previsao_avancada(db: Session):
    times = db.query(models.Classificacao).all()
    partidas_futuras = db.query(models.PartidaFutura).all()

    if not times:
        raise HTTPException(status_code=404, detail="Sincronize os dados primeiro.")

    # --- BASE DA LIGA ---
    total_gols = sum(t.gols_feitos for t in times)
    total_jogos = sum(t.jogos for t in times) / 2
    media_liga = total_gols / total_jogos if total_jogos > 0 else 1

    # --- MAPA DE TIMES ---
    dict_times = {
        t.nome_time: {
            "pontos": t.pontos,
            "ataque": (t.gols_feitos / t.jogos) if t.jogos else 0,
            "defesa": (t.gols_sofridos / t.jogos) if t.jogos else 0
        }
        for t in times
    }

    # --- FUNÇÃO DE EXPECTATIVA DE GOLS ---
    def gols_esperados(ataque, defesa):
        # xG (Expected Goals) adaptado: cruza os índices multiplicando-os e normalizando pela média da liga
        return ataque * defesa / media_liga

    # --- FUNÇÃO DE PONTOS ESPERADOS ---
    def pontos_esperados(gols_a, gols_b):
        diff = gols_a - gols_b
        
        # Limiar de decisão para simular a chance de vitória:
        # Se a diferença de expectativa for maior que 0.5 gol, confere a vitória ao favorito.
        if diff > 0.5:
            return 3
        elif diff < -0.5:
            return 0
        else:
            return 1

    # --- SIMULAÇÃO ---
    pontos_simulados = {t.nome_time: t.pontos for t in times}

    for partida in partidas_futuras:
        casa = partida.time_mandante
        fora = partida.time_visitante

        if casa not in dict_times or fora not in dict_times:
            continue

        t_casa = dict_times[casa]
        t_fora = dict_times[fora]

        # Vantagem do mando de campo (Home Advantage): Multiplicador estatístico base padrão na literatura de análise esportiva.
        vantagem_casa = 1.1

        gols_casa = gols_esperados(t_casa["ataque"] * vantagem_casa, t_fora["defesa"])
        gols_fora = gols_esperados(t_fora["ataque"], t_casa["defesa"])

        pts_casa = pontos_esperados(gols_casa, gols_fora)
        pts_fora = pontos_esperados(gols_fora, gols_casa)

        pontos_simulados[casa] += pts_casa
        pontos_simulados[fora] += pts_fora

    # --- MONTAGEM FINAL ---
    projecao_lista = []

    for t in times:
        projecao_lista.append({
            "time": t.nome_time,
            "pontos_atuais": t.pontos,
            "projecao_final": round(pontos_simulados[t.nome_time], 1)
        })

    posicoes_atuais = {t.nome_time: t.posicao for t in times}

    projecao_lista.sort(key=lambda x: x["projecao_final"], reverse=True)

    for i, item in enumerate(projecao_lista):
        item["posicao_real"] = posicoes_atuais.get(item["time"], 999)
        item["posicao_projetada"] = i + 1
        item["delta"] = item["posicao_real"] - item["posicao_projetada"]

    return {
        "metodologia": "Simulação baseada em ataque/defesa + mando de campo",
        "previsao": projecao_lista
    }
    
def poisson_gols(lmbda):
    # Retorna um número aleatório de gols baseado na Distribuição de Poisson, dado um lambda (média esperada).
    return np.random.poisson(lmbda)
    
def previsao_monte_carlo(db: Session, simulacoes: int = 1000):
    # O modelo mais complexo da aplicação: Aplica o método de Monte Carlo iterando "N" cenários diferentes
    # do restante da temporada. Ao invés de projetar pontos fixos, joga dados (probabilidade de Poisson) para descobrir as "chances reais".
    times = db.query(models.Classificacao).all()
    partidas_futuras = db.query(models.PartidaFutura).all()

    if not times:
        raise HTTPException(status_code=404, detail="Sem dados.")

    # --- BASE DA LIGA ---
    total_gols = sum(t.gols_feitos for t in times)
    total_jogos = sum(t.jogos for t in times) / 2
    media_liga = total_gols / total_jogos if total_jogos > 0 else 1

    # --- DADOS DOS TIMES ---
    stats = {
        t.nome_time: {
            "ataque": (t.gols_feitos / t.jogos),
            "defesa": (t.gols_sofridos / t.jogos),
            "pontos": t.pontos
        }
        for t in times
    }

    # --- CONTADORES ---
    resultados = {
        t.nome_time: {
            "titulos": 0,
            "g4": 0,
            "rebaixamento": 0,
            "pontos_total": 0
        }
        for t in times
    }

    vantagem_casa = 1.1

    # --- SIMULAÇÕES ---
    # Roda o fim do campeonato inteiro 1.000 vezes, gerando resultados totalmente diferentes a cada laço de repetição.
    for _ in range(simulacoes):

        pontos = {t.nome_time: t.pontos for t in times}

        for partida in partidas_futuras:
            casa = partida.time_mandante
            fora = partida.time_visitante

            if casa not in stats or fora not in stats:
                continue

            atk_c = stats[casa]["ataque"] * vantagem_casa
            def_c = stats[casa]["defesa"]

            atk_f = stats[fora]["ataque"]
            def_f = stats[fora]["defesa"]

            # Determina o Lambda (força do cruzamento de ataque vs defesa)
            lambda_c = atk_c * def_f / media_liga
            lambda_f = atk_f * def_c / media_liga

            # Simula a partida "rolando os dados" usando a variação randômica da curva de Poisson
            gols_c = poisson_gols(lambda_c)
            gols_f = poisson_gols(lambda_f)

            if gols_c > gols_f:
                pontos[casa] += 3
            elif gols_f > gols_c:
                pontos[fora] += 3
            else:
                pontos[casa] += 1
                pontos[fora] += 1

        # --- CLASSIFICAÇÃO FINAL ---
        ranking = sorted(pontos.items(), key=lambda x: x[1], reverse=True)

        for pos, (time, pts) in enumerate(ranking):
            resultados[time]["pontos_total"] += pts

            if pos == 0:
                resultados[time]["titulos"] += 1
            if pos < 4:
                resultados[time]["g4"] += 1
            if pos >= 16:
                resultados[time]["rebaixamento"] += 1

    # --- CONSOLIDA RESULTADOS ---
    resposta = []

    for time, r in resultados.items():
        # Transforma os contadores absolutos em percentuais reais baseados nas 1000 simulações
        resposta.append({
            "time": time,
            "pontos_medios": round(r["pontos_total"] / simulacoes, 1),
            "chance_titulo_%": round((r["titulos"] / simulacoes) * 100, 2),
            "chance_g4_%": round((r["g4"] / simulacoes) * 100, 2),
            "chance_rebaixamento_%": round((r["rebaixamento"] / simulacoes) * 100, 2)
        })

    resposta.sort(key=lambda x: x["pontos_medios"], reverse=True)

    return {
        "metodologia": f"Monte Carlo ({simulacoes} simulações) + Poisson",
        "previsao": resposta
    }