import os
import json

from pypdf import PdfReader

from config import *


class MOSDACKnowledgeBase:

    def __init__(self):

        # -----------------------------------------
        # INPUT FOLDERS
        # -----------------------------------------

        self.html_folder = "../downloads/html"
        self.pdf_folder = "../downloads/pdf"

        # -----------------------------------------
        # KNOWLEDGE BASE
        # -----------------------------------------

        self.output_folder = "../knowledge_base"

        self.image_folder = os.path.join(
            self.output_folder,
            "images"
        )

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        os.makedirs(
            self.image_folder,
            exist_ok=True
        )

        # JSONL knowledge base
        self.output_file = os.path.join(
            self.output_folder,
            "mosdac_knowledge.jsonl"
        )

    # ==================================================
    # HTML CONTENT
    # ==================================================

    def get_html_content(self):

        print("\n========================================")
        print("READING HTML TEXT FILES")
        print("========================================")

        documents = []

        if not os.path.exists(self.html_folder):

            print("HTML folder not found!")

            return documents

        files = [
            file
            for file in os.listdir(self.html_folder)
            if file.lower().endswith(".txt")
        ]

        print("HTML files found :", len(files))

        for index, file in enumerate(files, start=1):

            filepath = os.path.join(
                self.html_folder,
                file
            )

            print(
                f"[{index}/{len(files)}] "
                f"Reading : {file}"
            )

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8"
                ) as f:

                    content = f.read()

                if not content.strip():
                    continue

                documents.append({

                    "source_type": "HTML",

                    "source": file,

                    "page": None,

                    "content": content,

                    "images": []

                })

            except Exception as e:

                print(
                    f"Error reading HTML {file}: {e}"
                )

        return documents

    # ==================================================
    # EXTRACT PDF PAGE
    # ==================================================

    def extract_pdf_page(
        self,
        page,
        pdf_name,
        page_number
    ):

        text = ""

        images = []

        # ------------------------------------------
        # Extract text
        # ------------------------------------------

        try:

            page_text = page.extract_text()

            if page_text:
                text = page_text

        except Exception as e:

            print(
                f"Text extraction error "
                f"in {pdf_name}, page {page_number}: {e}"
            )

        # ------------------------------------------
        # Extract images
        # ------------------------------------------

        try:

            page_images = page.images

            for image_index, image in enumerate(
                page_images,
                start=1
            ):

                image_name = (
                    f"{pdf_name}_"
                    f"page_{page_number}_"
                    f"image_{image_index}"
                    f"{image.name[image.name.rfind('.'):]}"
                )

                image_path = os.path.join(
                    self.image_folder,
                    image_name
                )

                with open(
                    image_path,
                    "wb"
                ) as image_file:

                    image_file.write(
                        image.data
                    )

                # Relative path stored in metadata
                relative_path = os.path.join(
                    "images",
                    image_name
                )

                images.append(
                    relative_path
                )

                print(
                    f"      Image saved : "
                    f"{image_name}"
                )

        except Exception as e:

            print(
                f"Image extraction error "
                f"in {pdf_name}, page {page_number}: {e}"
            )

        return text, images

    # ==================================================
    # PDF CONTENT
    # ==================================================

    def get_pdf_content(self):

        print("\n========================================")
        print("READING PDF FILES")
        print("========================================")

        documents = []

        if not os.path.exists(self.pdf_folder):

            print("PDF folder not found!")

            return documents

        files = [
            file
            for file in os.listdir(self.pdf_folder)
            if file.lower().endswith(".pdf")
        ]

        print("PDF files found :", len(files))

        for index, file in enumerate(files, start=1):

            filepath = os.path.join(
                self.pdf_folder,
                file
            )

            print(
                f"\n[{index}/{len(files)}] "
                f"Processing PDF : {file}"
            )

            try:

                reader = PdfReader(filepath)

                pdf_name = os.path.splitext(file)[0]

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    print(
                        f"   Page {page_number}/"
                        f"{len(reader.pages)}"
                    )

                    text, images = self.extract_pdf_page(
                        page,
                        pdf_name,
                        page_number
                    )

                    # Save page even if it contains only image
                    if text.strip() or images:

                        documents.append({

                            "source_type": "PDF",

                            "source": file,

                            "page": page_number,

                            "content": text,

                            "images": images

                        })

            except Exception as e:

                print(
                    f"PDF Error : {file}"
                )

                print(e)

        return documents

    # ==================================================
    # CREATE KNOWLEDGE BASE
    # ==================================================

    def create_knowledge_base(self):

        print("\n")
        print("=" * 60)
        print("CREATING MOSDAC KNOWLEDGE BASE")
        print("=" * 60)

        # ------------------------------------------
        # HTML
        # ------------------------------------------

        html_documents = self.get_html_content()

        # ------------------------------------------
        # PDF
        # ------------------------------------------

        pdf_documents = self.get_pdf_content()

        # ------------------------------------------
        # COMBINE
        # ------------------------------------------

        all_documents = (
            html_documents +
            pdf_documents
        )

        print("\n========================================")
        print("KNOWLEDGE BASE SUMMARY")
        print("========================================")

        print(
            "HTML documents :",
            len(html_documents)
        )

        print(
            "PDF pages      :",
            len(pdf_documents)
        )

        print(
            "Total records  :",
            len(all_documents)
        )

        # ------------------------------------------
        # WRITE JSONL
        # ------------------------------------------

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as f:

            for document in all_documents:

                f.write(
                    json.dumps(
                        document,
                        ensure_ascii=False
                    )
                    + "\n"
                )

        print("\n" + "=" * 60)
        print("KNOWLEDGE BASE CREATED SUCCESSFULLY")
        print("=" * 60)

        print(
            "Knowledge Base :",
            self.output_file
        )

        print(
            "Images folder  :",
            self.image_folder
        )


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    kb = MOSDACKnowledgeBase()

    kb.create_knowledge_base()