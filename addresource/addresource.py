import requests
from bs4 import BeautifulSoup
import re
import click


def get_soup_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_sha256_hash_from_link(sha256_link, package, package_version=None):
    if package_version:
        url = f"https://pypi.org/project/{package}/{package_version}/{sha256_link}"
    else:
        url = f"https://pypi.org/project/{package}/{sha256_link}"
    
    soup = get_soup_from_url(url)

    # Find all 'tr' tags and iterate over them
    for tr in soup.find_all('tr'):
        th = tr.find('th')
        if th and th.text == 'SHA256':
            sha256_tr = tr
            break
    else:
        print("No SHA256 hash found in the page.")
        return None
    
    sha256_code = sha256_tr.find('td').find('code')
    sha256_hash = sha256_code.text

    return sha256_hash


def get_latest_source_distribution_and_sha256_hash(package_name, package_version=None):
    # If a version is specified, use it
    if package_version:
        url = f"https://pypi.org/project/{package_name}/{package_version}/#files"
    else:
        url = f"https://pypi.org/project/{package_name}/#files"
    
    soup = get_soup_from_url(url)

    # Find all links that match the source distribution pattern
    source_links = soup.find_all('a', href=re.compile(rf'{package_name}-.*\.tar\.gz$'))

    if not source_links:
        print(f"No source distribution found for package: {package_name}")
        return None
    
    # Find the "view hashes" link associated with the latest source distribution
    latest_sha256_link = source_links[0].find_next_sibling('a', string='view hashes')['href']
    latest_sha256_hash = get_sha256_hash_from_link(latest_sha256_link, package_name, package_version)
    latest_source_link = source_links[0]['href']

    return latest_source_link, latest_sha256_hash


@click.command()
@click.argument("formula-path", type=click.Path(exists=True))
@click.argument("package", type=str)
@click.option("--dry-run", is_flag=True, help="Print the new formula to the console instead of writing it to the file.")
def add_resource_to_homebrew_formula(formula_path, package, dry_run):
    """Add a resource to a Homebrew formula."""
    # Split the package string by '=='
    parts = package.split('==')

    # If there are two parts, the second part is the version
    if len(parts) == 2:
        package_name, package_version = parts
    else:
        package_name = package
        package_version = None

    latest_source_link, latest_sha256_hash = get_latest_source_distribution_and_sha256_hash(package_name, package_version)
    if not latest_source_link:
        return

    with open(formula_path, 'r') as file:
        formula = file.read()

    # Define the resource block
    resource_block = f'  resource "{package_name}" do\n' \
                     f'    url "{latest_source_link}"\n' \
                     f'    sha256 "{latest_sha256_hash}"\n' \
                     f'  end\n\n'

    # Split the formula at 'def install'
    parts = formula.split('def install', 1)

    # Insert the resource block before 'def install'
    new_formula = parts[0] + resource_block + 'def install' + parts[1]

    if dry_run:
        print("Dry run enabled. The following resource block would be added to the formula:\n")
        print(resource_block)
    else:
        # Write the new formula to the file
        with open(formula_path, 'w') as file:
            file.write(new_formula)
        print(f"Resource added to {formula_path}")


