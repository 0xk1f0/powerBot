# from python latest
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# add data folder and conf dir
RUN mkdir -p /var/lib/powerBot/config
RUN mkdir -p /var/lib/powerBot/data

# install poetry
RUN pip install poetry

# Copy initial necessary files to container
COPY pyproject.toml .
COPY poetry.lock .
COPY VERSION .

# Install poetry deps
RUN poetry install

# Copy module
COPY powerbot ./powerbot

# Start bot
CMD ["poetry", "run", "dist"]
