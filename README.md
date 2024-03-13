# Homebrew Formula Resource Adder
The script fetches the latest source distribution link and sha256 hash for the package from PyPI and adds a resource block to a Homebrew formula file. The resource block is added before the `def install` function in the formula file.

## Usage

```bash
python addresource.py [OPTIONS] FORMULA_PATH PACKAGE
```

## Arguments:
- `FORMULA_PATH`: The path to the Homebrew formula file.
- `PACKAGE`: The name and optionally version of the package to add a resource block for.

## Options:
- `--dry-run`: If specified, the script will print the new formula to the console instead of writing it to the file.

## Example

```bash
python addresource.py requests==2.3.0
```