from github import Github
import env

git = Github(env.ACCESS_TOKEN)
repo = git.get_repo(env.REPO)
deploy_label = repo.get_label("Ready to Deploy")

ready_to_deploy = repo.get_issues(state='open', sort='created', direction='desc', labels=[deploy_label])
for ticket in ready_to_deploy:
    print(ticket)

