from BitBucket import BitBucket as bb
from GitHub import GitHub as gh
import argparse
import logging


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--github", "-g", action="store_true")
    parser.add_argument("--bitbucket", "-b", action="store_true")
    parser.add_argument("--version", "-v", action="version", version="2.0.3")
    args = parser.parse_args()

    if args.github == True:
        gh().execute()
    elif args.bitbucket == True:
        bb().execute()
    else:
        logging.error("Please specify which service you are using by passing a --github/-g or --bitbucket/-b flag when invoking Demeter.")