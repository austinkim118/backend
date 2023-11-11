from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json

from django.views.decorators.csrf import csrf_exempt
# this is not good???
#@csrf_exempt
def login(request):
    # example login info to use in isloginInfoValid()
    dummy_login_data = {
        "username": "Austin",
        "password": "Kim"
    }

    if request.method == 'POST':
        # Retrieve the login data from the request's body
        login_data = json.loads(request.body.decode('utf-8'))

        # Validate the user's credentials
        username = login_data.get('username')
        password = login_data.get('password')

        # Perform authentication and respond with the appropriate data
        if is_valid_credentials(username, password, dummy_login_data):
            # Authentication was successful
            response_data = {'message': 'Login successful'}
            return JsonResponse(response_data)
        else:
            # Authentication failed
            response_data = {'message': 'Login failed'}
            return JsonResponse(response_data, status=401)  # Unauthorized

    # For GET requests, return a "Method Not Allowed" response
    return HttpResponse("Method not allowed", status=405)

    ## set up REST framework?
    # user_input = request.data

    # if (
    #     user_input.get("usernamd") == dummy_login_data.get("username")
    #     and user_input.get("password") == dummy_login_data.get("password")
    # ):
    #     verified = True
    # else:
    #     verified = False

    # response_data = {"verified": verified}
    # return response_data

def is_valid_credentials(username, password, dummy):
    if username == dummy.get('username') and password == dummy.get('password'):
        return True
    else:
        return False