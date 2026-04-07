# ⚽ ScoreFootball API

API para análise e previsões do Brasileirão.

---

## 🟢 Status

### `GET /brasileirao/`

Verifica se a API está online.

#### Response

```json
{
  "status": "ok",
  "mensagem": "API do ScoreFootball está online 🚀"
}
```

---

## 📊 Classificação

### `GET /brasileirao/classificacao`

Retorna a tabela atual do campeonato com estatísticas gerais.

#### Response (resumido)

```json
{
  "status": "ok",
  "gols_campeonato": 245,
  "partidas_registradas": 100,
  "classificacao": [
    {
      "posicao": 1,
      "nome_time": "Palmeiras",
      "pontos": 25
    }
  ]
}
```

---

## 📅 Próximos Jogos

### `GET /brasileirao/proximos-jogos`

Lista os jogos futuros agrupados por rodada.

#### Response

```json
{
  "status": "ok",
  "total_jogos": 10,
  "rodadas": {
    "1": [
      {
        "data": "2026-04-10",
        "hora": "16:00",
        "mandante": "Flamengo",
        "visitante": "Bahia"
      }
    ]
  }
}
```

---

## 📈 Tendência (Média)

### `GET /brasileirao/tendencia`

Projeção de pontuação baseada na média atual.

#### Response

```json
{
  "insight_de_tendencia": {
    "campeao_previsto": "Palmeiras"
  },
  "analise_detalhada": [
    {
      "time": "Palmeiras",
      "tendencia_final_38_rodadas": 95
    }
  ]
}
```

---

## 🎲 Monte Carlo

### `GET /brasileirao/previsao/monte-carlo`

Simula probabilidades do campeonato (1000 execuções).

#### Response

```json
{
  "metodologia": "Monte Carlo",
  "previsao": [
    {
      "time": "Palmeiras",
      "chance_titulo_%": 72.5,
      "chance_g4_%": 95.2,
      "chance_rebaixamento_%": 0.1
    }
  ]
}
```

---

## ⚡ Power Ranking

### `GET /brasileirao/power-ranking`

Ranking baseado em força ofensiva e defensiva.

#### Response

```json
[
  {
    "time": "Palmeiras",
    "score": 2.1,
    "posicao_forca": 1,
    "delta": 1
  }
]
```

---

## 🔄 Sincronização

### `GET /brasileirao/sync/dados`

Atualiza os dados do campeonato no banco local.

#### Response

```json
{
  "status": "ok",
  "mensagem": "Dados atualizados com sucesso"
}
```
