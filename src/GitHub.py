from termcolor import colored
from pyfiglet import Figlet
from github import Github
from pathlib import Path
from git import Repo
import configparser
import os.path
import github
import re


class GitHub:
    def __init__(self):
        self.local_repo = None
        self.github_repo = None
    

    def cli(self):
        print(colored("============================================", "cyan"))
        print(colored(Figlet(font="slant").renderText("Demeter"), "cyan") + "v2.1.0",)
        print(colored("============================================", "cyan"))

        ticket_mismatches = []
        indexed_pull_requests = None

        tickets = self.get_tickets()

        if len(tickets) != 0:
            pull_requests = self.get_pull_requests()
            indexed_pull_requests, ticket_mismatches = self.search_pull_requests(pull_requests, tickets)
        else:
            print(colored("No tickets found! Exiting...", "red"))
            return

        if len(ticket_mismatches) > 0:
            print(colored("There was an error connecting " + str(len(ticket_mismatches)) +
                        " ticket" +
                        ("s" if len(ticket_mismatches) > 1 else "") + ":", "red"))
            for ticket in ticket_mismatches:
                print(colored(f"  - #{ticket}", "red"))
            print(colored("Did the pull request include the ticket # in the title?", "red"))
            print(colored("Exiting...", "red"))
            return

        if len(indexed_pull_requests) == 0:
            return
        
        indexed_pull_requests = self.sort_pulls(indexed_pull_requests)
        print(colored("The following merge commits will be cherry-picked:", "green"))
        print(colored("===================================================================================================="
                    "==========", "green"))
        for pr in indexed_pull_requests:
            print(colored(str(pr.merged_at) + " - " + pr.title, "green"))
        print(colored("===================================================================================================="
                    "==========", "green"))
        print(colored("Look good? [y/n]: ", "green"), end="")

        if input().lower() == "n":
            print("Exiting...")
            return

        prev_release_sha = self.get_prev_release_sha()

        print(colored("Now please type the name of the new branch to create: ", "green"), end="")
        branch_name = input()

        self.create_git_branch(prev_release_sha, branch_name)
        
        print(colored("To cherry-pick the commits, please type \"y\": ", "green"), end="")
        if input().lower() == "y":
            self.prepare_workspace(branch_name)
            self.cherrypick(indexed_pull_requests)
        else:
            print("Exiting Demeter...")
            return

        print(colored("To push the changes to GitHub, please type \"y\": ", "green"), end="")
        if input().lower() == "y":
            self.push_to_github(branch_name)
            print("Process complete!")
        print("Exiting Demeter...")
        

    def get_tickets(self):
        print("Enter tickets one-by-one below.\nType \"done\" to conclude queuing:")
        tickets = []
        i = 1

        while True:
            ticket_number = input(str(i) + ".) ")
            i += 1

            if ticket_number == "done":
                break
            else:
                try:
                    parsed_ticket_num = int(ticket_number)

                    if parsed_ticket_num not in tickets:
                        tickets.append(parsed_ticket_num)
                    else:
                        print(colored("You\"ve already entered this ticket!"), "orange")
                except ValueError:
                    print(colored("Invalid entry!", "red"))
        return tickets


    def get_pull_requests(self):
        print("Fetching pull requests from GitHub...")
        
        try:
            return self.github_repo.get_pulls(state = "closed", sort = "created", direction = "desc")[:50]
        except Exception as ex:
            print(colored("Error fetching pull requests!", "red"))
            raise ex


    def search_pull_requests(self, pull_requests, tickets):
        indexed_pull_requests = []
        ticket_mismatches = []

        for ticket in tickets:
            match = False

            for pr in pull_requests:
                if re.search("^.*" + str(ticket) + "\D.*$", pr.title):
                    if pr.merged_at:
                        match = True
                        indexed_pull_requests.append(pr)
                    else:
                        print(colored(f"Warning: detected a pull request that was not merged into master: \"{pr.title}\"", "yellow"))

            if match is False:
                ticket_mismatches.append(ticket)   

        print("Connected " + str(len(tickets) - len(ticket_mismatches)) +
                    "/" + str(len(tickets)) +
                    " ticket(s)" +
                    " to " + str(len(indexed_pull_requests)) +
                    " pull request" + ("s" if len(indexed_pull_requests) > 1 or len(indexed_pull_requests) == 0 else ""))
        return indexed_pull_requests, ticket_mismatches


    def sort_pulls(self, pull_requests):
        return sorted(pull_requests, key=lambda x: x.merged_at, reverse=False)


    def get_prev_release_sha(self):
        print(colored("Please type the name of the target branch to checkout: ", "green"), end="")
        prev_release_sha = None
        done = False

        while not done:
            prev_release_name = input()
            try:
                prev_release_sha = self.github_repo.get_branch(branch=str(prev_release_name)).commit.sha
                print("Branch successfully indexed!")
                done = True

            except github.GithubException:
                print(colored("Branch not found. Try again?", "yellow"))
        return prev_release_sha


    def create_git_branch(self, prev_release_sha, release_name):
        print("Creating the branch...")

        try:
            self.github_repo.create_git_ref(ref = "refs/heads/" + str(release_name), sha = prev_release_sha)
            print("Branch successfully created on GitHub repo!")
        except github.GithubException as ex:
            print(colored("Couldn't create branch!", "red"))
            raise ex


    def prepare_workspace(self, branch_name):
        print("Preparing workspace for cherry-picking...")
        try:
            self.local_repo.git.stash()
            self.local_repo.git.checkout("master")
            self.local_repo.git.pull()
            self.local_repo.git.checkout(str(branch_name))
        except Exception as ex:
            print(colored("A problem occurred while preparing the workspace: ", "red"))
            raise ex
        

    def cherrypick(self, pull_requests):
        try:
            for pr in pull_requests:
                print("Cherry-picking commit: " + str(pr.merge_commit_sha))
                self.local_repo.git.cherry_pick("-m", "1", pr.merge_commit_sha)
        except Exception as ex:
            print(colored("Error occurred while cherry-picking commits: ", "red"))
            raise ex
        print("Cherry-picking complete.")


    def push_to_github(self, branch_name):
        try:
            print("Pushing changes to GitHub...")
            self.local_repo.git.push("origin", str(branch_name))
        except Exception as ex:
            print(colored("Error occurred while pushing changes: ", "red"))
            raise ex


    def execute(self):
        config_path = os.path.join(Path.home(), ".demeter")
        config = configparser.ConfigParser()
        config.read(config_path)

        if not os.path.isfile(config_path) or "GITHUB CREDENTIALS" not in config.sections():
            print(colored("Please enter your personal GitHub access token: ", "green"), end = "")
            GH_TOKEN = input()
            print(colored("Please enter the repository as it appears on in the Github URL e.g. {User}/{Repository}: ",
                        "green"), end = "")
            GH_REPO = input()
            print(colored("Please enter the directory path of the project on your machine e.g. /Users/{User}/Documents/"
                        "{Repo}: ", "green"), end = "")
            LOCAL_REPO = input()

            config["GITHUB CREDENTIALS"] = {
                "GH_TOKEN": GH_TOKEN,
                "GH_REPO": GH_REPO,
            }

            config["LOCAL REPO"] = {
                "GITHUB_REPO": LOCAL_REPO
            }

            with open(config_path, "a+") as settings:
                config.write(settings)

        try:
            self.local_repo = Repo(config.get("LOCAL REPO", "GITHUB_REPO"))
            self.github_repo = (Github(config.get("GITHUB CREDENTIALS", "GH_TOKEN"))
                        .get_repo(config.get("GITHUB CREDENTIALS", "GH_REPO")))
        except Exception as ex:
            print(colored("Error initializing values from the configuration file. Please verify the entries are correct in ~/.demeter", "red"))
            return
        
        self.cli()
