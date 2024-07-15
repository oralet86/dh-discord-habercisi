# Donanimhaber Discord Habercisi

This bot sends messages to a specified Discord channel when a new topic is created in a specified DonanimHaber forum.

## Features

- Monitors specified DonanimHaber forums for new topics.
- Sends notifications to a Discord channel with topic details.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- A Discord bot account. If you don't know how to create a bot account, follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html).

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/oralet86/dh-discord-habercisi.git
    ```
2. Navigate to the project directory:
    ```sh
    cd dh-discord-habercisi
    ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Change the name of file `.env.example` to `.env`:
    ```sh
    mv .env.example .env
    ```

### Configuration

1. Create a Discord bot and add it to your server. 
2. Create a `.env` file in the project root directory and add your bot token:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    ```

### Usage

1. Start the bot:
    ```sh
    python3 main.py
    ```

2. Use the following commands in Discord: (Default prefix is dh, you may change it from the `.env` file)
    - `dhekle 'link'`: Add a forum to the watch list.
    - `dhcikar 'link'`: Remove a forum from the watch list. If no link is provided, all forums are removed.
    - `dhliste`: Gives a list of all forums watched by the current text channel.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) for details.
