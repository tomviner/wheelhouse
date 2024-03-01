"""Query.

Usage:
    python -m wheelhouse.query
"""


from pathlib import Path

import chromadb

ROOT = Path(".")

chroma_client = chromadb.PersistentClient(str(ROOT / "data" / "interim" / "chromadir"))

collection = chroma_client.get_or_create_collection(name="my_collection")

results = collection.query(query_texts=["video"], n_results=2)
# {
#     'ids': [[]],
#     'distances': [[]],
#     'metadatas': [[]],
#     'embeddings': None,
#     'documents': [[]],
#     'uris': None,
#     'data': None
# }

for metadata in results["metadatas"]:
    for m in metadata:
        print(m["organisation"])
