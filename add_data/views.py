from django.shortcuts import render
from django.http import JsonResponse
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
import config
from django.contrib.auth.decorators import login_required
from .utils import save_uploaded_file, extract_headings_and_chunks
import re
import logging

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(message)s',
    encoding='utf-8'
)


@login_required
def view_page(request):
    return render(request, 'add_data/add_data_form.html')


@login_required
def add_data_view(request):
    if request.method == 'POST':
        logging.info(f"Request received")
        paragraph = request.POST.get('paragraph', '').strip()
        questions_text = request.POST.get('question', '').strip()

        logging.info(f"Paragraph: {paragraph}")
        logging.info(f"Questions: {questions_text}")

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
            config.es.index(index="questions_paragraphs_v4", body=doc)

            logging.info(
                f"Data successfully inserted into Elasticsearch for all questions.")

            return JsonResponse({
                'status': 'success',
                'message': 'Data successfully inserted into Elasticsearch for all questions.'
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Both fields are required.'})

    return render(request, 'add_data/add_data_form.html')
