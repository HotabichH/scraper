
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
import random
import json
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

class DynamicContentScraper:
    def __init__(self, config):
        self.urls = config.get('urls', [])
        self.data = []
        self.proxy = config.get('proxy')
        self.timeout = config.get('timeout', 120000)

    async def fetch_page_source(self, page, url):
        logging.info(f"Loading page: {url}")
        try:
            user_agent = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
            ])
            await page.set_extra_http_headers({"User-Agent": user_agent})
            await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
            await page.wait_for_load_state('networkidle')
            return await page.content()
        except Exception as e:
            logging.error(f"Error loading page {url}: {e}")
            return ""

    def parse_data(self, html):
        logging.info("Parsing data")
        if not html:
            logging.error("HTML is empty")
            return

        soup = BeautifulSoup(html, 'html.parser')
        parsed_count = 0

        table = soup.find('table')
        if table:
            headers = [header.text.strip() for header in table.find_all('th')]
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == len(headers):
                    row_data = {headers[i]: cells[i].text.strip() for i in range(len(headers))}
                    self.data.append(row_data)
                    parsed_count += 1
        
        logging.info(f"Found items: {parsed_count}")
        logging.info(f"Current data: {self.data}")

    async def scrape_page(self, page, url):
        html = await self.fetch_page_source(page, url)
        self.parse_data(html)

    async def scrape(self, url):
        async with async_playwright() as p:
            launch_args = {'headless': True}
            if self.proxy:
                launch_args['proxy'] = {
                    'server': self.proxy
                }
            try:
                browser = await p.chromium.launch(**launch_args)
                page = await browser.new_page()
                await self.scrape_page(page, url)
            except Exception as e:
                logging.error(f"Error launching browser: {e}")
            finally:
                await browser.close()

    async def run(self):
        tasks = [self.scrape(url) for url in self.urls]
        await asyncio.gather(*tasks)

    def save_to_csv(self, filename):
        logging.info(f"Saving data to {filename}")
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logging.info(f"Data successfully saved to {filename}")
        else:
            logging.warning("No data to save.")

    def save_to_json(self, filename):
        logging.info(f"Saving data to {filename}")
        if self.data:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            logging.info(f"Data successfully saved to {filename}")
        else:
            logging.warning("No data to save.")

    def save_to_excel(self, filename):
        logging.info(f"Saving data to {filename}")
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_excel(filename, index=False, encoding='utf-8')
            logging.info(f"Data successfully saved to {filename}")
        else:
            logging.warning("No data to save.")

if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    scraper = DynamicContentScraper(config)
    asyncio.run(scraper.run())
    scraper.save_to_csv('output.csv')
    scraper.save_to_json('output.json')
    scraper.save_to_excel('output.xlsx')
    logging.info("Scraping completed")
