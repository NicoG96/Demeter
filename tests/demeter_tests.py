from src import demeter
import unittest


def get_tickets_test():
    demeter.get_tickets()
    assert True


def get_pulls_test():
    demeter.get_pulls()
    assert True


def sort_pulls():
    demeter.sort_pulls()
    assert True


def get_merge_commits_tests():
    demeter.get_merge_commits()
    assert True


def build_release_branch_test():
    demeter.build_release_branch()
    assert True


if __name__ == '__main__':
    unittest.main()
