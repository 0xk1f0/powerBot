> [!NOTE]  
> Project in Maintenance Mode. Only doing Security related Updates.

# powerBot

[![Test, Build and Publish](https://github.com/0xk1f0/powerBot/actions/workflows/test_build_publish.yml/badge.svg)](https://github.com/0xk1f0/powerBot/actions/workflows/test_build_publish.yml)

A do-it-all discord bot written in spaghetti python

### What is integrated up to now

- Basic Moderation Functions like user restricting and message deletion
- Base32/64 Encode and Decode
- MD5/SHA Checksum
- Reddit fetching and Daily Posts to a specified channel via API
- waifu.pics fetching via API
- macvendors.com MAC-Address checking via API

## Usage

> Don't forget to edit and rename the example `config.example` accordingly

### Docker

A docker image is autobuilt and pushed to this repo's registry using
a workflow.

```bash
docker pull ghcr.io/0xk1f0/powerbot:master
```

You can use the docker-compose file provided in this repo for easy deployment.

> Don't forget to set the preferred Timezone in the `docker-compose.yml` file

```bash
git clone https://github.com/0xk1f0/powerBot
cd powerBot/
docker-compose up --build
```

The config location is handled by bind mounts, so the bot doesnt need to be rebuild when just the config changes.

### Manual

You'll need to have Python installed for this to work

```bash
git clone https://github.com/0xk1f0/powerBot
cd powerBot/
python -m venv env
source env/bin/activate
pip install -r requirements.txt
DATA_PATH="./data" CONF_PATH="./config" DS_PATH="./src/bin" python src/runbot.py
```

### Building the downscaler (`qds`)

You'll need to have Rust installed for this to work

```bash
# assuming you are in the cloned folder
cd src/opt/qds
cargo build --target x86_64-unknown-linux-musl --release
cp target/x86_64-unknown-linux-musl/release/qds ../../bin/
```

You could also implement other downscalers, although that could require some code modification.

### Obtaining the API Keys

Discord and Reddit are straightforward, just google.

## License

GPL 3.0
