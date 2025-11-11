import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import tempfile
from secret_hunter.fetcher import _download_archive, _fetch_git, _find_license, fetch_source, _verify_checksum
from argparse import Namespace

class TestFetcher(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.test_dir, ".cache")
        os.makedirs(self.cache_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('requests.get')
    def test_download_archive_success(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'test data']
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        url = "https://example.com/test.zip"
        cache_path = os.path.join(self.cache_dir, "test.zip")
        _download_archive(url, cache_path, max_size_mb=1, timeout=10, expected_checksum=None)

        self.assertTrue(os.path.exists(cache_path))
        with open(cache_path, 'rb') as f:
            self.assertEqual(f.read(), b'test data')

    @patch('requests.get')
    def test_download_archive_too_large(self, mock_get):
        # Setup mock response for a large file
        mock_response = MagicMock()
        mock_response.headers = {'content-length': str(2 * 1024 * 1024)} # 2MB
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        url = "https://example.com/large.zip"
        cache_path = os.path.join(self.cache_dir, "large.zip")
        with self.assertRaises(ValueError):
            _download_archive(url, cache_path, max_size_mb=1, timeout=10, expected_checksum=None)

    @patch('git.Repo.clone_from')
    def test_fetch_git_success(self, mock_clone_from):
        url = "https://github.com/example/repo.git"
        _fetch_git(url, branch="main", tag=None, cache_dir=self.cache_dir)
        self.assertTrue(mock_clone_from.called)


    def test_find_license(self):
        license_content = "MIT License"
        with open(os.path.join(self.test_dir, "LICENSE"), "w") as f:
            f.write(license_content)

        found_license = _find_license(self.test_dir)
        self.assertEqual(found_license, license_content)

    def test_verify_checksum(self):
        file_path = os.path.join(self.test_dir, "test.txt")
        with open(file_path, "w") as f:
            f.write("test")
        
        # SHA256 of "test"
        expected_checksum = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        self.assertTrue(_verify_checksum(file_path, expected_checksum))
        self.assertFalse(_verify_checksum(file_path, "wrong_checksum"))


    @patch('secret_hunter.fetcher._fetch_git')
    @patch('secret_hunter.fetcher._find_license')
    @patch('secret_hunter.fetcher.confirm_license')
    def test_fetch_source_git_with_license(self, mock_confirm_license, mock_find_license, mock_fetch_git):
        # Setup mocks
        repo_path = os.path.join(self.cache_dir, "repo")
        mock_fetch_git.return_value = repo_path
        mock_find_license.return_value = "MIT License"

        args = Namespace(
            source_url="https://github.com/example/repo.git",
            source_type="git",
            branch="main",
            tag=None,
            cache_dir=self.cache_dir,
            verify_license=True,
            dry_run=False,
            verify_checksum=None,
            max_download_size=100,
            timeout=60
        )

        result_path = fetch_source(args)

        self.assertEqual(result_path, repo_path)
        mock_fetch_git.assert_called_once()
        mock_find_license.assert_called_once_with(repo_path)
        mock_confirm_license.assert_called_once_with("MIT License", force_confirmation=True)
        
    @patch('secret_hunter.fetcher._fetch_git')
    def test_fetch_source_dry_run(self, mock_fetch_git):
        args = Namespace(
            source_url="https://github.com/example/repo.git",
            source_type="git",
            dry_run=True,
            branch="main",
            tag=None,
            cache_dir=self.cache_dir
        )
        
        result_path = fetch_source(args)
        self.assertIsNone(result_path)
        mock_fetch_git.assert_not_called()


if __name__ == '__main__':
    unittest.main()
