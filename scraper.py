import requests
import os
from bs4 import BeautifulSoup
import re
import json
import yaml

# Function to load URLs from a YAML file
def load_urls_from_yaml(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        return config['urls']

# Function to scrape job listings from a given URL
def scrape_jobs(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="jobsearch-result")

    def get_pub_date(result):
        pub_element = result.find("div", class_="jix-toolbar__pubdate")
        if pub_element:
            text_with_extra_spaces = pub_element.get_text()
            pub_date = re.sub(r'\s+', ' ', text_with_extra_spaces).strip("Indrykket: ")
            return pub_date
        return ""

    results_sorted = sorted(results, key=lambda result: get_pub_date(result), reverse=True)
    job_listings = []

    for result in results_sorted:
        title_element = result.find("h4").find("a") if result.find("h4") else None
        company_element = result.find("div", class_="jix-toolbar-top__company")
        location_element = (
            result.find("div", class_="jobad-element-area").find("span")
            if result.find("div", class_="jobad-element-area")
            else None
        )
        link_element = result.find("a", class_="btn btn-sm btn-block btn-primary d-md-none mt-2 seejobmobil")
        
        if (
            title_element is not None
            and company_element is not None
            and location_element is not None
        ):
            title = title_element.text.strip() if title_element else ""
            company = (
                company_element.find("a").text.strip()
                if company_element.find("a")
                else ""
            )
            location = location_element.text.strip()
            job_URL = link_element.get("href")
            pub_date = get_pub_date(result)
            
            job_listing = {
                "pub_date": pub_date,
                "title": title,
                "company": company,
                "location": location,
                "job_URL": job_URL
            }
            job_listings.append(job_listing)

    return job_listings

# Main function to run the scraping for all URLs in the YAML file
def main():
    urls = load_urls_from_yaml("config.yml")
    all_job_listings = []

    for url in urls:
        job_listings = scrape_jobs(url)
        all_job_listings.extend(job_listings)

    # Ensure the directory exists
    #os.makedirs("it", exist_ok=True)

    # Write to JSON file
    with open("data.json", "w") as json_file:
        json.dump(all_job_listings, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
