import json
import requests

class PushBullet():
    """
    A PushBullet class with the following operations:
        -   Create push notification request to the PushBullet API.

        Constants:
            -   ACCESS_TOKEN: access token for the PushBullet API.
            Can be found here: https://docs.pushbullet.com/v1/
            -   API_ENDPOINTS: endpoints of the PushBullet API.
    """
    API_ENDPOINTS = {
        'pushes': 'https://api.pushbullet.com/v2/pushes'
    }

    def __init__(self, access_token):
        self.access_token = access_token

    def push_notification(self, title, body):
        '''
        Push notification to PushBullet through PushBullet API

        Inputs:
            -   title: title of the notification
            -   body: detailed content of the notification
        '''
        payload = {"body": body, "title": title, "type": "note"}
        headers = {'Access-Token': self.access_token,
                   'Content-Type': 'application/json'}
        response = requests.post(self.API_ENDPOINTS['pushes'],
                                 data=json.dumps(payload),
                                 headers=headers)
        return json.loads(response.content)