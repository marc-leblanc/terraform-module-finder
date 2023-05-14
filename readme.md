# Terraform Module Finder

## Description
Terraform Module Finder is a script that helps in cataloging Terraform modules in local directories or GitHub repositories. It scans the directories, identifies the Terraform modules, and generates a catalog with module information.

## Usage
You can use this script to find and catalog Terraform modules in the following ways:

### Local Directories
To scan Terraform modules in local directories, use the `--path` option followed by the path to the directory you want to scan. For example:

```bash
python terraform-module-finder.py --path /path/to/directory
```

### GitHub Repositories
To scan Terraform modules in GitHub repositories, use the `--github` flag. Make sure to set the required environment variables `GITHUB_ORGANIZATION` and `GITHUB_ACCESS_TOKEN`. For example:

```bash
python terraform-module-finder.py --github
```


## Setup/Requirements
- Python 3.x
- Required scope on the GitHub Personal Access Token:
    - `repo` for accessing repositories
    - `read:org` for reading organization information

## Limitations
- The script currently has a rate limit for making requests to the GitHub API. Please be mindful of the rate limits and ensure you are within the allowed limits for your GitHub account.
- The script may not capture all possible Terraform modules, especially in complex repository structures or unconventional module organization.
- The accuracy of module descriptions heavily relies on the presence and consistency of provider configuration in the Terraform files. In some cases, the description may not accurately reflect the module's functionality.
- The script does not handle certain edge cases, such as modules defined in non-standard file extensions or non-standard module directory structures.


## Contributing
Contributions to the Terraform Module Finder script are welcome! If you want to contribute, please follow these steps:
1. Fork the repository and create your branch.
2. Make your changes and commit them.
3. Open a pull request with a detailed description of the changes you made.

We appreciate your contributions and efforts to improve the script!

## License
This script is licensed under the [GNU Affero General Public License v3.0](./gnu-agpl-v3.0.md). Please see the [LICENSE](./gnu-agpl-v3.0.md) file for more details.

