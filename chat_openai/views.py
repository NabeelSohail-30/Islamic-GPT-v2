from django.shortcuts import render, redirect
from .models import OpenAiMessage
from django.contrib.auth.decorators import login_required
from .utils import get_response
from django.http import JsonResponse
from .model_message import Messages
from django.http import HttpResponse
import csv


@login_required
def chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()

        if user_input:
            user_message = OpenAiMessage.objects.create(
                user=request.user, role='user', content=user_input)

            response = get_response(user_input)
            bot_message = OpenAiMessage.objects.create(
                user=request.user, role='bot', content=response)

            Messages.objects.create(
                query=user_input,
                response=response
            )

            response_data = {
                'status': 'success',
                'messages': [
                    {
                        'role': user_message.role,
                        'username': user_message.user.username,
                        'content': user_message.content,
                        'timestamp': user_message.timestamp
                    },
                    {
                        'role': bot_message.role,
                        'username': bot_message.user.username,
                        'content': bot_message.content,
                        'timestamp': bot_message.timestamp
                    }
                ]
            }

            return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def view_chat(request):
    messages = OpenAiMessage.objects.filter(
        user=request.user).order_by('timestamp')

    return render(request, 'chat_openai/chat.html', {'messages': messages})


@login_required
def export_messages_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="messages.csv"'

    writer = csv.writer(response)

    writer.writerow(['Query', 'Response', 'Timestamp'])

    messages = Messages.objects.all()

    for message in messages:
        writer.writerow([message.query, message.response, message.timestamp])

    return response
