from termcolor import colored
from pyfiglet import Figlet
from github import Github
import logging
import github
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

    connect_errors = None
    pull_requests = None
    commits = None

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
            pull_requests = sort_pulls(pull_requests)
    else:
        logging.error('Couldn\'t retrieve any associated pull requests. Exiting...')
        exit(1)

    print(colored('The following PRs will be cherry-picked into the next release:', 'yellow'))
    for pr in pull_requests:
        print(pr.title + ' - ' + pr.merged_at)
    print(colored('Look good? [y/n]', 'yellow'))

    if input() == 'n':
        logging.info('Exiting...')
        exit(1)
    else:
        build_release_branch()

    cherrypick(pull_requests)


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


def build_release_branch():
    prev_release_sha = get_prev_release_sha()

    print(colored('Now please type the version number of this release:\t', 'yellow'))
    curr_release_version = input()

    logging.info('Building the new release branch...')

    try:
        repo.create_git_ref(ref = 'refs/heads/releases/v' + curr_release_version, sha = prev_release_sha)
        logging.info('Successfully created new release branch!')
    except github.GithubException:
        logging.error('Couldn\'t create release branch! Exiting...')
        exit(1)


def get_prev_release_sha():
    print(colored('Please type the last release version (e.g. 1.45.0):\t', 'yellow'))
    prev_release_sha = None
    done = False

    while not done:
        prev_release_version = input()
        try:
            prev_release_sha = repo.get_branch(branch="releases/v" + prev_release_version).commit.sha
            logging.info('Previous release branch successfully indexed!')
            done = True

        except github.GithubException:
            logging.error('Branch not found. Try again?')

    return prev_release_sha


def cherrypick(pull_requests):
    logging.info('Cherry-picking ' + str(len(pull_requests)) + ' commits...')

    return True


if __name__ == "__main__":
    demeter_cli()
