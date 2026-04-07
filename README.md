# ⚽ ScoreFootball - Analise e Previsão do Brasileirão Série A

Uma aplicação *full-stack* desenvolvida para fornecer análises estatísticas profundas, classificação em tempo real e previsões matemáticas do **Brasileirão Série A**.

O sistema vai além da tabela tradicional: ele utiliza modelos estatísticos avançados (como **Distribuição de Poisson** e **Simulações de Monte Carlo**) para prever as chances de título, classificação para a Libertadores (G4/G6) e riscos de rebaixamento (Z4) de cada equipe.

---

## 🚀 Tecnologias Utilizadas

O projeto foi construído em arquitetura de **Monorepo**, dividindo claramente as responsabilidades entre Backend e Frontend, tudo orquestrado via containers.

**Backend:**
- **[FastAPI](https://fastapi.tiangolo.com/):** Framework web de altíssima performance para a construção da API.
- **[PostgreSQL](https://www.postgresql.org/):** Banco de dados relacional robusto.
- **[SQLAlchemy & Pydantic]:** ORM para modelagem de dados e tipagem rigorosa/validação de schemas.
- **[NumPy]:** Motor matemático para os cálculos das simulações de probabilidade.

**Frontend:**
- **HTML5, CSS3 & Vanilla JavaScript:** Interface leve, rápida e sem dependência de frameworks pesados.
- **[Nginx](https://www.nginx.com/):** Servidor web de alta performance usado para servir os arquivos estáticos.

**Infraestrutura:**
- **[Docker & Docker Compose](https://www.docker.com/):** Padronização do ambiente de desenvolvimento e deploy.

---

## ⚙️ Como Executar o Projeto Localmente

O projeto foi inteiramente "dockerizado" para que você possa rodá-lo com poucos comandos, sem precisar instalar Python, Node ou PostgreSQL diretamente na sua máquina.

### 1. Pré-requisitos
- Ter o [Docker](https://docs.docker.com/get-docker/) e o [Docker Compose](https://docs.docker.com/compose/install/) instalados.

### 2. Configuração do Ambiente (.env)
Crie um arquivo chamado `.env` na raiz do projeto (mesmo local do `docker-compose.yml`) e adicione as variáveis de ambiente necessárias. Você vai precisar de uma chave gratuita da API do football-data.org.

```env
# .env
API_KEY=sua_chave_da_api_aqui
```

### 3. Subindo os Containers
No terminal, na raiz do projeto, execute o comando abaixo para construir as imagens e subir os três serviços (Banco de Dados, Backend e Frontend):

```bash
docker-compose up -d --build
```

### 4. Acessando a Aplicação
- **Interface de Usuário (Frontend):** http://localhost:3000
- **Documentação Interativa da API (Swagger):** http://localhost:8000/docs

*Nota: Ao acessar o sistema pela primeira vez, lembre-se de clicar em "Sincronizar" na interface (ou bater na rota `/brasileirao/sync/dados`) para preencher o seu banco de dados local com os dados da temporada atual.*

---

## 📂 Estrutura do Projeto

```text
scoreFootball/
├── docker-compose.yml       # Orquestração dos serviços (DB, API, Nginx)
├── .env                     # Variáveis sensíveis (ignoradas no git)
├── backend/                 # API REST em FastAPI
│   ├── main.py              # Ponto de entrada e configuração do CORS
│   ├── routes.py            # Controladores e Endpoints HTTP
│   ├── service.py           # Regras de negócio, Poisson e Monte Carlo
│   ├── models.py            # Tabelas do banco de dados (SQLAlchemy)
│   ├── schemas.py           # Validações de entrada/saída (Pydantic)
│   └── Dockerfile           # Imagem Docker do Python
└── frontend/                # SPA Vanilla JS
    ├── index.html           # Estrutura visual e abas
    ├── style.css            # Estilização
    └── script.js            # Consumo da API e renderização do DOM
```

---

## 🧠 Entendendo os Modelos Preditivos

A aplicação se destaca pelos seus métodos de previsão (disponíveis na camada `service.py`).

> **⚠️ Importante sobre os dados:** Atualmente, **todos os cálculos preditivos utilizam estritamente os dados da temporada atual**. O sistema avalia o desempenho estatístico das equipes nas partidas já jogadas até o presente momento e simula os confrontos baseados exclusivamente na agenda de jogos que ainda virão pela frente. Não utilizamos, *por enquanto*, dados históricos de temporadas passadas na composição do algoritmo.

Os modelos disponíveis são:

1. **Tendência de Média e Frequência:** Projeções lineares baseadas nos pontos atuais ou na proporção de Vitórias/Empates/Derrotas que os times conquistaram no campeonato vigente.
2. **Power Ranking:** Avalia a força bruta atual de Ataque vs Defesa de cada equipe, cruzando com a média de gols global da liga, para revelar times que estão performando abaixo ou acima da sua qualidade técnica real.
3. **Simulação Avançada e Monte Carlo:** O algoritmo projeta a tabela final executando o restante do campeonato milhares de vezes. Em cada partida futura simulada, os gols são "rolados" estatisticamente usando a **Distribuição de Poisson** (cruzando Ataque do Mandante x Defesa do Visitante), revelando as reais porcentagens matemáticas de chance de título, vagas em copas internacionais e rebaixamento.

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Sinta-se livre para usar, estudar, modificar e distribuir este código da forma que achar melhor.