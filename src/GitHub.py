from termcolor import colored
from pyfiglet import Figlet
from github import Github
from pathlib import Path
from git import Repo
import configparser
import os.path
import logging
import github
import re


class GitHub:
    def __init__(self):
        self.local_repo = None
        self.github_repo = None
        self.fig = Figlet(font='slant')
        logging.getLogger().setLevel(logging.INFO)
    

    def cli(self):
        print(colored('============================================', 'cyan'))
        print(colored(self.fig.renderText('Demeter'), 'cyan'), end = '')
        print(colored('============================================', 'cyan'))

        connect_errors = None
        pull_requests = None

        tickets = self.get_tickets()

        if len(tickets) != 0:
            pull_requests, connect_errors = self.connect_pull_requests(self.get_pull_requests(), tickets)
        else:
            logging.error('No tickets were entered! Exiting...')
            return

        if len(pull_requests) != 0:
            if connect_errors:
                print(colored('There was an error connecting ' + str(connect_errors) +
                            ' ticket' +
                            ('s' if connect_errors > 1 else '') +
                            '. Would you still like to continue with deployment? [y/n]', 'yellow'))

                if input().lower() == 'n':
                    logging.info('Exiting...')
                    return
            pull_requests = self.sort_pulls(pull_requests)
        else:
            logging.error('Couldn\'t retrieve any associated pull requests. Exiting...')
            return

        print(colored('The following PRs will be cherry-picked into the next release:', 'yellow'))
        print(colored('===================================================================================================='
                    '==========', 'yellow'))
        for pr in pull_requests:
            print(str(pr.merged_at) + ' - ' + pr.title)
        print(colored('===================================================================================================='
                    '==========', 'yellow'))
        print(colored('Look good? [y/n]: ', 'yellow'), end='')

        if input().lower() == 'n':
            logging.info('Exiting...')
            exit(1)

        prev_release_sha = self.get_prev_release_sha()

        print(colored('Now please type the name of this release: ', 'yellow'), end='')
        release_name = input()

        self.build_release_branch(prev_release_sha, release_name)
        self.prepare_workspace(release_name)
        self.cherrypick(pull_requests, release_name)

        logging.info('Process completed successfully! Exiting Demeter.')


    def get_tickets(self):
        print("Enter tickets one-by-one to queue for release.\nType 'done' to conclude queuing:")
        tickets = []
        i = 1

        while True:
            ticket_number = input(str(i) + '.) ')
            i += 1

            if ticket_number == 'done':
                break
            else:
                try:
                    parsed_ticket_num = int(ticket_number)

                    if parsed_ticket_num not in tickets:
                        tickets.append(parsed_ticket_num)
                    else:
                        logging.warning('You\'ve already entered this ticket!')
                except ValueError:
                    logging.error('Invalid entry!\n')
        return tickets


    def get_pull_requests(self):
        logging.info('Fetching pull requests...')
        
        try:
            return self.github_repo.get_pulls(state = 'closed', sort = 'created', direction = 'desc')[:50]
        except Exception as ex:
            logging.error("Error fetching pull requests!")
            raise ex


    def connect_pull_requests(self, all_pulls, tickets):
        logging.info('Connecting ' + str(len(tickets)) +
                    ' issue' + ('s' if len(tickets) > 1 else '') +
                    ' to relevant pull requests...')

        connected_pulls = []
        errors = 0

        for ticket in tickets:
            match = False

            for pr in all_pulls:
                if re.search("^.*" + str(ticket) + "\D.*$", pr.title):
                    match = True
                    connected_pulls.append(pr)

            if match is False:
                errors += 1
                logging.error('Did not find a connected PR for ticket #' + str(ticket)
                            + '.\nDid the PR include the ticket # in the title?')

        logging.info('Connected ' + str(len(tickets) - errors) +
                    '/' + str(len(tickets)) +
                    ' issue' + ('s' if len(tickets)-errors > 1 else '') +
                    ' to ' + str(len(connected_pulls)) +
                    ' pull request' + ('s' if len(connected_pulls) > 1 or len(connected_pulls) == 0 else ''))
        return connected_pulls, errors


    def sort_pulls(self, pull_requests):
        return sorted(pull_requests, key=lambda x: x.merged_at, reverse=False)


    def get_prev_release_sha(self):
        print(colored('Please type the branch name to base this release off of: ', 'yellow'), end='')
        prev_release_sha = None
        done = False

        while not done:
            prev_release_name = input()
            try:
                prev_release_sha = self.github_repo.get_branch(branch=str(prev_release_name)).commit.sha
                logging.info('Previous release branch successfully indexed!')
                done = True

            except github.GithubException:
                logging.error('Branch not found. Try again?')

        return prev_release_sha


    def build_release_branch(self, prev_release_sha, release_name):
        logging.info('Building the new release branch...')

        try:
            self.github_repo.create_git_ref(ref = 'refs/heads/' + str(release_name), sha = prev_release_sha)
            logging.info('Successfully created new branch on the GitHub repository!')
        except github.GithubException as ex:
            logging.error('Couldn\'t create release branch!')
            raise ex


    def prepare_workspace(self, release_name):
        logging.info("Preparing workspace for cherry-picking...")
        try:
            logging.info('Stashing any uncommitted changes in repository...')
            self.local_repo.git.stash()

            logging.info('Checking out master branch...')
            self.local_repo.git.checkout('master')

            logging.info('Fetching any repo updates...')
            self.local_repo.git.pull()

            logging.info("Checking out branch: " + str(release_name) + '...')
            self.local_repo.git.checkout(str(release_name))
        except Exception as ex:
            logging.error("A problem occurred while preparing the workspace: ")
            raise ex
        

    def cherrypick(self, pull_requests, release_name):
        try:
            for pr in pull_requests:
                logging.info('Cherry-picking commit: ' + str(pr.merge_commit_sha))
                self.local_repo.git.cherry_pick('-m', '1', pr.merge_commit_sha)

            logging.info('Pushing changes to GitHub...')
            self.local_repo.git.push('origin', str(release_name))
        except Exception as ex:
            logging.error("Error occurred while cherry-picking commits!")
            raise ex


    def execute(self):
        config_path = os.path.join(Path.home(), ".demeter")
        config = configparser.ConfigParser()
        config.read(config_path)

        if not os.path.isfile(config_path) or 'GITHUB CREDENTIALS' not in config.sections():
            print(colored("Please enter your personal GitHub access token: ", "yellow"), end = '')
            GH_TOKEN = input()
            print(colored("Please enter the repository as it appears on in the Github URL e.g. {User}/{Repository}: ",
                        "yellow"), end = '')
            GH_REPO = input()
            print(colored("Please enter the directory path of the project on your machine e.g. /Users/{User}/Documents/"
                        "{Repo}: ", "yellow"), end = '')
            LOCAL_REPO = input()

            config['GITHUB CREDENTIALS'] = {
                'GH_TOKEN': GH_TOKEN,
                'GH_REPO': GH_REPO,
            }

            config['LOCAL REPO'] = {
                'GITHUB_REPO': LOCAL_REPO
            }

            with open(config_path, 'a+') as settings:
                config.write(settings)

        try:
            self.local_repo = Repo(config.get('LOCAL REPO', 'GITHUB_REPO'))
            self.github_repo = (Github(config.get('GITHUB CREDENTIALS', 'GH_TOKEN'))
                        .get_repo(config.get('GITHUB CREDENTIALS', 'GH_REPO')))
            self.cli()
        except Exception as ex:
            logging.error("Error initializing values from the configuration file. Please verify the entries are correct in ~/.demeter")
