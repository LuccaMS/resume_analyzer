from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_json_with_jsonloader(file_path, jq_schema='.'):
    """
    Load JSON using LangChain's JSONLoader
    jq_schema: JQ schema to extract specific fields (default: '.' for entire document)
    """
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=jq_schema,
        text_content=False  # Set to True if you want to extract text content only
    )
    documents = loader.load()
    return documents


def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split documents into chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    chunked_docs = text_splitter.split_documents(documents)
    return chunked_docs
