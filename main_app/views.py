from threading import Thread
from time import sleep

from django.http import HttpResponse
from django.shortcuts import render
from github import Github
from github.GithubException import GithubException
from rest_framework import permissions
from rest_framework.views import APIView

from main_app.models import Build
from utils import generate_installation_token, read_config_file, get_batch_status


def home(request):
    return HttpResponse('Home Page')


def check_batch_status(repo, token):
    while True:
        status = get_batch_status(repo, token)

        if not status:
            break

        sleep(5)


class GithubView(APIView):
    throttle_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        print(request.data)

        head_commit = request.data['head_commit']['id']

        if not head_commit:
            return HttpResponse(status=204)

        # authenticate
        installation_id = request.data['installation']['id']
        token = generate_installation_token(installation_id)
        g = Github(token)

        # get repo
        repo_id = request.data['repository']['id']
        repo = g.get_repo(repo_id)

        # check if branch "batch" exists
        try:
            repo.get_branch('batch')
        except GithubException:
            before_head = request.data['before']
            repo.create_git_ref('refs/heads/batch', before_head)

        # read .batch.yml content
        config = read_config_file(repo)

        # save new changes in Build table
        Build.objects.create(repo_id=repo_id, head_commit=head_commit)

        # check queue
        build_list = Build.objects.filter(repo_id=repo_id, is_merged=False)

        # merge if batch is filled
        if build_list.count() >= int(config['size']):
            repo.merge('batch', 'master')

            for build in build_list:
                build.is_merged = True
                build.save()

        # checking Travis build status in a separated thread
        t = Thread(target=check_batch_status, args=(repo, token))
        t.start()

        # update status


        return HttpResponse(request.data)
