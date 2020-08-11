from datetime import timedelta, datetime

import jwt
import requests


def generate_app_token():
    payload = {
        # issued at time
        'iat': int(datetime.now().timestamp()),
        # JWT expiration time (10 minute maximum)
        'exp': int((datetime.now() + timedelta(minutes=10)).timestamp()),
        # GitHub App's identifier
        'iss': 73186
    }

    key = open('batchbuilder.private-key.pem').read()

    token = jwt.encode(payload, key, 'RS256')

    return token.decode()


def generate_installation_token(installation_id):
    app_token = generate_app_token()

    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers={
            'Accept': 'application/vnd.github.machine-man-preview+json',
            'Authorization': f'Bearer {app_token}'
        })

    return response.json()['token']


def read_config_file(repo):
    content = repo.get_contents('.batch.yml', 'refs/heads/master').decoded_content.decode()
    size = 8
    bisection = True
    stop_at = 4

    for line in content.split('\n'):
        if 'size:' in line:
            size = line.split(':')[1].strip()

        if 'bisection:' in line:
            bisection = line.split(':')[1].strip()

        if 'stop_at:' in line:
            stop_at = line.split(':')[1].strip()

    return {
        'size': size,
        'bisection': bisection,
        'stop_at': stop_at
    }


def get_batch_status(repo, token):
    url = f'https://api.github.com/repos/{repo.owner.login}/{repo.name}/commits/batch/check-runs'
    print(url)

    response = requests.get(
        url,
        headers={
            'Accept': 'application/vnd.github.antiope-preview+json',
            'Authorization': f'Bearer {token}'
        })

    print(response.json()['check_runs'][0]['conclusion'])


def set_master_status(repo, token):
    url = f'https://api.github.com/repos/{repo.owner.login}/{repo.name}/commits/b2df1bd35ce21bb07feabfde4eb91301c5cf5967/check-runs'
    print(url)

    response = requests.post(
        url,
        headers={
            'Accept': 'application/vnd.github.antiope-preview+json',
            'Authorization': f'Bearer {token}'
        })

    print(response.json()['check_runs'][0]['conclusion'])

    # return response.json()['token']
