from BitBucket import BitBucket as bb
from GitHub import GitHub as gh
from termcolor import colored
import argparse
import requests
import semver
VERSION = "2.1.0"


def check_for_updates():
    releases = requests.get("https://api.github.com/repos/NicoG96/demeter/releases").json()
    releases = sorted(releases, key=lambda x: x["published_at"], reverse=True)
    formatted_version = str(releases[0]["tag_name"])[1:]

    if semver.compare(formatted_version, VERSION) == 1:
        print(colored(f"A new version of Demeter is available. Please consider upgrading to v{formatted_version}", "yellow"))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--github", "-g", action="store_true")
    parser.add_argument("--bitbucket", "-b", action="store_true")
    parser.add_argument("--version", "-v", action="version", version=VERSION)
    args = parser.parse_args()

    if args.github or args.bitbucket:
        check_for_updates()
        gh().execute() if args.github else bb().execute()
