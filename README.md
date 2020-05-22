<br />

  <h1 align="center">Demeter</h1>

  <p align="center">
    🍒 Automate the cherry-picking stuff with Python 🍒
  </p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Installation](#installation)
* [Requirements](#requirements)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

<!-- ABOUT THE PROJECT -->
## About the Project

This application serves to streamline the deployment process for projects hosted on GitHub and BitBucket.

Demeter helps developers cherry-pick certain pull requests from issue tickets that are slated for release by automating the branch creation and then incorporating the commits from these pull requests into the branch.  

In an ideal scenario, the pull requests that have already been merged into the development branch should all go into the next release, however, this is often not the case.  This is where Demeter comes into play -- it allows the developer to specify which resolved issue tickets they would like to include in the new release and effectively saves them the time spent time manually referencing each PR and cherry-picking chronologically.

<!-- INSTALLATION -->
## Installation

1.) Download the latest version of Demeter from the Releases tab

2.) Unzip the archive

3.) Setup a python virtual environment

4.) Activate the virtual environment

5.) Install the project dependencies by running `pip install -r requirements.txt`

6.) Once installed, invoke Demeter by typing `python3 Demeter.py [service]` where `service` denotes either GitHub (`--github` or `-g`) or BitBucket (`--bitbucket` or `-b`)

<!-- REQUIREMENTS -->
## Requirements

1. Python 3+
2. GitHub access token and/or BitBucket consumer keys
3. **Structured pull request system that includes ticket number in title**

<!-- USAGE EXAMPLES -->
## Usage

Usage is fairly straightforward. If you are running Demeter for the first time, you will be prompted for GitHub/BitBucket credentials that will only need to be entered once to setup the configuration file. **Note**: You will need to create a personal access token for Demeter to use prior to running the application (GitHub profile -> Settings -> Developer Settings -> Personal Access Tokens) or (BitBucket profile -> All workspaces -> Click 'Manage' on desired repository -> OAuth consumers -> Add consumer).

<img src="https://i.imgur.com/j6HQeLW.png"></a>

Once configured, you will then be prompted to enter the tickets you'd like to include in the next release.  (***Disclaimer***: Pull requests **MUST** include the ticket number somewhere in its title, otherwise the application will be unable to parse any pull request associated with these tickets).

<img src="https://i.imgur.com/JAFv4mU.png"></a>

From there, Demeter will then search for the associated pull request for these tickets among the last 50 closed pull requests.  It will display the connected tickets in a chronological list and prompt for your approval.

<img src="https://i.imgur.com/XPOt7ZB.png"></a>

If the user approves of the report, Demeter will then prompt the user which branch should be the target for the pending release branch.  The user will enter a valid branch name and then the name of the release branch they are currently making.  Demeter will create a new branch from the head of the specified base branch and begin cherry-picking the merge commits.

<img src="https://i.imgur.com/3XLHBGc.png"></a>

If all cherry-picks were successful, Demeter will output such in the log and then push the changes to the remote repository.  If everything completed without errors, you should then see your newly-created release branch on your repo!

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Nico Gonzalez - NicoG96@gmail.com
