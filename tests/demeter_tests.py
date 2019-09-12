from github import Github
from src import demeter
import unittest
import env


class DemeterTests(unittest.TestCase):
    git = Github(env.GITHUB_TOKEN)
    repo = git.get_repo(env.GITHUB_REPO)

    def test_get_pulls(self):
        connected_pulls = []

        tickets = [
            1049,
            1262,
            1050,
            1296,
            1302,
            1288,
            1263
        ]

        for ticket in tickets:
            connected_pulls.append(self.repo.get_pull(ticket))

        self.assertEqual(connected_pulls, demeter.get_pulls(tickets))

    def test_sort_pulls(self):
        ordered_pulls = []

        tickets_ordered = [
            1262,
            1265,
            1266,
            1263,
            1272
        ]

        tickets_unordered = [
            1272,
            1265,
            1262,
            1266,
            1263
        ]

        for ticket in tickets_ordered:
            ordered_pulls.append(self.repo.get_pull(ticket))

        self.assertEqual(ordered_pulls, demeter.sort_pulls(tickets_unordered))


if __name__ == '__main__':
    unittest.main()
