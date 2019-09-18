from bitbucket.client import Client
from termcolor import colored
from pyfiglet import Figlet
from git import Repo, Git
import configparser
import os.path
import logging
import github
import re

fig = Figlet(font='slant')
logging.getLogger().setLevel(logging.INFO)


def demeter_cli():
    print(colored('============================================', 'cyan'))
    print(colored(fig.renderText('Demeter'), 'cyan'), end = '')
    print(colored('============================================', 'cyan'))

    connect_errors = None
    pull_requests = None

    tickets = get_tickets()

    if len(tickets) is not 0:
        pull_requests, connect_errors = get_pulls(tickets)
    else:
        logging.error('No tickets were entered! Exiting...')
        exit(1)

    if len(pull_requests) is not 0:
        if connect_errors:
            print(colored('There was an error connecting ' + str(connect_errors) +
                          ' ticket' +
                          ('s' if connect_errors > 1 else '') +
                          '. Would you still like to continue with deployment? [y/n]', 'yellow'))

            if input().lower() == 'y':
                pull_requests = sort_pulls(pull_requests)
            else:
                logging.info('Exiting...')
                exit(1)
        else:
            pull_requests = sort_pulls(pull_requests)
    else:
        logging.error('Couldn\'t retrieve any associated pull requests. Exiting...')
        exit(1)

    print(colored('The following PRs will be cherry-picked into the next release:', 'yellow'))
    print(colored('===================================================================================================='
                  '==========', 'yellow'))
    for pr in pull_requests:
        print(str(pr.merged_at) + ' - ' + pr.title)
    print(colored('===================================================================================================='
                  '==========', 'yellow'))
    print(colored('Look good? [y/n]', 'yellow'))

    if input().lower() == 'n':
        logging.info('Exiting...')
        exit(1)
    else:
        prev_release_sha = get_prev_release_sha()

        print(colored('Now please type the name of this release:\t', 'yellow'))
        release_name = input()

        build_release_branch(prev_release_sha, release_name)
        cherrypick(pull_requests, release_name)


def get_tickets():
    print("Enter tickets one-by-one to queue for release.\nType 'done' to conclude queuing:\t")
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


def get_pulls(tickets):
    logging.info('Connecting ' + str(len(tickets)) + ' issue' +
                 ('s' if len(tickets) > 1 else '') + ' to relevant pull requests...')
    # all_pulls = r.get_pulls(state = 'closed', sort = 'created', direction = 'desc')[:50]
    connected_pulls = []
    errors = 0

    for ticket in tickets:
        match = False

        # for pr in all_pulls:
        #     if re.search("^.*" + str(ticket) + "\D.*$", pr.title):
        #         match = True
        #         connected_pulls.append(pr)

        if match is False:
            errors += 1
            logging.error('Did not find a connected PR for ticket #' + str(ticket)
                          + '.\nDid the PR include the ticket # in the title?')

    logging.info('Connected ' + str(len(tickets) - errors) + '/' + str(len(tickets)) + ' issue' +
                 ('s' if len(tickets)-errors > 1 else '') +
                 ' to ' + str(len(connected_pulls)) +
                 ' pull request' + ('s' if len(connected_pulls) > 1 or len(connected_pulls) == 0 else ''))

    return connected_pulls, errors


def sort_pulls(pull_requests):
    return sorted(pull_requests, key=lambda x: x.merged_at, reverse=False)


def build_release_branch(prev_release_sha, release_name):
    logging.info('Building the new release branch...')

    try:
        # r.create_git_ref(ref = 'refs/heads/' + str(release_name), sha = prev_release_sha)
        logging.info('Successfully created new release branch!')
    except github.GithubException:
        logging.error('Couldn\'t create release branch! Exiting...')
        exit(1)


def get_prev_release_sha():
    print(colored('Please type the branch name to base this release off of:\t', 'yellow'))
    prev_release_sha = None
    done = False

    while not done:
        prev_release_name = input()
        try:
            # prev_release_sha = r.get_branch(branch=str(prev_release_name)).commit.sha
            logging.info('Previous release branch successfully indexed!')
            done = True

        except github.GithubException:
            logging.error('Branch not found. Try again?')

    return prev_release_sha


def cherrypick(pull_requests, release_name):
    # logging.info('Fetching repo updates...')
    # repo.git.fetch()
    # repo.git.pull()
    #
    # logging.info("Checking out branch: " + str(release_name) + '...')
    # repo.git.checkout(str(release_name))
    #
    # logging.info('Cherry-picking ' + str(len(pull_requests)) + ' commit' +
    #              ('s' if len(pull_requests) > 1 else '') + '...')
    #
    # for pr in pull_requests:
    #     repo.git.cherry_pick('-m', '1', pr.merge_commit_sha)
    #
    # logging.info('Pushing changes to origin...')
    # repo.git.push('origin', str(release_name))
    #
    # logging.info('Success! Exiting...')

    return True


if __name__ == "__main__":
    config = configparser.ConfigParser()

    if not os.path.isfile("../config.ini"):
        print(colored("Please enter your BitBucket email login:\t", "yellow"))
        BB_EMAIL = input()
        print(colored("Please enter your BitBucket password:\t", "yellow"))
        BB_PASSWORD = input()
        print(colored("Please enter the directory path of the project on your machine {e.g. C:\{User}\Documents\{Repo}:"
                      "\t", "yellow"))
        REPO_PATH = input()

        config['BITBUCKET CREDENTIALS'] = {
            'BB_EMAIL': BB_EMAIL,
            'BB_PASSWORD': BB_PASSWORD,
            'REPO_PATH': REPO_PATH
        }

        with open('../config.ini', 'w') as settings:
            config.write(settings)

    config.read('../config.ini')

    client = Client(config.get('BITBUCKET CREDENTIALS', 'BB_EMAIL'), config.get('BITBUCKET CREDENTIALS', 'BB_PASSWORD'))
    git = Git(config.get('BITBUCKET CREDENTIALS', 'REPO_PATH'))
    repo = Repo(config.get('BITBUCKET CREDENTIALS', 'REPO_PATH'))
