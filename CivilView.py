from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from scrapy import Selector
from Utils import *
import pandas as pd
import threading
import requests
import os


class Scraper:
    def __init__(self):
        self.filenm = datetime.now().strftime("%m-%d-%Y__%H-%M-%S")
        self.count = 0           # Number of counties processed
        self.cmp = []            # List to hold scraped data
        self.progress = 0        # Progress percentage (0-100)
        self.total_count = 0     # Total number of counties to process
        self.is_running = False  # Flag to prevent concurrent runs
        self.lock = threading.Lock()  # Protect shared variables

    def save_data(self):
        if not os.path.exists("Output"):
            os.mkdir("Output")
        df = pd.DataFrame(self.cmp)
        df.sort_values(by=["County Name"], inplace=True)
        df.to_excel(f"Output/{self.filenm}.xlsx", index=False)

    def get_dataframe(self):
        return pd.DataFrame(self.cmp)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.filenm = datetime.now().strftime("%m-%d-%Y__%H-%M-%S")
        self.cmp = []
        self.count = 0
        self.progress = 0
        print("Getting Data............")
        counties = self.get_counties()
        self.total_count = len(counties)
        if self.total_count == 0:
            self.progress = 100
            self.is_running = False
            return
        # Use ThreadPoolExecutor to process each county in parallel.
        with ThreadPoolExecutor() as executor:
            executor.map(self.get_data, counties)
        # Ensure progress is exactly 100% when finished.
        with self.lock:
            self.progress = 100
        self.is_running = False
        print("Completed!")

    @staticmethod
    def get_response(url: str):
        r = requests.get(url, headers=headers)
        return Selector(text=r.text)

    def get_counties(self):
        response = self.get_response(URL)
        cmp_links = []
        for item in response.xpath("//main//div[contains(@class, 'table')]//a"):
            link = "https://salesweb.civilview.com" + item.xpath("./@href").get()
            county = " ".join(item.xpath(".//text()").getall()).strip()
            if ", NJ" in county:
                cmp_links.append(link)
        return cmp_links

    def get_data(self, link):
        response = self.get_response(link)
        county_name = " ".join(response.xpath("//main//h1//text()").getall()).split(" - ")[0].strip()
        table_heads = []
        for item in response.xpath("//form//table//tr/th"):
            head = " ".join(item.xpath(".//text()").getall()).strip()
            table_heads.append(head)
        # Process each row in the table but update progress only once per county.
        for item in response.xpath("//form//table//tr[not(.//th)]"):
            fnl = {"County Name": county_name}
            for i, name in enumerate(table_heads):
                if name not in columns_needed:
                    continue
                value = " ".join(item.xpath(f"./td[{i+1}]//text()").getall()).strip()
                if "date" in name.lower():
                    value = value.split(" ")[0]
                fnl[name] = value
            self.cmp.append(fnl)
            print(f"Scraped data row for county: {county_name}")
        # When finished processing one county, update progress once.
        with self.lock:
            self.count += 1
            self.progress = int((self.count / self.total_count) * 100)
            # Clamp progress to 100%.
            if self.progress > 100:
                self.progress = 100
        print(f"Completed county {county_name}: progress {self.progress}%")
