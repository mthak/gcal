"""
Mostly the Google quickstart.py code with the "freebusy" service running.

Also shows how to make datetimes using pytz.

Follow these instructions to get access credentials:

    https://developers.google.com/google-apps/calendar/quickstart/python

"""

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import pytz

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'PATH_TO_MY_SECRETS.apps.googleusercontent.com.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    # ----------------------------------------------------------------------------------------------------------------
    # Add event
    tz = pytz.timezone('US/Central')
    start_datetime = tz.localize(datetime.datetime(2016, 1, 3, 8))
    stop_datetime = tz.localize(datetime.datetime(2016, 1, 3, 8, 30))
    event = {
      'summary': 'My Test Event',
      'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'dateTime': start_datetime.isoformat(),
        'timeZone': 'US/Central',
      },
      'end': {
        'dateTime': stop_datetime.isoformat(),
        'timeZone': 'US/Central',
      },
      'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
      ],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

    # ----------------------------------------------------------------------------------------------------------------
    # This event should be returned by freebusy
    the_datetime = tz.localize(datetime.datetime(2016, 1, 3, 0))
    the_datetime2 = tz.localize(datetime.datetime(2016, 1, 4, 8))
    body = {
      "timeMin": the_datetime.isoformat(),
      "timeMax": the_datetime2.isoformat(),
      "timeZone": 'US/Central',
      "items": [{"id": 'my.email@gmail.com'}]
    }

    eventsResult = service.freebusy().query(body=body).execute()
    cal_dict = eventsResult[u'calendars']
    for cal_name in cal_dict:
        print(cal_name, cal_dict[cal_name])


if __name__ == '__main__':
    main()