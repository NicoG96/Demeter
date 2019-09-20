from termcolor import colored
from pyfiglet import Figlet
from git import Repo
import configparser
import requests
import os.path
import logging
import json
import re

fig = Figlet(font='slant')
logging.getLogger().setLevel(logging.INFO)


def demeter_cli():
    print(colored('============================================', 'cyan'))
    print(colored(fig.renderText('Demeter'), 'cyan'), end = '')
    print(colored('============================================', 'cyan'))

    connect_errors = None
    pull_requests = None

    issues = get_issues()

    if len(issues) is not 0:
        pull_requests, connect_errors = get_pulls(issues)
    else:
        logging.error('No issues were entered! Exiting...')
        exit(1)

    if len(pull_requests) is not 0:
        if connect_errors:
            print(colored('There was an error connecting ' + str(connect_errors) +
                          ' ticket' + ('s' if connect_errors > 1 else '') +
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
        print(str(pr['updated_on']) + ' - ' +
              str(pr['merge_commit']['hash']) + ' - ' +
              str(pr['title']))
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


def get_issues():
    print("Enter issue IDs one-by-one to queue for release.\nType 'done' to conclude queuing:\t")
    issues = []
    i = 1

    while True:
        issue_number = input(str(i) + '.) ')
        i += 1

        if issue_number == 'done':
            break
        else:
            try:
                parsed_ticket_num = int(issue_number)

                if parsed_ticket_num not in issues:
                    issues.append(parsed_ticket_num)
                else:
                    logging.warning('You\'ve already entered this ticket!')
            except ValueError:
                logging.error('Invalid entry!\n')
    return issues


def get_pulls(issues):
    all_pulls = []
    logging.info('Connecting ' + str(len(issues)) +
                 ' issue' + ('s' if len(issues) > 1 else '') +
                 ' to relevant pull requests...')

    url = 'https://api.bitbucket.org/2.0/repositories/{}/{}/pullrequests?state=MERGED'\
        .format(
            config.get("BITBUCKET CREDENTIALS", "BB_USER"),
            config.get("BITBUCKET CREDENTIALS", "BB_REPO"))

    try:
        response = (requests.get(url=url)).json()
        all_pulls = response.get('values')

    except json.decoder.JSONDecodeError:
        logging.error("Couldn't access BitBucket API - credentials error")
        exit(1)

    connected_pulls = []
    errors = 0

    for issue in issues:
        match = False

        for pr in all_pulls:
            if re.search("^.*" + str(issue) + "\D.*$", pr['title']):
                match = True
                connected_pulls.append(pr)

        if match is False:
            errors += 1
            logging.error('Did not find a connected PR for ticket #' + str(issue)
                          + '.\nDid the PR include the ticket # in the title?')

    logging.info('Connected ' + str(len(issues) - errors) +
                 '/' + str(len(issues)) +
                 ' issue' + ('s' if len(issues)-errors > 1 else '') +
                 ' to ' + str(len(connected_pulls)) +
                 ' pull request' + ('s' if len(connected_pulls) > 1 or len(connected_pulls) == 0 else ''))

    return connected_pulls, errors


def sort_pulls(pull_requests):
    return sorted(pull_requests, key=lambda x: x['updated_on'], reverse=False)


def build_release_branch(prev_release_sha, release_name):
    logging.info('Building the new release branch...')

    # r.create_git_ref(ref = 'refs/heads/' + str(release_name), sha = prev_release_sha)
    logging.info('Successfully created new release branch!')


def get_prev_release_sha():
    print(colored('Please type the branch name to base this release off of:\t', 'yellow'))
    prev_release_sha = None
    done = False

    while not done:
        url = 'https://api.bitbucket.org/2.0/repositories/testing21774/demtest/refs/branches/{}'.format(input())

        response = (requests.get(url = url)).json()

        if 'error' in response:
            logging.error('Branch not found. Try again?')
        else:
            logging.info('Previous release branch successfully indexed!')
            prev_release_sha = response['target']['hash']
            done = True

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
        print(colored("Please enter your BitBucket username:\t", "yellow"))
        BB_USER = input()
        print(colored("Please enter your BitBucket password:\t", "yellow"))
        BB_PASSWORD = input()
        print(colored("Please enter the name of the BitBucket repo:\t", "yellow"))
        BB_REPO = input()
        print(colored("Please enter the directory path of the project on your machine {e.g. C:\{User}\Documents\{Repo}:"
                      "\t", "yellow"))
        REPO_PATH = input()

        config['BITBUCKET CREDENTIALS'] = {
            'BB_USER': BB_USER,
            'BB_PASSWORD': BB_PASSWORD,
            'BB_REPO': BB_REPO
        }
        config['LOCAL REPOSITORY'] = {
            'REPO_PATH': REPO_PATH
        }

        with open('../config.ini', 'w') as settings:
            config.write(settings)

    config.read('../config.ini')

    repo = Repo(config.get('LOCAL REPOSITORY', 'REPO_PATH'))

    demeter_cli()
