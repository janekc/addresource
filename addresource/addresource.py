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


def get_source_distribution_and_sha256_hash(package_name, package_version=None):
    # If a version is specified, use it
    if package_version:
        url = f"https://pypi.org/project/{package_name}/{package_version}/#files"
    else:
        url = f"https://pypi.org/project/{package_name}/#files"

    soup = get_soup_from_url(url)

    #print(soup.text)

    # Find the div with the class 'card file__card'
    file_card_div = soup.find('div', class_='card file__card')
    link_tag = file_card_div.find('a')
    source_link = link_tag['href']

    # Find the "view hashes" link inside the div
    hashes_link_tag = file_card_div.find('a', string='view hashes')
    hashes_link = hashes_link_tag['href']

    if not source_link:
        raise ValueError(f"No source distribution found for {package_name}! Check the package name and version.")
    
    # Find the "view hashes" link associated with the latest source distribution
    sha256_hash = get_sha256_hash_from_link(hashes_link, package_name, package_version)

    return source_link, sha256_hash


def add_package(formula_path, package, dry_run):
    # Split the package string by '=='
    parts = package.split('==')

    # If there are two parts, the second part is the version
    if len(parts) == 2:
        package_name, package_version = parts
    else:
        package_name = package
        package_version = None

    latest_source_link, latest_sha256_hash = get_source_distribution_and_sha256_hash(package_name, package_version)
    if not latest_source_link:
        return

    with open(formula_path, 'r') as file:
        formula = file.read()

    # Check if a resource block for the package exists
    if f'resource "{package_name}" do' in formula:
        print(f"A resource block for {package_name} already exists.")
    else:
        print(f"No resource block for {package_name} found. Adding one...")

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


def add_requirements_file(formula_path, requirements_file, dry_run):
    # Parse the requirements file
    with open(requirements_file, 'r') as file:
        requirements = file.readlines()
        for requirement in requirements:
            requirement = requirement.strip()
            print(f"Adding resource for {requirement}...")
            add_package(formula_path, requirement, dry_run)


@click.command()
@click.argument("formula-path", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Print the new formula to the console instead of writing it to the file.")
@click.option('--package', default=None, help='The name of the package to add.')
@click.option('--requirements-file', type=click.Path(exists=True), default=None, help='The path to a requirements.txt file.')
def add_resource_to_homebrew_formula(formula_path, package, requirements_file, dry_run):
    """Add a resource to a Homebrew formula."""
    if package:
        add_package(formula_path, package, dry_run)
    elif requirements_file:
        add_requirements_file(formula_path, requirements_file, dry_run)
    else:
        print("You must specify either a package or a requirements file.")



