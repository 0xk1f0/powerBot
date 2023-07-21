# from deno alpine latest
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy initial necessary files to container
COPY requirements.txt .
COPY VERSION .

# this is the spotify cache file
COPY .cache* .

# Copy all files from src/
COPY src .

# add data folder and conf dir
RUN mkdir /var/lib/powerBot/config
RUN mkdir /var/lib/powerBot/data

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Start bot
WORKDIR /app
CMD ["python3", "runbot.py"]
