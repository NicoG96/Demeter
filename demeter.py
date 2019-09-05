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

    tickets = get_tickets()
    pulls = get_pulls(tickets)

    # build_release_branch()


def get_tickets():
    tickets = []
    done = False

    ticket_number = input("Enter a ticket to queue for release, type 'end' to conclude queuing:\t")

    # while not done:
    #     if user_input() == 'end':
    #         done = True
    #     else:
    #         tickets.append(user_input())
    return tickets


def get_pulls(tickets):
    logging.info('Connecting issues to relevant pull requests ...')
    all_pulls = repo.get_pulls(state = 'closed', sort = 'created', direction = 'desc')[:50]
    connected_pulls = []

    for ticket in tickets:
        match = False

        for pr in all_pulls:
            if re.search("^#?\s?" + ticket + ".*", pr.title):
                match = True
                connected_pulls.append(pr)
                break

        if match is False:
            logging.error('Did not find any connected PR to ticket #' + ticket)
            logging.warning('Did the PR include the ticket # in the title?')

    return connected_pulls


def build_release_branch():
    return True


if __name__ == "__main__":
    demeter_cli()
