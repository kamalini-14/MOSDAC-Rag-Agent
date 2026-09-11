import os
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from config import *


class MOSDACParser:

    def __init__(self):

        self.input_file = "../logs/discovered_urls.txt"

        self.output_folder = "../downloads/html"

        self.error_file = "../logs/parser_errors.txt"

        os.makedirs(self.output_folder, exist_ok=True)

        open(self.error_file, "w").close()

    # --------------------------------------------------------

    def sanitize_filename(self, url):

        parsed = urlparse(url)

        name = parsed.path.strip("/")

        if name == "":
            name = "home"

        name = name.replace("/", "_")
        name = name.replace("?", "_")
        name = name.replace("&", "_")
        name = name.replace("=", "_")
        name = name.replace(":", "_")

        return name + ".txt"

    # --------------------------------------------------------

    def is_useful_url(self, url):

        lower = url.lower()

        skip_extensions = (
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".rar",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".xml",
            ".rss"
        )

        if lower.endswith(skip_extensions):
            return False

        return True

    # --------------------------------------------------------

    def extract_text(self, html):

        soup = BeautifulSoup(html, "lxml")

        title = ""

        if soup.title:
            title = soup.title.get_text(strip=True)

        remove_tags = [
            "script",
            "style",
            "noscript",
            "header",
            "footer",
            "nav",
            "aside",
            "form",
            "iframe"
        ]

        for tag in soup(remove_tags):
            tag.decompose()

        text = soup.get_text(separator="\n")

        cleaned = []

        for line in text.splitlines():

            line = line.strip()

            if line != "":
                cleaned.append(line)

        content = "\n".join(cleaned)

        return title, content

    # --------------------------------------------------------

    def log_error(self, url, reason):

        with open(self.error_file, "a", encoding="utf-8") as f:
            f.write(f"{url} --> {reason}\n")

    # --------------------------------------------------------

    def parse(self):

        if not os.path.exists(self.input_file):

            print("discovered_urls.txt not found")

            return

        with open(self.input_file, "r", encoding="utf-8") as f:

            urls = []

            for line in f:

                line = line.strip()

                if line != "":
                    urls.append(line)

        total = len(urls)

        success = 0

        failed = 0

        print(f"\nTotal URLs : {total}\n")

        for i, url in enumerate(urls, start=1):

            print(f"[{i}/{total}] Parsing : {url}")

            if not self.is_useful_url(url):

                failed += 1

                self.log_error(url, "Skipped (Non HTML Resource)")

                continue

            try:

                response = requests.get(

                    url,

                    headers=HEADERS,

                    timeout=REQUEST_TIMEOUT,

                    allow_redirects=True

                )

                if response.status_code != 200:

                    failed += 1

                    self.log_error(url, f"HTTP {response.status_code}")

                    continue

                content_type = response.headers.get("Content-Type", "")

                if "html" not in content_type.lower():

                    failed += 1

                    self.log_error(url, "Not HTML")

                    continue

                title, content = self.extract_text(response.text)

                if len(content) < 200:

                    failed += 1

                    self.log_error(url, "Very Little Content")

                    continue

                lower = content.lower()

                blocked_words = [

                    "login",

                    "logout",

                    "access denied",

                    "sign in"

                ]

                blocked = False

                for word in blocked_words:

                    if word in lower:

                        blocked = True
                        break

                if blocked:

                    failed += 1

                    self.log_error(url, "Login/Restricted Page")

                    continue

                filename = self.sanitize_filename(url)

                filepath = os.path.join(

                    self.output_folder,

                    filename

                )

                with open(

                    filepath,

                    "w",

                    encoding="utf-8"

                ) as f:

                    f.write(f"TITLE : {title}\n")
                    f.write(f"URL : {url}\n\n")
                    f.write(content)

                success += 1

                time.sleep(DELAY)

            except Exception as e:

                failed += 1

                self.log_error(url, str(e))

        print("\n" + "=" * 60)
        print("PARSING COMPLETED")
        print("=" * 60)
        print(f"Successful : {success}")
        print(f"Failed     : {failed}")
        print(f"Saved To   : {self.output_folder}")
        print(f"Errors     : {self.error_file}")
        print("=" * 60)


if __name__ == "__main__":

    parser = MOSDACParser()

    parser.parse()