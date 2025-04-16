import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import json
import re
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import hashlib
from store_data import upload_many_blobs_with_transfer_manager
load_dotenv(override=True)
# Configuration
BASE_URL = os.getenv('BASE_URL')
MAX_DEPTH = int(os.getenv('MAX_DEPTH'))             # Maximum recursion depth (base URL is depth 0)
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS'))  # Maximum number of concurrent requests

from google.auth import default
from google.oauth2 import service_account

# Try to get credentials - works in both Docker and Cloud Run
try:
    # First try Application Default Credentials (works in Cloud Run)
    credentials, project = default()
except Exception:
    # Fall back to explicit credentials file (for Docker)
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
    else:
        raise Exception("No credentials available")
# Create folder for JSON data
DATA_FOLDER = "scraped_data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def safe_filename(url):
    """Generates a filename based on the URL path."""
    parsed = urlparse(url)
    path = parsed.path.strip('/') or 'index'
    filename = re.sub(r'[^A-Za-z0-9_\-]', '_', path) + ".json"
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return os.path.join(DATA_FOLDER, f"{filename}_{url_hash}.json")

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
    asyncio.run(scrape_and_load())
    upload_many_blobs_with_transfer_manager()
    return


if __name__ == '__main__':
    asyncio.run(scrape_and_load())
    upload_many_blobs_with_transfer_manager()