import json
import requests
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        print("Incoming webhook message:", json.dumps(payload, indent=2))

        entry = payload.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        message = value.get('messages', [])[0]

        if message and message.get('type') == 'text':
            business_phone_number_id = value.get('metadata', {}).get('phone_number_id')
            message_id = message.get('id')
            from_number = message.get('from')
            text_body = message.get('text', {}).get('body')

            reply_message = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": "Echo: " + text_body},
                "context": {"message_id": message_id}
            }

            headers = {
                "Authorization": f"Bearer {settings.GRAPH_API_TOKEN}"
            }

            # Send reply message
            requests.post(f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                          headers=headers, json=reply_message)

            # Mark message as read
            mark_read_message = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            requests.post(f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                          headers=headers, json=mark_read_message)

        return JsonResponse({'status': 'success'})

    elif request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WEBHOOK_VERIFY_TOKEN:
            print("Webhook verified successfully!")
            return HttpResponse(challenge)
        else:
            return HttpResponseForbidden()

def index(request):
    return HttpResponse("<pre>Nothing to see here. Checkout README.md to start.</pre>")
