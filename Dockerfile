# from deno alpine latest
FROM python:3

# Set working directory
WORKDIR /app

# Copy initial necessary files to container
COPY requirements.txt .
COPY VERSION .

# this is the spotify cache file
COPY .cache* .

# Copy all files from src/
COPY src ./src

# add data folder
RUN mkdir data

# Install deps
RUN apt-get update
RUN apt-get install -y -q build-essential curl
RUN pip install --no-cache-dir -r requirements.txt

# rust install and build for qds
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
WORKDIR /app/src/opt/qds
RUN cargo build --release
RUN cp target/release/qds ../../bin/

# Start bot
WORKDIR /app
CMD ["python3", "src/runbot.py"]