from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response

class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = InstalledAppFlow.from_client_secrets_file(
            'django_project/client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['google_auth_state'] = state
        return HttpResponseRedirect(authorization_url)

class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('google_auth_state', None)
        flow = InstalledAppFlow.from_client_secrets_file(
            'django_project/client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            state=state
        )
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
        )
        credentials = flow.credentials

        service = build('calendar', 'v3', credentials=credentials)
        events = service.events().list(calendarId='primary').execute()
        
        return Response(events)
