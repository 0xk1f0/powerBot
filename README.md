# powerBot

A do-it-all discord bot written in spaghetti python

## Usage

> Don't forget to edit and rename the example `config.example` accordingly

### Manual

```bash
git clone https://github.com/0xk1f0/powerBot
cd powerBot/
python -m venv env
./runbot.py
```

### Docker

> Don't forget to set the preferred Timezone in the `docker-compose.yml` file

```bash
git clone https://github.com/0xk1f0/powerBot
cd powerBot/
docker-compose up --build
```

### Obtaining the API Keys

Discord and Reddit are straightforward, just google.

Same goes for Spotify although I advice to run the bot from a PC with a browser the first time as Spotify will ask you to login the first time.
A `.cache` file will be generated after that and you won't need the browser anymore as long as it is present (will auto renew).

## License

GPL 3.0
