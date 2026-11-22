"""Day 3: query an EXISTING Azure AI Search keyword index.
Not vector search: use Microsoft's vector quickstart to add an embedding field.
Expected sample index fields: id, title, content (adjust to your index schema).
Run: python -m app.azure_search_demo
"""
import os
from dotenv import load_dotenv
load_dotenv()


def search_azure(question: str):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.environ["AZURE_SEARCH_INDEX"],
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
    )
    results = client.search(search_text=question, top=3)
    return [dict(result) for result in results]


if __name__ == "__main__":
    for doc in search_azure("home loan documents"):
        print(doc)
