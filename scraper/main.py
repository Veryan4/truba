from services import scraper
from dotenv import load_dotenv

# Call scrape() when file is called
if __name__ == '__main__':
  load_dotenv()
  scraper.scrape()
