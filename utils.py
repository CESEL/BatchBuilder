from datetime import timedelta, datetime
from time import sleep

import jwt
import requests

from django.conf import settings

from main_app.models import Build


def generate_app_token():
    payload = {
        # issued at time
        'iat': int(datetime.now().timestamp()),
        # JWT expiration time (10 minute maximum)
        'exp': int((datetime.now() + timedelta(minutes=10)).timestamp()),
        # GitHub App's identifier
        # 'iss': 73186
        'iss': settings.GITHUB_APP_ID
    }

    # key = open('batchbuilder.private-key.pem').read()
    key = open(settings.GITHUB_APP_PRIVATE_KEY_PATH).read()

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

    response = requests.get(
        url,
        headers={
            'Accept': 'application/vnd.github.antiope-preview+json',
            'Authorization': f'Bearer {token}'
        })

    if response.json()['check_runs'] and response.json()['check_runs'][0]['conclusion']:
        return response.json()['check_runs'][0]


def set_master_status(repo, token, check_run):
    url = f'https://api.github.com/repos/{repo.owner.login}/{repo.name}/check-runs'

    for build in Build.objects.filter(repo_id=repo.id):
        response = requests.post(
            url,
            json={
                'name': check_run['name'],
                'head_sha': build.head_commit,
                'details_url': check_run['details_url'],
                'external_id': check_run['external_id'],
                'status': check_run['status'],
                'started_at': check_run['started_at'],
                'conclusion': check_run['conclusion'],
                'completed_at': check_run['completed_at'],
                'output': check_run['output'],
            },
            headers={
                'Accept': 'application/vnd.github.antiope-preview+json',
                'Authorization': f'Bearer {token}'
            })

        if response.status_code == 201:
            build.delete()

        sleep(1)
