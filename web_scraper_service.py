import requests
from bs4 import BeautifulSoup
from config.logging import setup_logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WebScraperService:
    def __init__(self):
        self.logger = setup_logging()
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def scrape_definitions(self, url):
        try:

            response = requests.get(url)
            if response.status_code != 200:
                self.logger.error(
                    f"Failed to retrieve {url}. Status code: {response.status_code}"
                )
                return None

            soup = BeautifulSoup(response.content, "html.parser")
            main_div = soup.find("div", class_="dir obverse exacts")
            if not main_div:
                self.logger.error(f"Main div not found in {url}.")
                return None

            entries = main_div.find_all("div", class_="fgb entry")
            definitions = [
                entry.get_text(separator=" ", strip=True) for entry in entries
            ]
            full_definition = "\n\n".join(definitions)
            self.logger.debug(f"Extracted definitions: {full_definition}")

            return full_definition
        except requests.RequestException as re:
            self.logger.error(f"Request failed for {url}: {re}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None
