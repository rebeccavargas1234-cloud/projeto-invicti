FROM python:3.10-slim

# Criar diretório
WORKDIR /app

# Copiar arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Rodar app
CMD ["python", "app.py"]
