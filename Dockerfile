# from deno alpine latest
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy initial necessary files to container
COPY requirements.txt .
COPY VERSION .

# Copy all files from src/
COPY src .

# add data folder and conf dir
RUN mkdir -p /var/lib/powerBot/config
RUN mkdir -p /var/lib/powerBot/data

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Start bot
WORKDIR /app
CMD ["python3", "runbot.py"]
