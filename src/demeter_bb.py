from datetime import datetime, timedelta
from termcolor import colored
from pyfiglet import Figlet
from git import Repo
import configparser
import webbrowser
import requests
import os.path
import logging
import json
import re

fig = Figlet(font = 'slant')
logging.getLogger().setLevel(logging.INFO)


def demeter_cli():
    print(colored('============================================', 'cyan'))
    print(colored(fig.renderText('Demeter'), 'cyan'), end = '')
    print(colored('============================================', 'cyan'))

    connect_errors = None
    pull_requests = None

    issues = get_issues()

    if len(issues) is not 0:
        pull_requests, connect_errors = connect_pull_requests(get_pull_requests(), issues)

    else:
        logging.error('No issues were entered! Exiting...')
        exit(1)

    if len(pull_requests) is not 0:
        if connect_errors:
            print(colored('There was an error connecting ' + str(connect_errors) +
                          ' ticket' + ('s' if connect_errors > 1 else '') +
                          '. Would you still like to continue? [y/n]', 'yellow'))

            if input().lower() == 'n':
                logging.info('Exiting...')
                exit(1)
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
    print(colored('Look good? [y/n]: ', 'yellow'), end ='')

    if input().lower() == 'n':
        logging.info('Exiting...')
        exit(1)

    prev_branch = get_remote_branch()

    if prev_branch is None:
        logging.error("Couldn't fetch the specified branch!")
        exit(1)

    print(colored('Now please type the name of the new branch: ', 'yellow'), end='')
    new_branch = input()
    build_new_branch(prev_branch, new_branch)
    cherrypick(pull_requests, new_branch)
    logging.info('Process completed successfully! Exiting Demeter...')


def get_issues():
    print("Enter issue IDs one-by-one to queue for release.\nType 'done' to conclude queuing: ")
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


def get_pull_requests():
    all_pulls = []
    logging.info('Fetching pull requests...')

    url = 'https://api.bitbucket.org/2.0/repositories/{}/pullrequests?fields=values.title,values.updated_on,' \
          'values.merge_commit.hash&state=MERGED'.format(config.get("BITBUCKET CREDENTIALS", "BB_REPO"))

    header = {'Authorization': 'Bearer {}'.format(config.get("BITBUCKET CREDENTIALS", "BB_ACCESS_TOKEN"))}

    try:
        response = (requests.get(url = url, headers = header)).json()
        all_pulls = response.get('values')

    except json.decoder.JSONDecodeError:
        logging.error("Couldn't access BitBucket API - credentials error")
        exit(1)

    return all_pulls


def connect_pull_requests(all_pulls, issues):
    logging.info('Connecting ' + str(len(issues)) +
                 ' issue' + ('s' if len(issues) > 1 else '') +
                 ' to relevant pull requests...')
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
                 ' issue' + ('s' if len(issues) - errors > 1 else '') +
                 ' to ' + str(len(connected_pulls)) +
                 ' pull request' + ('s' if len(connected_pulls) > 1 or len(connected_pulls) == 0 else ''))

    return connected_pulls, errors


def sort_pulls(pull_requests):
    return sorted(pull_requests, key = lambda x: x['updated_on'], reverse = False)


def get_remote_branch():
    print(colored('Please type the branch name to base this release off of: ', 'yellow'), end='')
    done = False

    while not done:
        branch_name = input()

        url = 'https://api.bitbucket.org/2.0/repositories/{}/refs/branches/{}' \
            .format(config.get('BITBUCKET CREDENTIALS', 'BB_REPO'), branch_name)

        header = {'Authorization': 'Bearer {}'.format(config.get("BITBUCKET CREDENTIALS", "BB_ACCESS_TOKEN"))}

        response = (requests.get(url=url, headers=header)).json()

        if 'error' in response:
            logging.error('Branch not found. Try again?')
        else:
            logging.info('Previous release branch successfully indexed!')
            return branch_name

    return None


def build_new_branch(prev_branch, new_branch):
    repo.git.checkout(prev_branch)
    logging.info('Fetching any repo updates...')
    repo.git.pull()

    logging.info('Building the new branch...')
    repo.git.checkout('-b', new_branch)

    logging.info('Successfully created new branch!')


def cherrypick(pull_requests, new_branch):
    logging.info('Cherry-picking ' + str(len(pull_requests)) + ' commit' +
                 ('s' if len(pull_requests) > 1 else '') + '...')

    for pr in pull_requests:
        repo.git.cherry_pick('-m', '1', pr['merge_commit']['hash'])

    logging.info('Pushing changes to origin...')
    repo.git.push('--set-upstream', 'origin', str(new_branch))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not os.path.isfile("config.ini") or 'BITBUCKET CREDENTIALS' not in config.sections():
        # get user credentials
        print(colored("Please enter your OAuth2 consumer key: ", "yellow"), end = '')
        BB_KEY = input()

        print(colored("Please enter your OAuth2 consumer secret: ", "yellow"), end = '')
        BB_SECRET = input()

        print(colored("Please enter the name of the repo as it appears in the BitBucket URL (e.g. {user}/{repo}): ",
                      "yellow"), end = '')
        BB_REPO = input()

        print(colored("Please enter the directory path of the project on your machine (e.g. /Users/{User}/Documents"
                      "/{Repo}): ", "yellow"), end = '')
        LOCAL_REPO = input()

        # fetch authentication code
        print(colored("Opening web browser... please copy the code from the URL and paste it here: ", "yellow"),
              end = '')

        webbrowser.open("https://bitbucket.org/site/oauth2/authorize?client_id=" + BB_KEY + "&response_type=code")
        BB_AUTH_CODE = input()

        # fetch access and refresh tokens
        data = {
            'grant_type': 'authorization_code',
            'code': BB_AUTH_CODE
        }

        API_keys = requests.post('https://bitbucket.org/site/oauth2/access_token',
                                 data = data,
                                 auth = (BB_KEY, BB_SECRET)).json()

        BB_ACCESS_TOKEN = API_keys['access_token']
        BB_REFRESH_TOKEN = API_keys['refresh_token']

        # write all data to config file
        config['BITBUCKET CREDENTIALS'] = {
            'BB_KEY': BB_KEY,
            'BB_SECRET': BB_SECRET,
            'BB_ACCESS_TOKEN': BB_ACCESS_TOKEN,
            'BB_REFRESH_TOKEN': BB_REFRESH_TOKEN,
            'BB_REPO': BB_REPO,
        }

        config['LOCAL REPO'] = {
            'LOCAL_REPO': LOCAL_REPO
        }

        config['METADATA'] = {
            'Last_Updated': str(datetime.now())
        }

        with open('config.ini', 'w+') as settings:
            config.write(settings)

    # check if the access token has expired
    if datetime.now() - datetime.strptime(config.get('METADATA', 'Last_Updated'), '%Y-%m-%d %H:%M:%S.%f') >= timedelta(hours=2):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': config.get('BITBUCKET CREDENTIALS', 'BB_REFRESH_TOKEN')
        }

        updated_keys = requests.post('https://bitbucket.org/site/oauth2/access_token',
                                     data = data,
                                     auth = (config.get('BITBUCKET CREDENTIALS', 'BB_KEY'),
                                             config.get('BITBUCKET CREDENTIALS', 'BB_SECRET'))).json()
        BB_ACCESS_TOKEN = updated_keys['access_token']
        BB_REFRESH_TOKEN = updated_keys['refresh_token']

        # update the keys in the config file
        config.set('BITBUCKET CREDENTIALS', 'BB_ACCESS_TOKEN', BB_ACCESS_TOKEN)
        config.set('BITBUCKET CREDENTIALS', 'BB_REFRESH_TOKEN', BB_REFRESH_TOKEN)
        config.set('METADATA', 'Last_Updated', str(datetime.now()))

        with open('config.ini', 'w+') as settings:
            config.write(settings)

    repo = Repo(config.get('LOCAL REPO', 'LOCAL_REPO'))

    demeter_cli()
