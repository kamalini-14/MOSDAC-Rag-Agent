import os
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import *


class MOSDACDownloader:

    def __init__(self):

        self.input_file = "../logs/discovered_urls.txt"

        self.error_file = "../logs/downloader_errors.txt"

        self.downloaded = set()

        self.extensions = {
            ".pdf": "../downloads/pdf",
            ".doc": "../downloads/docx",
            ".docx": "../downloads/docx",
            ".xls": "../downloads/xlsx",
            ".xlsx": "../downloads/xlsx",
            ".csv": "../downloads/csv",
            ".zip": "../downloads/zip"
        }

        for folder in self.extensions.values():
            os.makedirs(folder, exist_ok=True)

        open(self.error_file, "w").close()

    # --------------------------------------------------

    def get_extension(self, url):

        url = url.lower()

        for ext in self.extensions:

            if url.endswith(ext):
                return ext

        return None

    # --------------------------------------------------

    def download_file(self, url):

        extension = self.get_extension(url)

        if extension is None:
            return

        if url in self.downloaded:
            return

        try:

            response = requests.get(

                url,

                headers=HEADERS,

                timeout=REQUEST_TIMEOUT,

                stream=True

            )

            if response.status_code != 200:
                return

            folder = self.extensions[extension]

            filename = os.path.basename(url.split("?")[0])

            if filename == "":
                filename = "file" + extension

            filepath = os.path.join(folder, filename)

            with open(filepath, "wb") as f:

                for chunk in response.iter_content(1024):

                    if chunk:

                        f.write(chunk)

            self.downloaded.add(url)

            print(f"[DOWNLOADED] {filename}")

        except Exception as e:

            with open(self.error_file, "a") as f:

                f.write(f"{url} --> {e}\n")

    # --------------------------------------------------

    def run(self):

        if not os.path.exists(self.input_file):

            print("URL list not found.")

            return

        with open(self.input_file, "r") as f:

            urls = [line.strip() for line in f if line.strip()]

        print(f"\nScanning {len(urls)} webpages...\n")

        for page in urls:

            print(f"[PAGE] {page}")

            try:

                response = requests.get(

                    page,

                    headers=HEADERS,

                    timeout=REQUEST_TIMEOUT

                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "lxml")

                for tag in soup.find_all("a", href=True):

                    link = urljoin(page, tag["href"])

                    self.download_file(link)

                time.sleep(DELAY)

            except Exception as e:

                with open(self.error_file, "a") as f:

                    f.write(f"{page} --> {e}\n")

        print("\n======================================")

        print("DOWNLOADING COMPLETED")

        print("======================================")

        print("Downloaded Files:")

        for folder in self.extensions.values():

            print(folder)

        print("\nErrors:")

        print(self.error_file)


if __name__ == "__main__":

    downloader = MOSDACDownloader()

    downloader.run()