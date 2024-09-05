from django.shortcuts import render
from django.http import JsonResponse
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
import os
from pinecone import Pinecone
import config


def add_data_view(request):
    if request.method == 'POST':
        text = request.POST.get('data', '')

        if text:
            try:
                document = Document(page_content=text, metadata={
                    "title": "User Input Data"})
                documents = [document]

                config.vectorstore.add_documents(documents=documents)

                return JsonResponse({"status": "success", "message": "Data saved and vectorized successfully!"})

            except Exception as e:
                return JsonResponse({"status": "failure", "message": f"An error occurred: {str(e)}"})
        else:
            return JsonResponse({"status": "failure", "message": "No data provided"})

    return render(request, 'add_data/add_data_form.html')
