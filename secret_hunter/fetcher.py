import os
import git
import requests
import tarfile
import zipfile
import hashlib
from tqdm import tqdm
from urllib.parse import urlparse
from secret_hunter.auth_check import confirm_license

def _get_cache_path(url, cache_dir):
    """Generates a cache path for a given URL."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    return os.path.join(cache_dir, filename)

def _verify_checksum(filepath, expected_checksum):
    """Verifies the checksum of a downloaded file."""
    if not expected_checksum:
        return True
    
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    
    calculated_checksum = hasher.hexdigest()
    if calculated_checksum.lower() == expected_checksum.lower():
        print(f"Checksum verified for {os.path.basename(filepath)}")
        return True
    else:
        print(f"Checksum mismatch for {os.path.basename(filepath)}.")
        print(f"  Expected: {expected_checksum}")
        print(f"  Got:      {calculated_checksum}")
        return False


def _download_archive(url, cache_path, max_size_mb, timeout, expected_checksum):
    """Downloads an archive file with progress and size checks."""
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    if total_size > max_size_mb * 1024 * 1024:
        raise ValueError(f"Download size ({total_size / 1024 / 1024:.2f} MB) exceeds the maximum of {max_size_mb} MB.")

    with open(cache_path, "wb") as f, tqdm(
        desc=f"Downloading {os.path.basename(cache_path)}",
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))
            
    if not _verify_checksum(cache_path, expected_checksum):
        raise ValueError("Checksum verification failed.")

    return cache_path

def _extract_archive(archive_path, extract_dir):
    """Extracts an archive to the specified directory."""
    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as tar:
            tar.extractall(path=extract_dir)
    elif zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as zipf:
            zipf.extractall(path=extract_dir)
    else:
        raise ValueError(f"Unsupported archive type: {archive_path}")

def _fetch_git(url, branch, tag, cache_dir):
    """Clones a git repository."""
    repo_name = os.path.basename(urlparse(url).path).replace(".git", "")
    repo_path = os.path.join(cache_dir, repo_name)
    if os.path.exists(repo_path):
        print(f"Using cached repository at {repo_path}")
        repo = git.Repo(repo_path)
        repo.remotes.origin.pull()
    else:
        print(f"Cloning repository from {url} to {repo_path}...")
        repo = git.Repo.clone_from(url, repo_path, progress=tqdm)

    if tag:
        repo.git.checkout(tag)
    elif branch:
        repo.git.checkout(branch)

    return repo_path

def _find_license(directory):
    """Finds and reads the license file in a directory."""
    for filename in ["LICENSE", "LICENSE.md", "COPYING"]:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    return None

def fetch_source(args):
    """Fetches the source code from a remote location."""
    os.makedirs(args.cache_dir, exist_ok=True)
    source_url = args.source_url

    if args.dry_run:
        print("Dry run enabled. No files will be downloaded or extracted.")
        # Attempt to fetch license for git repos in dry run
        if args.source_type == "git" or source_url.endswith(".git"):
             # This would require a partial clone or API access, which is complex.
             # For now, we just indicate what would happen.
            print(f"Would attempt to clone {source_url} and find a license.")
        return None

    if args.source_type == "git" or source_url.endswith(".git"):
        repo_path = _fetch_git(source_url, args.branch, args.tag, args.cache_dir)
        license_text = _find_license(repo_path)
        if args.verify_license:
            confirm_license(license_text, force_confirmation=True)
        return repo_path

    elif args.source_type == "archive" or source_url.endswith((".zip", ".tar.gz", ".tgz")):
        cache_path = _get_cache_path(source_url, args.cache_dir)
        if not os.path.exists(cache_path):
            _download_archive(source_url, cache_path, args.max_download_size, args.timeout, args.verify_checksum)

        extract_dir = cache_path.rsplit(".", 1)[0]
        _extract_archive(cache_path, extract_dir)
        license_text = _find_license(extract_dir)
        if args.verify_license:
            confirm_license(license_text, force_confirmation=True)
        return extract_dir

    else:
        raise ValueError(f"Unsupported source type for URL: {source_url}")
