from django.shortcuts import render

from django.middleware.csrf import get_token
from django.http import JsonResponse, HttpResponse
from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

class AuthenticateUserView(View):
    def post(self, request):
        user_input = json.loads(request.body)
        username = user_input.get('username')
        password = user_input.get('password')

        if username == 'Austin' and password == 'Kim':
            return JsonResponse({'authenticated': True})
        else:
            return JsonResponse({'authenticated': False})
        
    def get(self, request):
        return HttpResponse("Received GET method: Method not allowed")