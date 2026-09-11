import os
import json


class MOSDACChunker:

    def __init__(self):

        self.input_file = (
            "../knowledge_base/"
            "mosdac_knowledge.jsonl"
        )

        self.output_file = (
            "../knowledge_base/"
            "mosdac_chunks.jsonl"
        )

        # Chunk settings
        self.chunk_size = 1000
        self.chunk_overlap = 200

    # ==================================================
    # CHUNK TEXT
    # ==================================================

    def create_chunks(self, text):

        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[start:end]

            # Try to end at a sentence
            if end < len(text):

                last_period = chunk.rfind(".")

                if last_period > 500:

                    end = start + last_period + 1

                    chunk = text[start:end]

            chunks.append(
                chunk.strip()
            )

            start = end - self.chunk_overlap

        return chunks

    # ==================================================
    # PROCESS KNOWLEDGE BASE
    # ==================================================

    def chunk_documents(self):

        print("\n")
        print("=" * 60)
        print("CHUNKING MOSDAC KNOWLEDGE BASE")
        print("=" * 60)

        if not os.path.exists(self.input_file):

            print(
                "Knowledge Base not found!"
            )

            return

        total_chunks = 0

        with open(
            self.input_file,
            "r",
            encoding="utf-8"
        ) as input_file, open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as output_file:

            for line in input_file:

                document = json.loads(line)

                text = document.get(
                    "content",
                    ""
                )

                chunks = self.create_chunks(
                    text
                )

                for index, chunk in enumerate(
                    chunks,
                    start=1
                ):

                    chunk_data = {

                        "chunk_id":
                            f"{document['source']}"
                            f"_"
                            f"{document.get('page', 'NA')}"
                            f"_"
                            f"{index}",

                        "source_type":
                            document["source_type"],

                        "source":
                            document["source"],

                        "page":
                            document.get("page"),

                        "content":
                            chunk,

                        "images":
                            document.get(
                                "images",
                                []
                            )

                    }

                    output_file.write(
                        json.dumps(
                            chunk_data,
                            ensure_ascii=False
                        )
                        + "\n"
                    )

                    total_chunks += 1

        print("\n" + "=" * 60)
        print("CHUNKING COMPLETED")
        print("=" * 60)

        print(
            "Total chunks :",
            total_chunks
        )

        print(
            "Output :",
            self.output_file
        )


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    chunker = MOSDACChunker()

    chunker.chunk_documents()