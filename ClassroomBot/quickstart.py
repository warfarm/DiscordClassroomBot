from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
         'https://www.googleapis.com/auth/classroom.coursework.me']

def getScopes():
  return SCOPES

def main():
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json', SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

            # Tell the user to go to the authorization URL.
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print('Please go to this URL: {}'.format(auth_url))
            
            # The user will get an authorization code. This code is used to get the
            # access token.
            code = input('Enter the authorization code: ')
            
            flow.fetch_token(code=code)
            creds = flow.credentials
            # creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('classroom', 'v1', credentials=creds, static_discovery = False)

        # # Call the Classroom API
        # results = service.courses().list(pageSize=10).execute()
        # courses = results.get('courses', [])

        # if not courses:
        #     print('No courses found.')
        #     return
        # # Prints the names of the first 10 courses.
        # print('Courses:')
        # for course in courses:
        #     print(course['name'])

    except HttpError as error:
        print('An error occurred: %s' % error)

    return creds


if __name__ == '__main__':
    main()