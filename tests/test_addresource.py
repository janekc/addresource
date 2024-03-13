import pytest
from addresource.addresource import get_soup_from_url, get_sha256_hash_from_link, get_latest_source_distribution_and_sha256_hash

def test_get_soup_from_url():
    url = "https://pypi.org/project/requests/"
    soup = get_soup_from_url(url)
    assert soup.title.string == "requests · PyPI"

def test_get_sha256_hash_from_link():
    sha256_link = "#copy-hash-modal-d7d71a1a-90a6-4fa0-bb4b-3e1fb2de01a9"
    package = "requests"
    sha256_hash = get_sha256_hash_from_link(sha256_link, package)
    assert len(sha256_hash) == 64  # SHA256 hash is 64 characters long

def test_get_latest_source_distribution_and_sha256_hash():
    package = "requests"
    latest_source_link, latest_sha256_hash = get_latest_source_distribution_and_sha256_hash(package)
    assert latest_source_link.startswith("https://files.pythonhosted.org/packages/")
    assert len(latest_sha256_hash) == 64  # SHA256 hash is 64 characters long