import json
import sys

import chromadb
chroma_client = chromadb.PersistentClient('data/interim/chromadir')

collection = chroma_client.get_or_create_collection(name="my_collection")

def embed(data):
    print(f'adding {len(data)} items')
    for item in data:
        desc = item.pop('description', None) or item['title']

        collection.add(
            documents=desc,
            metadatas=item,
            ids=item['link']
        )


if __name__ == '__main__':
    args = sys.argv[1:]

    file = sys.stdin
    if args:
        file = open(args[0])

    data = json.load(file)

    embed(data)
