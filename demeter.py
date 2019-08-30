from github import Github
import env

user = Github(env.ACCESS_TOKEN)

for repo in user.get_user().get_repos():
    print(repo.name)
