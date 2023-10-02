import requests
import json
import logging
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

Base = declarative_base()


class Listing(Base):
    """
    Represents a listing object with details such as title, price, link, and image URL.

    Args:
        data (dict): Data for the listing.
        listing_type (str): The type of data ('html' or 'json').

    Attributes:
        id (int): Unique identifier for the listing.
        title (str): Title of the listing.
        price (str): Price of the listing.
        details (str): Additional details about the listing.
        link (str): Link to the listing.
        img_url (str): URL of the listing's image.
    """

    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(String)
    details = Column(String)
    link = Column(String)
    img_url = Column(String)

    def __init__(self, data, listing_type='html'):
        if listing_type == 'json':
            self.title = data.get('title', 'N/A')
            self.price = data.get('price', 'N/A')
            self.details = data.get('details', 'N/A')
            self.link = data.get('link', 'N/A')
            self.img_url = data.get('img_url', 'N/A')
        elif listing_type == 'html':
            soup = BeautifulSoup(data, 'html.parser')
            # Get the title of the listing
            title_element = soup.find(
                'h2', class_='mb-1 truncate typography_shared__SK_V2 typography_m-headingS__ozYY8 typography_subtitle2__nF6ow')
            self.title = title_element.text.strip() if title_element else 'N/A'
            # Get the price of the listing
            price_element = soup.find(
                'p', class_='m:mb-4 typography_shared__SK_V2 typography_m-headingS__ozYY8 typography_subtitle2__nF6ow')
            self.price = price_element.text.strip() if price_element else 'N/A'
            # Get the details of the listing
            details_element = soup.find(
                'p', class_='mb-2 m:mb-4 text-gray-dark truncate typography_shared__SK_V2 typography_m-body1__5__iP typography_caption__Cf12X')
            self.details = details_element.text.strip() if details_element else 'N/A'
            # Get the link to the listing
            link_element = soup.find(
                'a', class_='adCard_anchor__hJqwV adCardImageCarousel_snapCarousel___axZ8 m:rounded-bl-lg')
            self.link = 'https://autot.tori.fi' + \
                link_element['href'].strip() if link_element else 'N/A'
            # Get the image URL for the listing
            try:
                self.img_url = soup.find(
                    'img', class_='adCardImageCarousel_image__PzAHL')['src']
            except:
                self.img_url = 'N/A'

    def is_valid(self):
        """Check if the listing is valid."""
        return bool(self.title or self.link)

    def __repr__(self):
        return (
            f'<Listing title="{self.title}" '
            f'price="{self.price}" '
            f'details="{self.details}" '
            f'link="{self.link}" '
            f'img_url="{self.img_url}">'
        )


class ListingRepository:
    """
    Manages database operations for listings.

    Args:
        connection_string (str): Database connection string.
    """

    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        # Create the table if it doesn't exist
        Base.metadata.create_all(self.engine)

    def save_listing(self, listing):
        """Save a listing to the database."""
        session = self.Session()
        session.add(listing)
        session.commit()
        session.close()

    def get_all_links(self):
        """Retrieve all listing links from the database."""
        session = self.Session()
        links = [listing.link for listing in session.query(Listing).all()]
        session.close()
        return set(links)

# Scraper objects


class ScraperBase:
    """
    Base class for scrapers.

    Args:
        config_file (str): Path to the configuration file.
        db_connection_string (str): Database connection string.
    """

    def __init__(self, config_file='config.json', db_connection_string='sqlite:///listings.db'):
        self.config_file = config_file
        self.load_config()
        self.new_listings = []
        self.repository = ListingRepository(db_connection_string)

    def load_config(self):
        """Load configuration data from the config file."""
        try:
            with open(self.config_file, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            logging.error(f"Config file '{self.config_file}' not found.")
            self.config = {}

    def scrape_listings(self):
        """Scrape listings (to be implemented in child classes)."""
        pass

    def scrape_url(self, url):
        """Scrape listings from a URL and add new listings to the repository."""
        logging.info(f"Scraping URL: {url}")
        response = requests.get(url)
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            listing_elements = soup.find_all('div', class_='w-full p-2')

            for listing_element in listing_elements:
                listing = Listing(str(listing_element))
                if listing.is_valid() and listing.link not in self.repository.get_all_links():
                    self.new_listings.append(listing)
        else:
            logging.error(f"Failed to fetch URL: {url}")

    def save_listings(self):
        """Save new listings to the database."""
        session = self.repository.Session()
        for listing in self.new_listings:
            session.add(listing)
        session.commit()
        session.close()
        self.new_listings.clear()


class ToriScraper(ScraperBase):
    """
    Scraper for Tori listings.

    Args:
        config_file (str): Path to the configuration file.
        db_connection_string (str): Database connection string.
    """

    def scrape_listings(self):
        """Scrape listings from Tori URLs."""
        if 'listing_urls' in self.config:
            for listing_url in self.config['listing_urls']:
                self.scrape_url(listing_url)
        else:
            logging.error("No listing URLs found in the configuration.")

    def scrape_url(self, url):
        """Scrape listings from a Tori URL and add new listings to the repository."""
        response = requests.get(url)
        logging.info(f"Scraping Tori URL: {url}")
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            listing_elements = soup.find_all('div', class_='w-full p-2')
            for listing_element in listing_elements:
                listing = Listing(str(listing_element))
                if listing.is_valid() and listing.link not in self.repository.get_all_links():
                    self.new_listings.append(listing)
        else:
            logging.error(f"Failed to fetch Tori URL: {url}")


class NettikoneScraper(ScraperBase):
    """
    Scraper for Nettikone listings.

    Args:
        api_key (str): API key for Nettikone.
        makes (list): List of makes to filter listings.
        config_file (str): Path to the configuration file.
        db_connection_string (str): Database connection string.
    """

    def __init__(self, api_key, makes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.base_url = 'https://api.nettix.fi/rest/machine/search'
        self.headers = {
            'X-Access-Token': self.api_key,
        }
        self.makes = makes if makes else None

    def scrape_listings(self):
        """Scrape Nettikone listings and add new listings to the repository."""
        params = {
            'page': 1,
            'rows': 30,
            'status': ['forsale'],
            'categories': [1, 2],
            'sortBy': 'dateCreated',
            'sortOrder': 'asc',
            'includeMakeModel': True,
        }

        if self.makes:
            params['make'] = self.makes

        try:
            response = requests.get(
                self.base_url, headers=self.headers, params=params)
            logging.info(
                f"Nettikone API Response status code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                listings = []

                for item in data:
                    listing_data = {
                        'title': item['model'],
                        'link': '' + item['adUrl'],
                        'price': str(item['id']),
                        'img_url': item['images'][0]['smallThumbnail']['url'] if 'images' in item and len(item['images']) > 0 else None,
                        'details': item['model'],
                    }
                    listing = Listing(listing_data, listing_type='json')
                    listings.append(listing)
                if listing.is_valid() and listing.link not in self.repository.get_all_links():
                    self.new_listings.extend(listings)
            else:
                logging.error(
                    f"Failed to retrieve Nettikone data. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during Nettikone request: {e}")


def get_nettikone_api_token(username, password):
    """
    Retrieve the Nettikone API token.

    Args:
        username (str): Nettikone username.
        password (str): Nettikone password.

    Returns:
        str: Nettikone API token or None if the token retrieval fails.
    """
    token_url = "https://auth.nettix.fi/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "username": username,
        "password": password
    }

    try:
        # Disable SSL certificate verification
        response = requests.post(token_url, data=data, verify=False)
        logging.info(
            f"Nettikone API Token Response status code: {response.status_code}")
        response.raise_for_status()
        token_data = response.json()
        if "access_token" in token_data:
            return token_data["access_token"]
        else:
            logging.error("Failed to obtain Nettikone API token.")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during Nettikone request: {e}")


# Example usage
# if __name__ == "__main__":
#     # Create a ToriScraper object and scrape listings
#     tori_scraper = ToriScraper()
#     tori_scraper.scrape_listings()
#     tori_scraper.save_listings()

#     # Create a NettikoneScraper object and scrape listings
#     nettikone_api_key = get_nettikone_api_token(
#         "your_username", "your_password")
#     nettikone_scraper = NettikoneScraper(api_key=nettikone_api_key)
#     nettikone_scraper.scrape_listings()
#     nettikone_scraper.save_listings()
