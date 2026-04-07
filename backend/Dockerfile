# Utiliza a imagem oficial do Python na versão "slim" (reduz o tamanho final da imagem e a superfície de ataque)
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container (todas as ações subsequentes ocorrerão aqui)
WORKDIR /app

# Copia apenas o arquivo de dependências primeiro.
# Isso é uma boa prática para otimizar o cache de build do Docker: 
# se o requirements.txt não mudar, o Docker reaproveita a camada e não reinstala as bibliotecas.
COPY requirements.txt .

# Instala as dependências do Python.
# A flag --no-cache-dir evita armazenar os pacotes baixados em cache local, mantendo a imagem leve.
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para dentro do diretório de trabalho (/app)
COPY . .

# Comando padrão executado quando o container inicia.
# Inicia o Uvicorn na porta 8000, escutando em todas as interfaces (0.0.0.0).
# A flag --reload permite Hot Reload (atualiza sozinho) e é ideal APENAS para ambiente de desenvolvimento.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]