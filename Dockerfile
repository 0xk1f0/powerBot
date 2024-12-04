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

# Install Dependencies only
RUN poetry install --no-root

# Copy module
COPY powerbot ./powerbot

# Install root
RUN poetry install --only-root

# Start bot
CMD ["poetry", "run", "main"]
