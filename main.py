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
            'Request to teams returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


    return 'done\n'
"""
 github doc = https://developer.github.com/webhooks/
 microcoft doc = https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using
 https://docs.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference#office-365-connector-card
 
 The @type and @context are to tell Microsoft Teams what kind of message is coming in and what schema to use to decode and post the message.
 
 Unfortunately, image was not shown...
"""
"""
message_template = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "John Doe commented on Trello",
    "title": "Project Tango",
    "sections": [
        {
            "activityTitle": "John Doe commented",
            "activitySubtitle": "On Project Tango",
            "activityText": "\"Here are the designs\"",
            "activityImage": "http://connectorsdemo.azurewebsites.net/images/MSC12_Oscar_002.jpg"
        },
        {
            "title": "Details",
            "facts": [
                {
                    "name": "Labels",
                    "value": "Designs, redlines"
                },
                {
                    "name": "Due date",
                    "value": "Dec 7, 2016"
                },
                {
                    "name": "Attachments",
                    "value": "[final.jpg](http://connectorsdemo.azurewebsites.net/images/WIN14_Jan_04.jpg)"
                }
            ]
        },
        {
            "title": "Images",
            "images": [
                {
                    "image":"http://connectorsdemo.azurewebsites.net/images/MicrosoftSurface_024_Cafe_OH-06315_VS_R1c.jpg"
                },
                {
                    "image":"http://connectorsdemo.azurewebsites.net/images/WIN12_Scene_01.jpg"
                },
                {
                    "image":"http://connectorsdemo.azurewebsites.net/images/WIN12_Anthony_02.jpg"
                }
            ]
        }
    ],
    "potentialAction": [
        {
            "@context": "http://schema.org",
            "@type": "ViewAction",
            "name": "View in Trello",
            "target": [
                "https://trello.com/c/1101/"
            ]
        }
    ]
  }
"""


def compose_message(headers, contents):
    event = headers['X-GitHub-Event']

    title = "None"
    summary = "None"
    sections = [
        {
            "title": "Details",
            "facts": [
                {
                    "name": "Labels",
                    "value": "Designs, redlines"
                },
                {
                    "name": "Due date",
                    "value": "Dec 7, 2016"
                },
                {
                    "name": "Attachments",
                    "value": "[final.jpg](http://connectorsdemo.azurewebsites.net/images/WIN14_Jan_04.jpg)" # markdown is available
                }
            ]
        }
    ]
    url = 'https://github.com/MIZUNO-CORPORATION'

    if event == 'ping': # this event is occurred when the new webhook is established
        title = "New webhook"
        summary = 'New webhook was established'

        date = contents['hook']['updated_at']
        events_list = contents['hook']['events']
        editor = contents['sender']['login']

        sections = compose_sections(Date=date, Events=events_list, Editor=editor)

        url = 'https://github.com/organizations/MIZUNO-CORPORATION/settings/hooks'

    elif event == 'gollum': # When Wiki page was updated or created
        title = 'Wiki'
        summary = 'Wiki page was updated'

        repository = contents['repository']['name']
        editor = contents['sender']['login']

        sections = compose_sections(Repository=repository, Editor=editor)

        url = contents['pages'][0]['html_url']

    elif event == 'issues':
        title = 'Issue'
        summary = 'Issue was {}'.format(contents['action'])

        repository = contents['repository']['name']
        event_title = contents['issue']['title']
        editor = contents['sender']['login']
        date = contents['issue']['updated_at']

        sections = compose_sections(Repository=repository, Title=event_title, Editor=editor, Date=date)

        url = contents['issue']['html_url']

    elif event == 'pull_request':
        title = 'Pull Request'
        summary = 'Pull Request was {}'.format(contents['action'])

        repository = contents['repository']['name']
        event_title = contents['pull_request']['title']
        editor = contents['sender']['login']
        date = contents['pull_request']['updated_at']

        sections = compose_sections(Repository=repository, Title=event_title, Editor=editor, Date=date)

        url = contents['pull_request']['html_url']

    elif event == 'push':
        title = 'Push'
        summary = 'New commits were pushed to {}'.format(contents['repository']['name'])

        repository = contents['repository']['name']
        editor = contents['sender']['login']
        date = contents['repository']['updated_at']

        sections = compose_sections(Repository=repository, Editor=editor, Date=date)

        url = contents['push']['html_url']

    elif event == 'repository':
        title = 'Repository'
        summary = 'Repository was {}'.format(contents['action'])

        repository = contents['repository']['name']
        editor = contents['sender']['login']
        date = contents['repository']['updated_at']

        sections = compose_sections(Repository=repository, Editor=editor, Date=date)

        url = contents['repository']['html_url']

    elif event == 'team':
        title = 'Team'
        summary = 'Team was {}'.format(contents['action'])

        name = contents['team']['name']
        editor = contents['sender']['login']

        sections = compose_sections(Name=name, Editor=editor)

        url = contents['team']['html_url']

    elif event == 'team_add':
        title = 'Team added repository'
        summary = 'Team added repository'

        team_name = contents['team']['name']
        repository_name = contents['repository']['name']
        editor = contents['sender']['login']

        sections = compose_sections(Team=team_name, Repository=repository_name, Editor=editor)

        url = contents['team']['html_url']

    else:
        raise ValueError('Unknown event(: {}) was occurred'.format(event))

    return get_template_json(title, summary, sections, url)

def compose_sections(**kwargs):
    sections = []
    for key, value in kwargs.items():
        sections += [{
            "name": key,
            "value": value
        }]

    return [
        {
            "title": "Details",
            "facts": [
                sections
            ]
        }
    ]


def get_template_json(title, summary, sections, url=None):

    message_template = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": summary,
        "title": title,
        "sections": sections,
        "potentialAction": [
            {
                "@context": "http://schema.org",
                "@type": "ViewAction",
                "name": "Go {}".format(title),
                "target": [
                    url
                ]
            }
        ]
    }

    if url is not None:
        message_template['potentialAction'] = [
            {
                "@context": "http://schema.org",
                "@type": "ViewAction",
                "name": "Go {}".format(title),
                "target": [
                    url
                ]
            }
        ]

    return message_template

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)