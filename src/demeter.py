from termcolor import colored
from datetime import datetime
from pyfiglet import Figlet
from github import Github
import logging
import env
import re

fig = Figlet(font='slant')
git = Github(env.GITHUB_TOKEN)
repo = git.get_repo(env.GITHUB_REPO)
logging.getLogger().setLevel(logging.INFO)


def demeter_cli():
    print(colored('============================================', 'cyan'))
    print(colored(fig.renderText('Demeter'), 'cyan'), end = '')
    print(colored('============================================', 'cyan'))

    pull_requests = None
    connect_errors = None
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

            if input() == 'y':
                pull_requests = sort_pulls(pull_requests)
            else:
                logging.info('Exiting...')
                exit(1)
    else:
        logging.error('Couldn\'t retrieve any associated pull requests. Exiting...')
        exit(1)

    commits = get_merge_commits(pull_requests)

    if len(pull_requests) == len(commits):
        build_release_branch()


def get_tickets():
    print("Enter tickets one-by-one to queue for release.\nType 'end' to conclude queuing:\t")
    tickets = []
    i = 1

    while True:
        ticket_number = input(str(i) + '.) ')
        i += 1

        if ticket_number == 'end':
            break
        else:
            try:
                tickets.append(int(ticket_number))
            except ValueError:
                logging.error('Invalid entry!\n')

    return tickets


def get_pulls(tickets):
    logging.info('Connecting ' + str(len(tickets)) + ' issue' +
                 ('s' if len(tickets) > 1 else '') + ' to relevant pull requests...')
    all_pulls = repo.get_pulls(state = 'closed', sort = 'created', direction = 'desc')[:50]
    connected_pulls = []
    errors = 0

    for ticket in tickets:
        match = False

        for pr in all_pulls:
            if re.search("^.*" + str(ticket) + "\D.*$", pr.title):
                match = True
                connected_pulls.append(pr)
                break

        if match is False:
            errors += 1
            logging.error('Did not find a connected PR for ticket #' + str(ticket)
                          + '.\nDid the PR include the ticket # in the title?')

    logging.info('Connected ' + str(len(tickets) - errors) + ' issue' +
                 ('s' if len(tickets)-errors > 1 else '') +
                 ' to ' + str(len(connected_pulls)) +
                 ' pull request' + ('s' if len(connected_pulls) > 1 else ''))

    return connected_pulls, errors


def sort_pulls(pull_requests):
    return sorted(pull_requests, key=lambda x: x.merged_at, reverse=False)


def get_merge_commits(pull_requests):
    commits = []
    return commits


def build_release_branch():
    return True


if __name__ == "__main__":
    demeter_cli()
