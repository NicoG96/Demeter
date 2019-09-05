from termcolor import colored
from pyfiglet import Figlet
from github import Github
import logging
import env
import re

git = Github(env.GITHUB_TOKEN)
repo = git.get_repo(env.GITHUB_REPO)
fig = Figlet(font='slant')


def demeter_cli():
    print(colored('============================================', 'cyan'))
    print(colored(fig.renderText('Demeter'), 'cyan'), end = '')
    print(colored('============================================', 'cyan'))

    pull_requests = None
    tickets = get_tickets()

    if len(tickets) is not 0:
        pull_requests = get_pulls(tickets)
    else:
        logging.error('No tickets were entered! Exiting...')
        exit(1)

    if len(pull_requests) is not 0:
        sort_pulls(pull_requests)
    else:
        logging.error('Couldn\'t retrieve associated pull requests. Exiting...')
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
    logging.info('Connecting ' + str(len(tickets)) + ' issues to relevant pull requests...')
    all_pulls = repo.get_pulls(state = 'closed', sort = 'created', direction = 'desc')[:50]
    connected_pulls = []

    for ticket in tickets:
        match = False

        for pr in all_pulls:
            if re.search("^.*" + str(ticket) + "\D.*$", pr.title):
                match = True
                connected_pulls.append(pr)
                break

        if match is False:
            logging.error('Did not find any connected PR to ticket #' + str(ticket)
                          + '.\nDid the PR include the ticket # in the title?')

    return connected_pulls


def sort_pulls(pull_requests):
    return pull_requests


def get_merge_commits(pull_requests):
    commits = []
    return commits


def build_release_branch():
    return True


if __name__ == "__main__":
    demeter_cli()
