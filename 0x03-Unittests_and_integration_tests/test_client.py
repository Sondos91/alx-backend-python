#!/usr/bin/env python3
"""
A github org client
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient
from parameterized import parameterized_class
import fixtures


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google", {"login": "google", "id": 1}),
        ("microsoft", {"login": "microsoft", "id": 2}),
    ])
    def test_org(self, org_name, expected):
        """
        Test that the org method
        returns the correct organization data.
        """
        with patch.object(
                GithubOrgClient,
                'org',
                new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = expected
            client = GithubOrgClient(org_name)
            self.assertEqual(client.org, expected)

    def test_public_repos_url(self):
        """
        Test that the _public_repos_url property returns the correct URL.
        """
        org_name = "test_org"
        expected_url = "https://api.github.com/orgs/test_org/repos"
        with patch.object(
                GithubOrgClient,
                'org',
                new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": expected_url}
            client = GithubOrgClient(org_name)
            self.assertEqual(client._public_repos_url, expected_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test that public_repos returns the correct list of repository names,
        and that get_json and _public_repos_url are called as expected.
        """
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = test_payload
        test_url = "http://test_url"
        org_name = "test_org"
        with patch.object(
                GithubOrgClient,
                '_public_repos_url',
                new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = test_url
            client = GithubOrgClient(org_name)
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test that has_license correctly identifies repositories
        with a specific license.
        """
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": fixtures.TEST_PAYLOAD[0][0],
        "repos_payload": fixtures.TEST_PAYLOAD[0][1],
        "expected_repos": fixtures.TEST_PAYLOAD[0][2],
        "apache2_repos": fixtures.TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for the GithubOrgClient class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment by patching requests.get.
        """
        cls.get_patcher = patch('requests.get')
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            class MockResponse:
                def __init__(self, payload):
                    self._payload = payload

                def json(self):
                    return self._payload

            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                return MockResponse(cls.repos_payload)
            return MockResponse(None)

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Stop patching requests.get.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test public_repos returns expected repo names from fixtures.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test public_repos returns expected repo names
        filtered by license 'apache-2.0'.
        """
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()