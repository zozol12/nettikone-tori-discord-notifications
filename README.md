---

# Nettikone and Tori Notifier Discord Bot

![GitHub](https://img.shields.io/github/license/zozol12/nettikone-tori-discord-notifications)
![GitHub issues](https://img.shields.io/github/issues/zozol12/nettikone-tori-discord-notifications)

**Note: This project is under development and may contain bugs.**

## Description

This repository contains a Python library for scraping the latest listings from Nettikone and Tori, saving them to an SQLite database, along with a Discord bot that sends notifications about new listings.

**It was originally created for personal use, but I thought maybe it can be handy for someone too.**

The library is somewhat hard-coded and not as configurable as it should be, but there are plans to rewrite it for better flexibility.

### Features

- **Scrape Nettikone:** Retrieve listings of vehicles and equipment from Nettikone based on various criteria.
- **Scrape Tori:** Fetch listings of vehicles and equipment from Tori.fi based on your preferences.
- **Discord Notifications:** Receive notifications in a Discord channel when new listings are found.
- **Customizable:** Configure the bot to search for specific makes and models.

## Installation

1. Clone this repository to your local machine:

   ```
   git clone https://github.com/zozol12/nettikone-tori-discord-notifications.git
   ```

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

## Usage

### Library Usage

1. Import the `NettikoneScraper` and `ToriScraper` classes from `Lib.py`.

2. Initialize the scrapers with your preferences:

   ```python
   from nettikone_scraper import NettikoneScraper
   from tori_scraper import ToriScraper

   nettikone_scraper = NettikoneScraper(api_key="your_netikone_api_key", makes=["Make1", "Make2"])
   tori_scraper = ToriScraper(config_file="config.json")
   ```

3. Use the `scrape_listings()` method to retrieve listings:

   ```python
   nettikone_scraper.scrape_listings()
   tori_scraper.scrape_listings()
   ```

4. Save the listings to a database:

   ```python
   nettikone_scraper.save_listings()
   tori_scraper.save_listings()
   ```

### Discord Bot

1. Set up a Discord bot and obtain its token. Follow the official Discord documentation to create a bot.

2. Edit `config.json` with your configuration options (listing_urls are generated automatically based on makes):

   ```json
   {
       "bot_token": "your_discord_bot_token",
       "channel_id": 123456789,   // Your Discord channel ID
       "makes": ["Make1", "Make2"],
       // Other configuration options...
   }
   ```

3. Import and run the Discord bot:

   ```python
   python bot.py
   ```

### Helper Class

The `helper.py` file contains a helper class for managing makes and generating Tori URLs. Use it as follows:

1. Import the helper class:

   ```python
   from helper import generate_tori_url, get_make_ids
   ```

2. Use the `generate_tori_url()` function to create Tori URLs based on makes:

   ```python
   makes = ["Make1", "Make2"]
   tori_url = generate_tori_url(makes)
   ```

3. Use the `get_make_ids()` function to retrieve make IDs:

   ```python
   make_names = ["Make1", "Make2"]
   make_ids = get_make_ids(make_names)
   ```

### Configuration Options

- `bot_token`: Your Discord bot token.
- `channel_id`: The ID of the Discord channel where notifications will be sent.
- `makes`: A list of makes to search for listings.
- `api_key` (Nettikone only): Your Nettikone API key.
- `delay`: Interval in seconds between scraping attempts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Issues

The code can be significantly improved, and there are plans to rewrite the library soon.

If you encounter any issues or have suggestions for improvements, please [open an issue](https://github.com/zozol12/nettikone-tori-discord-notifications/issues).
