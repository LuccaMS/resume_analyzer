from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class RetrieveResumesInput(BaseModel):
    query: str = Field(description="Query to search for in resumes")

class RetrieveResumesTool(BaseTool):
    name: str = "retrieve_resumes"
    description: str = "Search and return information about people resumes with source information."
    args_schema: Type[BaseModel] = RetrieveResumesInput
    retriever: object = Field(exclude=True)  # Exclude from serialization
    
    def __init__(self, retriever, **kwargs):
        super().__init__(retriever=retriever, **kwargs)
    
    def _run(self, query: str) -> str:
        # Get documents from retriever
        documents = self.retriever.invoke(query)
        
        # Format response with metadata
        results = []
        for doc in documents:
            # Extract filename from source path
            source_file = doc.metadata.get('source', 'Unknown')
            if '/' in source_file:
                source_file = source_file.split('/')[-1]
            
            result = {
                "content": doc.page_content,
                "source": source_file,
                "metadata": doc.metadata
            }
            results.append(result)
        
        # Format as readable string for LLM
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"Document {i}:\nSource: {result['source']}\nContent: {result['content']}\n"
            formatted_results.append(formatted_result)
        
        return "\n---\n".join(formatted_results)

# Usage
#retriever_tool = RetrieveResumesTool(retriever=retriever)
#retriever_tool.invoke("btg")