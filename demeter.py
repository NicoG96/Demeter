from github import Github
import env

git = Github(env.ACCESS_TOKEN)
user = git.get_user()
repo = git.get_repo(env.REPO)

open_issues = repo.get_issues(state='open')
for issue in open_issues:
    print(issue)
