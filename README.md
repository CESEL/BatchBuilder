# BatchBuilder

A GitHub app to batch builds on Travis CI. 

Instead of testing every submitted change, 
this app enables teams to batch changes and run tests once for every batch.
If all builds are successful, the status of all commits in the batch is set to "success" on GitHub. 
Otherwise, bisection is performed until the failure(s) is isolated. 
In this case the status of each commit is set individually. 

## Getting started
1. Visit https://github.com/apps/batchbuilder and click "Configure"

2. Select desired repositories

3. Add a file named `.batch.yml` at the root of the project containing the following configuration
```    
- size: [integer number > 1]
- bisection: [true or false]
- stop_at: [integer number > 1 ]
```

4. Add the following configuration to `.travis.yml` file

```
branches:
  only:
  - batch
```

5. Start to write code, commit and push changes or merge a pull request into master branch.


__Note__: By default, only commits to master branch is going to be tested.



## Development
This repository contains the required files to run a Django application that waits for API calls from GitHub.
After each change on the master branch, an HTTP POST request is sent by GitHub to this app. 
A database keeps track of submitted changes for each project. When the batch is ready to test on Travis CI 
(is reached to required size), the changes are merged together and pushed to "batch" branch.
This branch is tested on Travis CI. 

### Workflow
- Extract installation ID of the project.
- Generate a JWT token and authenticate.
- Create "batch" branch if does not exist.
- Read `.batch.yml` file content.
- Store new changes in the database.
- Check if enough commits exists to be tested.
- Merge changes.
- Push into `batch` branch.
- Check Travis CI for test results.
- Set commits' status on GitHub using GitHub check API.


### Required GitHub Permissions
- metadata: read
- checks: read & write
- code: read & write
- commit statuses: read & write
- pull requests: read & write


### Run and Configure Django App
- Create a python virtual environment
- Install requirements
- `python manage.py migrate`
- `python manage.py runserver`
- Use a reverse proxy web server (Such as Nginx) or a tunnel  (Such as Ngrok) to expose localhost:8000
- Change API address on GitHub app settings page.
- Generate a private key on GitHub settings page and put it at the root of this repo. 
  Its name must be `batchbuilder.private-key.pem`
