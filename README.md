# Github2Teams

Connection from GitHub to Microsoft Teams using webhooks and heroku

## Requirements

See requirements.txt

- Export requirements.txt

  ```bash
  pip freeze > requirements.txt
  ```

  

## Test

Use ngrok.

- ~~Set temporary Environment path~~

  ```bash
  export FLASK_APP=main.py
  export FLASK_DEBUG=1
  ```

  

- Set Deployed Environment path

  ```bash
  export WEBHOOK_URL='https://~~~'
  ```

- Get local's global address by ngrok

  ```bash
  ngrok http {port number}
  ```

  e.g.) Output is below (`port number`=8000)

  ```bash
  Session Status                online                                     
  Session Expires               7 hours, 59 minutes                                                   
  Web Interface                 http://~:4040                             
  Forwarding                    http://~.ngrok.io -> http://localhost:8000 
  Forwarding                    https://~.ngrok.io -> http://localhost:8000
  ```

- Set `https://~.ngrok.io`**/analyze_json**` using above url to payload url in Github

  ![github_webhook](https://user-images.githubusercontent.com/63040751/79216816-c5f45e80-7e88-11ea-8cda-d1fd61b6d55b.PNG)

## Deploy

Deploy to Heroku

### Initial Settings

- Connect Heroku to Github

  Go Heroku Personal Account site > github2teams > Deploy 

  Click Github icon

  ![heroku_connect_github](https://user-images.githubusercontent.com/63040751/79216820-c856b880-7e88-11ea-8912-1a1a0b3580c4.PNG)

- Choose your github's repository, and then set "Enable Automatic Deploys"

  ![heroku_deploy](https://user-images.githubusercontent.com/63040751/79216823-ca207c00-7e88-11ea-99e7-c4e43a2f99d7.PNG)

- Set Environment Path

  Go Heroku Personal Account site > github2teams > Settings > Config Vars

  Click "Reveal vars", and set specific path's information.

  Note that environment path can be set by Heroku CLI too.

  ![heroku_config](https://user-images.githubusercontent.com/63040751/79216817-c7be2200-7e88-11ea-834d-7ed46d27efcb.png)

  ```
  KEY=WEBHOOK_URL ,VALUE=https://~~~~
  ```


- Set heroku's url to payload url in github

  ```bash
  https://{your app name}.herokuapp.com/analyze_json
  ```

  ![github_webhook](https://user-images.githubusercontent.com/63040751/79216816-c5f45e80-7e88-11ea-8cda-d1fd61b6d55b.PNG)

### Deploy

You should commit registered repository only!!

```bash
git add -A
git commit -m "aaaaa"
git push
```

