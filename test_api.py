import requests

# --- CONFIGURAÇÕES ---
# Coloque o token que você vai receber por e-mail
API_KEY = "9656c2f60451410f8ddf78df06fb8725"
COMPETITION = "BSA" # Código do Brasileirão Série A

def testar_football_data():
    print(f"Iniciando conexão com Football-Data.org para o Brasileirão...\n")
    
    url = f"https://api.football-data.org/v4/competitions/{COMPETITION}/standings"
    headers = {"X-Auth-Token": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        
        # Tratamento de erro direto
        if response.status_code != 200:
            print(f"❌ Erro na API: Status {response.status_code}")
            print(response.text)
            return
            
        dados = response.json()
        
        # Pega o ano da temporada atual que a API está retornando
        temporada = dados["season"]["startDate"][:4]
        tabela = dados["standings"][0]["table"]
        
        print("-" * 50)
        print(f"🏆 CLASSIFICAÇÃO: BRASILEIRÃO SÉRIE A ({temporada}) 🏆")
        print("-" * 50)
        
        # O campeonato de 2026 começa agora em abril, então os times podem estar com 0 pontos
        for time in tabela[:5]: 
            posicao = time["position"]
            nome = time["team"]["shortName"]
            pontos = time["points"]
            jogos = time["playedGames"]
            vitorias = time["won"]
            
            print(f"{posicao}º | {nome.ljust(15)} | Pontos: {pontos} | Jogos: {jogos} | Vitórias: {vitorias}")
            
        print("-" * 50)
        print("✅ SUCESSO! Furamos o bloqueio e temos dados da temporada atual!")

    except Exception as erro:
        print(f"❌ Erro na requisição: {erro}")

if __name__ == "__main__":
    testar_football_data()