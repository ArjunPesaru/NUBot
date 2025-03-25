import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import json
import re
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
load_dotenv(override=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
# Configuration
BASE_URL = 'https://www.khoury.northeastern.edu/'
MAX_DEPTH = 3            # Maximum recursion depth (base URL is depth 0)
CONCURRENT_REQUESTS = 10  # Maximum number of concurrent requests

# Create folder for JSON data
DATA_FOLDER = "scraped_data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def safe_filename(url):
    if isinstance(url, bytes):
        url = url.decode("utf-8")  # decode bytes to str

    parsed = urlparse(url)
    path = parsed.path.strip('/') or 'index'
    filename = re.sub(r'[^A-Za-z0-9_\-]', '_', path) + ".json"
    return os.path.join(DATA_FOLDER, filename)


async def fetch(session, url, semaphore):
    """Fetch the content of the URL asynchronously."""
    try:
        async with semaphore:
            async with session.get(url,ssl=False) as response:
                if response.status != 200:
                    print(f"Failed to retrieve {url} (status: {response.status})")
                    return None
                return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def async_scrape(url, depth=0, session=None, semaphore=None):
    """Recursively scrape pages asynchronously and store in JSON format."""
    if depth > MAX_DEPTH:
        return

    # Check if already scraped
    filename = safe_filename(url)
    if os.path.exists(filename):
        return

    print(f"Scraping (depth {depth}): {url}")
    
    html = await fetch(session, url, semaphore)
    if html is None:
        return

    # Parse HTML and extract text
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script, style, and navigation elements
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else "No Title"
    text = soup.get_text(separator="\n", strip=True)

    # Save structured data to JSON
    page_data = {
        "url": url,
        "title": title,
        "text": text
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, indent=4)

    # Extract and follow internal links
    tasks = []
    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
            next_url = next_url.split('#')[0]  # Remove fragments
            tasks.append(async_scrape(next_url, depth + 1, session, semaphore))

    if tasks:
        await asyncio.gather(*tasks)
    

async def scrape_and_load():
    """Main function to initiate scraping."""
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    
    async with aiohttp.ClientSession() as session:
        await async_scrape(BASE_URL, depth=0, session=session, semaphore=semaphore)
    

def scrape_and_load_task():
    return asyncio.run(scrape_and_load())

if __name__ == '__main__':
    asyncio.run(scrape_and_load())
