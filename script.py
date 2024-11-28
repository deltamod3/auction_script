from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv

# Configure Selenium to use Chrome and load the page
options = Options()
options.add_argument("--headless")


# Initialize the Chrome driver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


def scrape_phillips(url):
    # Open the webpage
    driver.get(url)

    # Wait for images to load (adjust timeout as necessary)
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "phillips-image__image"))
    )

    # Now that the page is loaded, get the page source
    page_source = driver.page_source

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract auction name and date
    auction_name = (
        soup.find("h1", class_="auction-page__hero__title").get_text(strip=True)
        if soup.find("h1", class_="auction-page__hero__title")
        else "N/A"
    )
    auction_date = (
        soup.find("span", class_="auction-page__hero__date").get_text(strip=True)
        if soup.find("span", class_="auction-page__hero__date")
        else "N/A"
    )

    lots = []
    for lot in soup.find_all("li", class_="lot single-cell"):
        artist = (
            lot.find("p", class_="phillips-lot__description__artist").get_text(
                strip=True
            )
            if lot.find("p", class_="phillips-lot__description__artist")
            else "N/A"
        )
        title = (
            lot.find("p", class_="phillips-lot__description__title").get_text(
                strip=True
            )
            if lot.find("p", class_="phillips-lot__description__title")
            else "N/A"
        )
        estimate = (
            lot.find(
                "span", class_="phillips-lot__description__estimate__price"
            ).get_text(strip=True)
            if lot.find("span", class_="phillips-lot__description__estimate__price")
            else "N/A"
        )
        image_url = (
            lot.find("img", class_="phillips-image__image")["src"]
            if lot.find("img", class_="phillips-image__image")
            else "N/A"
        )
        detail_url = (
            lot.find("a", class_="phillips-lot__description")["href"]
            if lot.find("a", class_="phillips-lot__description")
            else "N/A"
        )

        # Clean up estimate to extract low and high prices
        low_estimate, high_estimate = "N/A", "N/A"
        if "-" in estimate:
            parts = estimate.replace("CHF", "").strip().split("-")
            low_estimate = parts[0].strip()
            high_estimate = parts[1].strip() if len(parts) > 1 else "N/A"

        # Append the extracted data
        lots.append(
            [
                auction_date,
                auction_name,
                title,
                low_estimate,
                high_estimate,
                detail_url,
                image_url,
                artist,
            ]
        )

    return lots


def scrape_tgp(url):
    # Open the webpage
    driver.get(url)

    # Wait for images to load (adjust timeout as necessary)
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "lot-card_card-title-wrapper__CZ4GI")
        )
    )

    # Now that the page is loaded, get the page source
    page_source = driver.page_source

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract auction name and date
    auction_name = (
        soup.find("div", class_="head-section_left-content__kHbkD")
        .find("h2")
        .get_text(strip=True)
        if soup.find("div", class_="head-section_left-content__kHbkD")
        and soup.find("h2")
        else "N/A"
    )

    auction_date = "N/A"
    date_element = soup.find("ul", class_="head-section_data-list__Yo6Tt")
    if date_element:
        date_span = date_element.find("span")
        if date_span:
            auction_date = date_span.get_text(strip=True)

    lots = []
    for lot in soup.find_all("div", class_="cards-container_lot-card-gird-item__H8Dkn"):
        title = (
            lot.find("p", class_="lot-card_card-title__EEZRj").get_text(strip=True)
            if lot.find("p", class_="lot-card_card-title__EEZRj")
            else "N/A"
        )
        estimate = (
            lot.find("div", class_="lot-card_estimate-bid__8g2bA")
            .find_all("span")[1]
            .get_text(strip=True)
            if lot.find("div", class_="lot-card_estimate-bid__8g2bA")
            else "N/A"
        )
        image_url = (
            lot.find("img", class_="lot-card_card-image__LUuZk")["src"]
            if lot.find("img", class_="lot-card_card-image__LUuZk")
            else "N/A"
        )
        detail_url = (
            lot.find("a", class_="lot-card_card-title-wrapper__CZ4GI")["href"]
            if lot.find("a", class_="lot-card_card-title-wrapper__CZ4GI")
            else "N/A"
        )

        # Clean up estimate to extract low and high prices
        low_estimate, high_estimate = "N/A", "N/A"
        if "-" in estimate:
            parts = estimate.replace("CHF", "").strip().split("-")
            low_estimate = parts[0].strip()
            high_estimate = parts[1].strip() if len(parts) > 1 else "N/A"

        # Append the extracted data
        lots.append(
            [
                auction_date,
                auction_name,
                title,
                low_estimate,
                high_estimate,
                detail_url,
                image_url,
            ]
        )

    return lots


def save_to_csv(data, filename="auction_data.csv"):
    headers = [
        "Auction Date",
        "Auction Name",
        "Lot Title",
        "Estimate Low",
        "Estimate High",
        "Description",
        "Main Image URL",
        "Artist Name",
    ]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


if __name__ == "__main__":
    phillips_url = "https://www.phillips.com/auctions/auction/CH060424"
    tgp_url = (
        "https://www.tgpauction.com/auction-catalog/street-pop-wine-sport_SHXH0L1NW0"
    )

    print("Start scraping phillips...")

    phillips_data = scrape_phillips(phillips_url)
    save_to_csv(phillips_data, "phillips_auction_data.csv")

    print("Scraping phillips is finished...")
    print("Start scraping tgp...")

    tgp_data = scrape_tgp(tgp_url)
    save_to_csv(tgp_data, "tgp_auction_data.csv")
    print("Scraping tgp is finished...")
