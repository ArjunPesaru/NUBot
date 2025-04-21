from prefect import flow, task, get_run_logger
# Import the supporting functions from dataflow module
from dataflow.scraper import scrape_and_load_task  # adjust import to actual module path
from dataflow.chunk_data import chunk_data

# Define Prefect tasks
@task
def scrape_all_urls_task():
    """Task to scrape all URLs and load raw data."""
    logger = get_run_logger()
    logger.info("Starting scrape_all_urls_task...")
    data = scrape_and_load_task()  # call the helper function to scrape and load data
    # logger.info(f"Scraped data: {len(data)} items.")
    return data

@task
def dataSegmentation(data):
    """Task to segment the scraped data into chunks."""
    logger = get_run_logger()
    logger.info("Starting dataSegmentation task...")
    segments = chunk_data()  # call helper to chunk the data
    # logger.info(f"Segmented data into {len(segments)} chunks.")
    return segments

@flow
def scraper_flow():
    """Prefect flow to orchestrate scraping and data segmentation."""
    # Run the scraping task and then pass its result into the segmentation task
    raw_data = scrape_all_urls_task()
    segmented = dataSegmentation(raw_data)
    # (Optional) do something with segmented data, e.g., save or return
    return "done"

if __name__ == "__main__":
    # This allows testing the flow locally by running this script
    scraper_flow()
