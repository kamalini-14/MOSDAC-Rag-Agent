import os
import json

import chromadb
from sentence_transformers import SentenceTransformer


class MOSDACEmbedding:

    def __init__(self):

        # ==================================================
        # PROJECT ROOT
        # ==================================================

        # embedding.py is inside:
        # satellite/crawler/embedding.py

        self.project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # ==================================================
        # INPUT CHUNKS
        # ==================================================

        self.input_file = os.path.join(
            self.project_root,
            "knowledge_base",
            "mosdac_chunks.jsonl"
        )

        # ==================================================
        # VECTOR DATABASE
        # ==================================================

        self.vector_db_folder = os.path.join(
            self.project_root,
            "knowledge_base",
            "vector_db"
        )

        os.makedirs(
            self.vector_db_folder,
            exist_ok=True
        )

        print("\nInput file:")
        print(self.input_file)

        print("\nVector database:")
        print(self.vector_db_folder)

        # ==================================================
        # EMBEDDING MODEL
        # ==================================================

        print("\nLoading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # ==================================================
        # CHROMADB
        # ==================================================

        print("\nConnecting to ChromaDB...")

        self.client = chromadb.PersistentClient(
            path=self.vector_db_folder
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="mosdac_documents"
            )
        )

        print("Connected to ChromaDB")

        print(
            "Existing vectors :",
            self.collection.count()
        )

    # ==================================================
    # CREATE EMBEDDINGS
    # ==================================================

    def create_embeddings(self):

        print("\n")
        print("=" * 60)
        print("CREATING MOSDAC EMBEDDINGS")
        print("=" * 60)

        # --------------------------------------------------
        # CHECK CHUNK FILE
        # --------------------------------------------------

        if not os.path.exists(
            self.input_file
        ):

            print(
                "\nChunk file not found!"
            )

            print(
                self.input_file
            )

            return

        # --------------------------------------------------
        # READ CHUNKS
        # --------------------------------------------------

        documents = []
        ids = []
        metadatas = []

        with open(
            self.input_file,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                chunk = json.loads(line)

                content = chunk.get(
                    "content",
                    ""
                ).strip()

                if not content:
                    continue

                chunk_id = chunk.get(
                    "chunk_id"
                )

                if not chunk_id:
                    continue

                documents.append(
                    content
                )

                ids.append(
                    str(chunk_id)
                )

                # --------------------------------------------------
                # IMAGE INFORMATION
                # --------------------------------------------------

                images = chunk.get(
                    "images",
                    []
                )

                if not isinstance(images, list):
                    images = [str(images)]

                image_string = "|".join(
                    str(image)
                    for image in images
                )

                # --------------------------------------------------
                # METADATA
                # --------------------------------------------------

                metadatas.append({

                    "source_type":
                        str(
                            chunk.get(
                                "source_type",
                                ""
                            )
                        ),

                    "source":
                        str(
                            chunk.get(
                                "source",
                                ""
                            )
                        ),

                    "page":
                        str(
                            chunk.get(
                                "page",
                                ""
                            )
                        ),

                    "images":
                        image_string
                })

        print(
            "\nChunks found :",
            len(documents)
        )

        if not documents:

            print(
                "No chunks available!"
            )

            return

        # ==================================================
        # GENERATE EMBEDDINGS
        # ==================================================

        print(
            "\nGenerating embeddings..."
        )

        embeddings = self.model.encode(
            documents,
            show_progress_bar=True
        )

        # ==================================================
        # STORE IN CHROMADB
        # ==================================================

        print(
            "\nStoring vectors..."
        )

        self.collection.upsert(

            ids=ids,

            documents=documents,

            embeddings=embeddings.tolist(),

            metadatas=metadatas

        )

        # ==================================================
        # FINAL INFORMATION
        # ==================================================

        print("\n" + "=" * 60)
        print("EMBEDDINGS CREATED SUCCESSFULLY")
        print("=" * 60)

        print(
            "Chunks processed :",
            len(documents)
        )

        print(
            "Vectors in ChromaDB :",
            self.collection.count()
        )

        print(
            "Vector DB :",
            self.vector_db_folder
        )


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    embedding = MOSDACEmbedding()

    embedding.create_embeddings()