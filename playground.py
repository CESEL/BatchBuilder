from datetime import datetime
from time import sleep

from github import Github

from utils import generate_installation_token, get_batch_status

token = generate_installation_token(10584737)

g = Github(token)
repo = g.get_repo('beheshtraya/test-ci-tool')

# def add_new_file(i, repo):
#     repo.create_file(f'test{i}.py', f'adding file number {i}', f'print("{i}")')
#     sleep(0.5)


# for i in range(54, 55):
#     add_new_file(i, repo)


# get_batch_status(repo, token)


t1 = datetime.now()
repo.create_git_ref('refs/heads/batch8', 'c8dc54c1838a222b5510ec04a2d5651ce8682340')
t2 = datetime.now()

print(t2 - t1)

# from travispy import TravisPy
#
# t = TravisPy.github_auth(token)
# user = t.user()
