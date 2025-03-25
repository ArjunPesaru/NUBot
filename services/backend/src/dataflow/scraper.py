import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import json
import re
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

#  Load configuration from .env
load_dotenv('backend.env', override=True)

BASE_URL = os.getenv('BASE_URL')
MAX_DEPTH = int(os.getenv('MAX_DEPTH', 2))  # default to 2
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', 5))


#  Create folder to store JSON files
DATA_FOLDER = "scraped_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

def safe_filename(url):
    if isinstance(url, bytes):
        url = url.decode("utf-8")  # decode bytes to str

    parsed = urlparse(url)
    path = parsed.path.strip('/') or 'index'
    filename = re.sub(r'[^A-Za-z0-9_\-]', '_', path) + ".json"
    return os.path.join(DATA_FOLDER, filename)




async def fetch(session, url, semaphore):
    try:
        async with semaphore:
            async with session.get(url, ssl=False) as response:
                if response.status != 200:
                    print(f" Failed to retrieve {url} (status: {response.status})")
                    return None
                return await response.text()
    except Exception as e:
        print(f" Error fetching {url}: {e}")
        return None

async def async_scrape(url, depth=0, session=None, semaphore=None):
    if depth > MAX_DEPTH:
        return

    filename = safe_filename(url)
    if os.path.exists(filename):
        return

    print(f"🔍 Scraping (depth {depth}): {url}")
    html = await fetch(session, url, semaphore)
    if html is None:
        return

    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else "No Title"
    text = soup.get_text(separator="\n", strip=True)

    page_data = {
        "url": url,
        "title": title,
        "text": text
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, indent=4)

    # Recurse on internal links
    tasks = []
    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
            next_url = next_url.split('#')[0]
            tasks.append(async_scrape(next_url, depth + 1, session, semaphore))

    if tasks:
        await asyncio.gather(*tasks)

async def scrape_and_load():
    """Main async entry point"""
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession() as session:
        await async_scrape(BASE_URL, 0, session, semaphore)

#  Airflow-compatible callable
def run_scraper():
    print(" Starting async scraper via run_scraper()...")
    asyncio.run(scrape_and_load())

#  Local test support
if __name__ == "__main__":
    run_scraper()
