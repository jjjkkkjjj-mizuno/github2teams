import os
from flask import Flask, request
import json
import requests
app = Flask(__name__)


WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)
if WEBHOOK_URL is None:
    raise ValueError('Couldn\'t load WEBHOOK_URL')

@app.route('/')
def index():
    return 'This web application allows us to connect between github and microsoft teams!!'

@app.route('/analyze_json', methods=['GET', 'POST'])
def get_json():
    # get POSTed json data
    headers = request.headers
    #print(headers['X-GitHub-Event'])
    contents = request.json
    #print(content)

    message = compose_message(headers, contents)

    # send json data to webhook's url
    response = requests.post(
        WEBHOOK_URL, data=json.dumps(message),
        headers={'Content-Type': 'application/json'}
    )

    # error handling
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


    return 'done\n'


def compose_message(headers, contents):
    event = headers['X-GitHub-Event']

    message = {'text': ''}

    if event == 'ping': # this event is occurred when the new webhook is established
        message['text'] = 'New webhook was established'

    elif event == 'gollum': # When Wiki page was updated or created
        message['text'] = 'Wiki page was updated'

    else:
        raise ValueError('Unknown event(: {}) was occurred'.format(event))

    return message


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)