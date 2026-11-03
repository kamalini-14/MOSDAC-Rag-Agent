import os
import chromadb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

vector_db_folder = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "vector_db"
)

print("Vector DB path:")
print(vector_db_folder)

client = chromadb.PersistentClient(
    path=vector_db_folder
)

collections = client.list_collections()

print("\nCollections found:")

if not collections:
    print("NO COLLECTIONS FOUND")
else:
    for collection in collections:
        print(
            f"- {collection.name}"
        )