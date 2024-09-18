from django.shortcuts import render
from django.http import JsonResponse
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
import config
from django.contrib.auth.decorators import login_required
from .utils import save_uploaded_file, extract_headings_and_chunks
import re

# @login_required
# def add_data_view(request):
#     if request.method == 'POST':
#         text = request.POST.get('data', '')
#         docx_file = request.FILES.get('file')
#         if text:
#             try:
#                 document = Document(page_content=text, metadata={
#                     "title": "Wuzu Ki Sunnatien"})
#                 documents = [document]
#                 config.vectorstore.add_documents(documents=documents)
#                 # vector = config.embeddings.embed_query(text)
#                 # config.es.index(index=config.index_name, body={
#                 #     'chunk_text': text,
#                 #     'vector': vector
#                 # })
#                 return JsonResponse({"status": "success", "message": "Data saved and vectorized successfully!"})
#             except Exception as e:
#                 return JsonResponse({"status": "failure", "message": f"An error occurred: {str(e)}"})
#         elif docx_file:
#             try:
#                 docx_file_path = save_uploaded_file(docx_file)
#                 chunks = extract_headings_and_chunks(docx_file_path)
#                 documents = []
#                 for chunk in chunks:
#                     document = Document(page_content=chunk, metadata={
#                         "title": "Docx File Data"})
#                     documents.append(document)
#                 config.vectorstore.add_documents(documents=documents)
#                 return JsonResponse({"status": "success", "message": f'Docx file processed, {len(chunks)} chunks vectorized and saved!'})
#             except Exception as e:
#                 return JsonResponse({"status": "failure", "message": f"An error occurred with the doc file: {str(e)}"})
#         else:
#             return JsonResponse({"status": "failure", "message": "No data or file provided"})
#     return render(request, 'add_data/add_data_form.html')


@login_required
def add_data_view(request):
    if request.method == 'POST':
        paragraph = request.POST.get('paragraph', '').strip()
        questions_text = request.POST.get('question', '').strip()

        if paragraph and questions_text:
            # questions = [q.strip() + '؟' for q in questions_text.split('؟') if q.strip()]
            questions = [q.strip() + '؟' for q in re.split(r'[؟?]',
                                                           questions_text) if q.strip()]

            # for question in questions:
            #     question_vector = config.embeddings.embed_query(question)
            doc = {
                'paragraph': paragraph,
                'question': questions,
            }
            config.es.index(index="questions_paragraphs_v3", body=doc)

            return JsonResponse({
                'status': 'success',
                'message': 'Data successfully inserted into Elasticsearch for all questions.'
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Both fields are required.'})

    return render(request, 'add_data/add_data_form.html')
