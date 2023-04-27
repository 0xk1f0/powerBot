# from deno alpine latest
FROM python:3

# Set working directory
WORKDIR /app

# Copy initial necessary files to container
COPY requirements.txt .
COPY config.toml .
COPY runbot.py .
COPY VERSION .
# this is the spotify cache file
COPY .cache* .

# Copy all files from src/
COPY src ./src

# add data folder
RUN mkdir data

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Start bot
CMD ["python3", "runbot.py"]