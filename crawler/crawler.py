import os
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

from config import *


class MOSDACCrawler:

    def __init__(self):

        self.visited = set()

        self.queue = deque([BASE_URL])

        os.makedirs("../logs", exist_ok=True)

        self.error_file = "../logs/crawler_errors.txt"
        self.url_file = "../logs/discovered_urls.txt"

        open(self.error_file, "w").close()
        open(self.url_file, "w").close()

    # ----------------------------------------------------

    def is_internal(self, url):

        return urlparse(url).netloc == urlparse(BASE_URL).netloc

    # ----------------------------------------------------

    def is_valid(self, url):

        if not url.startswith("http"):
            return False

        lower = url.lower()

        if lower.startswith("mailto:"):
            return False

        if lower.startswith("javascript:"):
            return False

        if lower.startswith("tel:"):
            return False

        if lower.endswith(".pdf"):
            return False

        if lower.endswith(".docx"):
            return False

        if lower.endswith(".xlsx"):
            return False

        if lower.endswith(".zip"):
            return False

        return True

    # ----------------------------------------------------

    def crawl(self):

        discovered = []

        while self.queue:

            current_url = self.queue.popleft()

            if current_url in self.visited:
                continue

            print(f"[VISITING] {current_url}")

            try:

                response = requests.get(
                    current_url,
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT
                )

                if response.status_code != 200:

                    with open(self.error_file, "a") as f:
                        f.write(
                            f"{current_url} --> HTTP {response.status_code}\n"
                        )

                    continue

                content_type = response.headers.get(
                    "Content-Type", ""
                )

                if "text/html" not in content_type:
                    continue

                self.visited.add(current_url)

                discovered.append(current_url)

                with open(self.url_file, "a") as f:
                    f.write(current_url + "\n")

                soup = BeautifulSoup(
                    response.text,
                    "lxml"
                )

                for tag in soup.find_all("a", href=True):

                    href = tag["href"].strip()

                    absolute = urljoin(current_url, href)

                    absolute = absolute.split("#")[0]

                    absolute = absolute.rstrip("/")

                    if not self.is_valid(absolute):
                        continue

                    if not self.is_internal(absolute):
                        continue

                    if absolute not in self.visited:
                        self.queue.append(absolute)

                time.sleep(DELAY)

            except requests.exceptions.RequestException as e:

                with open(self.error_file, "a") as f:
                    f.write(f"{current_url} --> {e}\n")

        return discovered


if __name__ == "__main__":

    crawler = MOSDACCrawler()

    urls = crawler.crawl()

    print()

    print("=" * 60)
    print("CRAWLING COMPLETED")
    print("=" * 60)
    print("Total Pages :", len(urls))
    print("Errors Logged : logs/crawler_errors.txt")
    print("URLs Saved    : logs/discovered_urls.txt")
    print("=" * 60)