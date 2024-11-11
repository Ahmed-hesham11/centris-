
# Centris Scraper

## Description
This project is a web scraper for property listings from Centris.ca. Using **Scrapy** and **Splash**, it gathers data on properties available for rent in specific regions, capturing details such as the category, address, price, room count, and URL for each listing.

## Features
- Scrapes rental property listings by region
- Collects property data including category, address, price, and room count
- Uses **Splash** to render JavaScript content for accurate data retrieval
- Implements pagination for comprehensive data coverage

## Project Structure
- **listis.py**: The main spider that handles requests, parses responses, and extracts property data.
- **Lua Script**: Controls Splash for JavaScript-rendered content.

## Technologies Used
- **Python**
- **Scrapy** - For web scraping
- **Scrapy-Splash** - For handling JavaScript-rendered content
- **JSON** - For data requests and responses

## Setup Instructions
1. **Install Dependencies**:
   ```bash
   pip install scrapy scrapy-splash
   ```

2. **Run Splash**:
   Splash is required to handle JavaScript-rendered pages. Run Splash as a Docker container:
   ```bash
   docker run -p 8050:8050 scrapinghub/splash
   ```

3. **Run the Spider**:
   Execute the spider to start scraping:
   ```bash
   scrapy crawl listis
   ```

## Example Output
Each scraped listing includes the following fields:
- `category`: Type of property (e.g., Residential, Commercial)
- `address`: Property location
- `price`: Rental price
- `roomes_number`: Number of rooms
- `url`: Direct link to the property listing

## Notes
- Some data, like `Year_built`, may sometimes be inconsistent due to the dynamic nature of the content.
