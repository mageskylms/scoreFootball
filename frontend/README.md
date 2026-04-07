# 🖥️ ScoreFootball - Frontend (Vanilla JavaScript)

Este diretório contém a interface de usuário (UI) do projeto ScoreFootball. Desenvolvida com HTML, CSS e JavaScript puro (Vanilla JS), esta camada é responsável por apresentar os dados e análises do Brasileirão de forma interativa e responsiva, consumindo a API do backend.

---

## 🚀 Tecnologias Utilizadas

- **HTML5:** Estrutura semântica da página.
- **CSS3:** Estilização e design responsivo da interface.
- **Vanilla JavaScript:** Lógica de interação, manipulação do DOM e chamadas assíncronas à API do backend.
- **Nginx:** Servidor web leve e de alta performance utilizado para servir os arquivos estáticos do frontend em ambiente Docker.

---

## ⚙️ Como Executar Localmente

O frontend é parte integrante do ambiente Docker Compose do projeto. Para executá-lo, você deve seguir as instruções de inicialização do projeto completo.

### 1. Pré-requisitos
- Ter o [Docker](https://docs.docker.com/get-docker/) e o [Docker Compose](https://docs.docker.com/compose/install/) instalados.

### 2. Inicialização
Certifique-se de que o arquivo `.env` esteja configurado na raiz do projeto e, em seguida, execute o Docker Compose na raiz do projeto:

```bash
# Na raiz do projeto (scoreFootball/)
> docker-compose up -d --build
