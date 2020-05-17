from BitBucket import BitBucket as bb
from GitHub import GitHub as gh
import argparse
import logging


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", "-s", help="Specify \"github\" or \"bitbucket\"", required=True)
    parser.add_argument("--version", "-v", action="version", version="2.0.0")
    args = parser.parse_args()

    if args.service.lower() == "github":
        gh().execute()
    elif args.service.lower() == "bitbucket":
        bb().execute()
    else:
        logging.error("Unknown service. Please specify either github or bitbucket")