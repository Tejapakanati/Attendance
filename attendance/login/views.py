from rest_framework.authentication import get_authorization_header
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import Userserializer
from rest_framework.response import Response
from .models import User
from rest_framework.exceptions import APIException,AuthenticationFailed
from rest_framework.permissions import AllowAny
from .Authentication  import create_access_token,create_refresh_token,decode_refresh_token,decode_access_token



class register_view(APIView):
    def post(self,request):
        serializer = Userserializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
class login_view(APIView):
    def post(self,request):
        user = User.objects.filter(email=request.data['email']).first()
        if not user: 
            raise APIException ('invalid credentials')
        if not user.check_password(request.data['password']):
            raise APIException('invalid credentials')
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()

        response.set_cookie(key='refreshToken' , value=refresh_token,httponly=True)
        response.data = {
            'token' : access_token
        }
        return response
    
# Authenticated user
class user_view(APIView):
    def get(self,request):
        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2: # bearer and token the token will be second value
            token = auth[1].decode('utf-8') # that token will be decode to utf-8 (access token)
            id = decode_access_token(token) # decode the access token to fetch the id

            # fetch the user based on the id
            user = User.objects.filter(pk=id).first()

            return Response(Userserializer(user).data)
        
        raise AuthenticationFailed('unauthenticated')


#refresh that access token
#we have to validate the token and then generate new access token
# @method_decorator(csrf_exempt, name='dispatch')
class refresh_view(APIView):
    # permission_classes = [AllowAny]
    def post(self,request):
        refresh_token = request.COOKIES.get('refreshToken') # get the refresh token from the cookies
        id = decode_refresh_token(refresh_token) # decode the refresh token
        access_token = create_access_token(id) # generaate new access token

        return Response({
            'token' : access_token #return that new access token
        })

# remove the refresh token
class logout_view(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie(key = 'refreshToken')
        response.data={
            'message':'success'
        }

        return response
        
    
class home_view(APIView):
    def get(self, request):
        auth_header = get_authorization_header(request).split() # get token from the autherization header
        if auth_header and len(auth_header) == 2:
            try:
                token = auth_header[1].decode('utf-8') #decode the token
                id = decode_access_token(token) # Get the  ID from the decoded token
                user = User.objects.get(pk=id)  # Fetch the user from the database
            except Exception as e:
                raise AuthenticationFailed(str(e)) #Raises a new AuthenticationFailed exception to inform the client about the authentication failure, 
                                                   #using the original error message for context.
            
            data = {
                'messages' : 'welcome to home page!',
                'user' : user.email

            }

            return Response(data)
        return AuthenticationFailed('unauthorised') # If the token is missing or incorrect, raise an error