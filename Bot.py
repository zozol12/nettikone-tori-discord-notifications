import discord
import json
import asyncio
import logging  # Added for logging
from discord.ext import commands, tasks
from Helper import generate_tori_url, get_make_ids
from Lib import ToriScraper, NettikoneScraper, get_nettikone_api_token

# Initialize configuration variables
config_data = {}
file_path = 'config.json'

# Set up logging
logging.basicConfig(level=logging.INFO)  # Adjust log level as needed

# Load configuration data from config.json
try:
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
except FileNotFoundError:
    logging.error(
        "config.json not found. Please ensure it exists with valid configuration.")
    exit(1)

# Retrieve configuration values
makes = config_data.get('makes', [])
bot_token = config_data.get('bot_token', '')
channel_id = config_data.get('channel_id', 0)
print(channel_id)
api_token = config_data.get('api_token', '')
netti_login = config_data.get('netti_login', '')
netti_pass = config_data.get('netti_pass', '')
delay = config_data.get('delay', 10)

# Update the 'listing_urls' field with the new 'makes' data
config_data['listing_urls'] = [generate_tori_url(config_data.get('makes', []))]

# Write the updated configuration back to config.json
try:
    with open(file_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)
except Exception as e:
    logging.error(f"Failed to write to config.json: {e}")

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True

# Get API token for Nettikone
api_token = get_nettikone_api_token(netti_login, netti_pass)

# Initialize Tori and Nettikone scrapers
tori_scraper = ToriScraper('config.json')
nettikone_scraper = NettikoneScraper(api_token, makes=get_make_ids(makes))

# Initialize the Discord bot
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logging.info(f"Logged in as {bot.user.name}")
    scrape_and_notify.start()  # Start the background task


@tasks.loop(seconds=delay)  # Adjust the interval as needed
async def scrape_and_notify():
    """Background task to scrape listings and send notifications."""
    global makes
    try:
        tori_scraper.scrape_listings()
        nettikone_scraper.scrape_listings()

        # Combine new listings from both scrapers
        all_new_listings = tori_scraper.new_listings + nettikone_scraper.new_listings
        logging.info(f'New listings found: {len(all_new_listings)}')

        # Send notifications to the specified Discord channel
        channel = bot.get_channel(channel_id)
        for listing in all_new_listings:
            # Add a source attribute to the Listing object
            listing.source = 'Tori' if listing in tori_scraper.new_listings else 'Nettikone'
            
            embed = discord.Embed(
                title="New Listing", description=f"Title: {listing.title}\nPrice: {listing.price}\nLink: {listing.link}\nSource: {listing.source}")
            if listing.img_url:
                embed.set_thumbnail(url=listing.img_url)
            await channel.send(embed=embed)

        tori_scraper.save_listings()
        nettikone_scraper.save_listings()
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")



async def main():
    """Main function to start the bot."""
    try:
        await bot.start(bot_token)
    except Exception as e:
        logging.error(f"Failed to start the bot: {e}")

# Run the bot with your bot token
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
