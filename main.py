import os
from flask import Flask, request
import json
import pymsteams
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

    card = compose_message(headers, contents)

    # send card to webhook's url
    card.send()


    return 'done\n'
"""
 github doc = https://developer.github.com/webhooks/
 microcoft doc = https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using
 https://docs.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference#office-365-connector-card
 
 pymsteams doc = https://pypi.org/project/pymsteams/
"""


def compose_message(headers, contents):
    event = headers['X-GitHub-Event']

    if event == 'ping': # this event is occurred when the new webhook is established
        title = "New webhook"
        summary = 'New webhook was established'

        date = contents['hook']['updated_at']
        events_list = contents['hook']['events']
        editor = contents['sender']['login']

        sections = compose_sections(title, summary, Date=date, Events=events_list, Editor=editor)

        url = 'https://github.com/organizations/MIZUNO-CORPORATION/settings/hooks'

    elif event == 'gollum': # When Wiki page was updated or created
        title = 'Wiki'
        summary = 'Wiki page was updated'

        repository = contents['repository']['name']
        editor = contents['sender']['login']

        sections = compose_sections(title, summary, Repository=repository, Editor=editor)

        url = contents['pages'][0]['html_url']

    elif event == 'issues':
        title = 'Issue'
        summary = 'Issue was {}'.format(contents['action'])

        repository = contents['repository']['name']
        event_title = contents['issue']['title']
        editor = contents['sender']['login']
        date = contents['issue']['updated_at']

        sections = compose_sections(title, summary, Repository=repository, Title=event_title, Editor=editor, Date=date)

        url = contents['issue']['html_url']

    elif event == 'pull_request':
        title = 'Pull Request'
        summary = 'Pull Request was {}'.format(contents['action'])

        repository = contents['repository']['name']
        event_title = contents['pull_request']['title']
        editor = contents['sender']['login']
        date = contents['pull_request']['updated_at']

        sections = compose_sections(title, summary, Repository=repository, Title=event_title, Editor=editor, Date=date)

        url = contents['pull_request']['html_url']

    elif event == 'push':
        title = 'Push'
        summary = 'New commits were pushed to {}'.format(contents['repository']['name'])

        repository = contents['repository']['name']
        editor = contents['sender']['login']
        date = contents['repository']['updated_at']

        sections = compose_sections(title, summary, Repository=repository, Editor=editor, Date=date)

        url = contents['repository']['html_url']

    elif event == 'repository':
        title = 'Repository'
        summary = 'Repository was {}'.format(contents['action'])

        repository = contents['repository']['name']
        editor = contents['sender']['login']
        date = contents['repository']['updated_at']

        sections = compose_sections(title, summary, Repository=repository, Editor=editor, Date=date)

        url = contents['repository']['html_url']

    elif event == 'team':
        title = 'Team'
        summary = 'Team was {}'.format(contents['action'])

        name = contents['team']['name']
        editor = contents['sender']['login']

        sections = compose_sections(title, summary, Name=name, Editor=editor)

        url = contents['team']['html_url']

    elif event == 'team_add':
        title = 'Team added repository'
        summary = 'Team added repository'

        team_name = contents['team']['name']
        repository_name = contents['repository']['name']
        editor = contents['sender']['login']

        sections = compose_sections(title, summary, Team=team_name, Repository=repository_name, Editor=editor)

        url = contents['team']['html_url']

    else:
        raise ValueError('Unknown event(: {}) was occurred'.format(event))

    return compose_card(title, summary, sections, url)

def compose_sections(title, summary, **kwargs):
    sections = pymsteams.cardsection()

    sections.activityTitle(title)
    sections.activitySubtitle(summary)
    sections.activityImage('https://user-images.githubusercontent.com/63040751/79412387-53969200-7fe0-11ea-8e39-6da2e22bab6e.png')

    for key, value in kwargs.items():
        sections.addFact(key, value)

    return sections


def compose_card(title, summary, sections, url=None):
    card = pymsteams.connectorcard(WEBHOOK_URL)

    card.title(title)
    card.summary(summary)

    card.addSection(sections)

    if url is not None:
        card.addLinkButton("Check {}".format(title), url)

    return card

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)