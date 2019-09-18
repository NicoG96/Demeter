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

This application serves to streamline the deployment process for projects hosted on GitHub. 
Demeter helps developers cherry-pick certain pull requests from issue tickets that are slated for release by automating the branch creation and then incorporating the commits from these pull requests into the branch.  In an ideal scenario, the pull requests that have already been merged into the development branch should all go into the next release, however, this is often not the case.  This is where Demeter comes into play -- it allows the developer to specify which resolved issue tickets they would like to include in the new release and effectively saves them the time spent time manually referencing each PR and cherry-picking chronologically.

<!-- INSTALLATION -->
## Installation

1.) Download the latest version of Demeter from the Releases tab

2.) Unzip the archive

3.) In a terminal, navigate to the unzipped directory and type:
`python3 setup.py install`

4.) Once installed, simply run the command: `python3 demeter/demeter.py`



<!-- REQUIREMENTS -->
## Requirements
1. Python 3.7.2+
2. GitHub access token
3. Structured pull request system that includes ticket number in title


<!-- USAGE EXAMPLES -->
## Usage

Usage is fairly straightforward. Upon starting the program, you will be prompted to enter the tickets you'd like to include in the next release.  (***Disclaimer***: Pull requests **MUST** include the ticket number somewhere in its title, otherwise the application will be unable to parse any pull request associated with these tickets).

<img src="https://i.imgur.com/wtlWi8p.png"></a>

From there, Demeter will then search for the associated pull request for these tickets among the last 50 closed pull requests.  If there was no match for a certain ticket, Demeter will notify the user and prompt them as to whether or not they would like to continue with the release.

<img src="https://i.imgur.com/66ic5vz.png"></a>

If all tickets were connected to 1+ pull requests or the user entered 'y' to the above, a report of the PRs is then displayed to the user so that they can QA its results.  If all looks well, the user can proceed to the final step.

<img src="https://i.imgur.com/kwf2MDA.png"></a>

Demeter will then prompt the user which branch should be the target for the pending release branch.  The user will enter a valid branch name and then the name of the release branch they are currently making.  Demeter will consequently create a new branch from the head of the specified base branch and begin cherry-picking the merge commits.

<img src="https://i.imgur.com/HuoyKEH.png"></a>

If all cherry-picks were successful, Demeter will output such in the log and then push the changes to the remote repository.  If everything completed without errors, you should then see your newly-created release branch on your repo!

<img src="https://i.imgur.com/3yjKZQI.png"></a>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

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