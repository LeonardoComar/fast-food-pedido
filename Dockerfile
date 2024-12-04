FROM python:3.9-slim-buster

# Evita a criação de arquivos .pyc e garante a saída não-bufferizada no terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo de dependências e instala as dependências
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Instala a dependência adicional 'cpf'
RUN pip install cpf

# Copia o código fonte do projeto para o diretório de trabalho
COPY . /app/

# Expõe a porta 8080
EXPOSE 8080

# Inicia o serviço com uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
