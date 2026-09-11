import os
import psycopg2

from config import *


class MOSDACDatabase:

    def __init__(self):

        self.connection = psycopg2.connect(

            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD

        )

        self.cursor = self.connection.cursor()

    # -------------------------------------------------

    def insert_document(self, title, url, file_path, content):

        query = """

        INSERT INTO documents
        (title, url, file_path, content)

        VALUES (%s,%s,%s,%s)

        ON CONFLICT (url)

        DO NOTHING;

        """

        self.cursor.execute(

            query,

            (
                title,
                url,
                file_path,
                content
            )

        )

    # -------------------------------------------------

    def save_all(self):

        self.connection.commit()

    # -------------------------------------------------

    def close(self):

        self.cursor.close()

        self.connection.close()


# ======================================================

if __name__ == "__main__":

    db = MOSDACDatabase()

    folder = "../downloads/html"

    count = 0

    for file in os.listdir(folder):

        if not file.endswith(".txt"):
            continue

        filepath = os.path.join(folder, file)

        with open(filepath, "r", encoding="utf-8") as f:

            text = f.read()

        lines = text.split("\n")

        title = ""

        url = ""

        content = ""

        for line in lines:

            if line.startswith("TITLE :"):

                title = line.replace("TITLE :", "").strip()

            elif line.startswith("URL :"):

                url = line.replace("URL :", "").strip()

            else:

                content += line + "\n"

        db.insert_document(

            title,
            url,
            filepath,
            content

        )

        count += 1

    db.save_all()

    db.close()

    print()

    print("=" * 60)

    print("DATABASE STORAGE COMPLETED")

    print("Total Documents Stored :", count)

    print("=" * 60)