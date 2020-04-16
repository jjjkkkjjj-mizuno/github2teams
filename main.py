import os
from flask import Flask, request
import datetime
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
        date = date_converter(date)
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
        date = date_converter(date)

        sections = compose_sections(title, summary, Repository=repository, Title=event_title, Editor=editor, Date=date)

        url = contents['issue']['html_url']

    elif event == 'pull_request':
        title = 'Pull Request'
        summary = 'Pull Request was {}'.format(contents['action'])

        repository = contents['repository']['name']
        event_title = contents['pull_request']['title']
        editor = contents['sender']['login']
        date = contents['pull_request']['updated_at']
        date = date_converter(date)

        sections = compose_sections(title, summary, Repository=repository, Title=event_title, Editor=editor, Date=date)

        url = contents['pull_request']['html_url']

    elif event == 'push':
        title = 'Push'
        summary = 'New commits were pushed to {}'.format(contents['repository']['name'])

        repository = contents['repository']['name']
        editor = contents['sender']['login']
        date = contents['repository']['updated_at']
        date = date_converter(date)

        sections = compose_sections(title, summary, Repository=repository, Editor=editor, Date=date)

        url = contents['repository']['html_url']

    elif event == 'repository':
        title = 'Repository'
        summary = 'Repository was {}'.format(contents['action'])

        repository = contents['repository']['name']
        editor = contents['sender']['login']
        date = contents['repository']['updated_at']
        date = date_converter(date)

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

def date_converter(date):
    """
    Convert GMT to JST(+9)
    :param date: str, given date is GMT
    :return:
        jst_date: str, represented JST
    """
    # print(date)
    # 2020-04-16T04:23:59Z
    # split into date and time
    d, t = date.split('T')

    # get year, month, day, hour, minute, second
    d_ = d.split('-')
    t_ = t.split(':')
    y, mo, d, h, mi, s = int(d_[0]), int(d_[1]), int(d_[2]), int(t_[0]), int(t_[1]), int(t_[2][:-1])

    dateT = datetime.datetime(y, mo, d, h, mi, s)
    # plus 9 hours to convert to JST
    dateT += datetime.timedelta(hours=9)

    """
    >>> date = datetime.datetime(200,2,2,2,2,2)
    >>> date + datetime.timedelta(hours=26)
    datetime.datetime(200, 2, 3, 4, 2, 2)
    >>> '{:%H:%M:%S}'.format(date)
    '02:02:02'
    >>> '{:%Y:%M:%D}'.format(date)
    '0200:02:02/02/00'
    >>> '{:%Y:%M:%d}'.format(date)
    '0200:02:02'
    """

    jst_date = '{:%Y-%M-%d}T{:%H:%M:%S}Z'.format(dateT, dateT)

    return jst_date

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