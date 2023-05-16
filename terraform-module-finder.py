import os
import sys
import subprocess
import argparse
import glob
import requests
import tempfile
import shutil
import time


RATE_LIMIT_DELAY = 1  # Delay in seconds between API requests

# Function to check if a directory contains a Terraform module using terraform-docs
def is_terraform_module(directory):
    skip_directories = [".git", ".terraform", ".svn", ".hg", ".idea", "node_modules", "vendor", "__pycache__", "venv", "virtualenv"]
    if any(dir_name in directory for dir_name in skip_directories):
        return False
    tf_files = glob.glob(f"{directory}/*.tf")
    return bool(tf_files)


# Function to get the name of a Terraform module
def get_module_name(directory):
    return directory.split("/")[-1]


# Function to get the description of a Terraform module
def get_module_description(directory):
    provider_lines = []
    tf_files = glob.glob(f"{directory}/*.tf")
    for tf_file in tf_files:
        with open(tf_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "provider " in line:
                    provider_name = line.strip().split('"')[1] if '"' in line else line.strip().split()[1]  # Extract the provider name
                    provider_lines.append(provider_name)

    if provider_lines:
        providers = ", ".join(provider_lines)
        return f"Providers: {providers}"
    else:
        return ""  # Default to an empty string if no providers found

# Function to calculate the quality of a Terraform module
def calculate_module_quality(directory):
    # Example logic: Calculate the number of resources in the module
    tf_files = glob.glob(f"{directory}/*.tf")
    total_resources = 0
    for tf_file in tf_files:
        with open(tf_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith("resource"):
                    total_resources += 1

    # Assign quality based on the number of resources
    if total_resources < 5:
        return "Low"
    elif total_resources < 10:
        return "Medium"
    else:
        return "High"


# Function to calculate the size of a Terraform module
def calculate_module_size(directory):
    # Example logic: Calculate the total number of files in the module
    file_count = sum(len(files) for _, _, files in os.walk(directory))
    return file_count


# Function to calculate the score of a Terraform module
def calculate_module_score(directory):
    # Example logic: Calculate the score based on quality and size
    quality = calculate_module_quality(directory)
    size = calculate_module_size(directory)

    # Assign score based on quality and size
    if quality == "Low":
        if size <= 10:
            return "1"
        elif size <= 50:
            return "2"
        else:
            return "3"
    elif quality == "Medium":
        if size <= 10:
            return "4"
        elif size <= 50:
            return "5"
        else:
            return "6"
    else:
        if size <= 10:
            return "7"
        elif size <= 50:
            return "8"
        else:
            return "9"


# Function to process directories locally
def process_local_directories(directory):
    modules = []
    for root, dirs, files in os.walk(directory):
        if ".terraform" in dirs:
            dirs.remove(".terraform")  # Exclude .terraform directories
        if is_terraform_module(root):
            module_name = get_module_name(root)
            module_description = get_module_description(root)
            module_quality = calculate_module_quality(root)
            module_size = calculate_module_size(root)
            module_score = calculate_module_score(root)
            modules.append((module_name, root, module_description, module_quality, module_size, module_score))
    return modules


def process_github_repositories(org_name, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/orgs/{org_name}/repos"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    repositories = response.json()
    
    catalog = []
    total_repos = len(repositories)  # Total repositories scanned
    total_modules = 0  # Total modules found

    for repository in repositories:
        repo_name = repository["name"]
        repo_url = repository["html_url"]
        repo_clone_url = repository["clone_url"]

        # Create a temporary directory to clone the repository
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Clone the repository locally
                print(f"Cloning repository: {repo_name}")
                subprocess.check_call(["git", "clone", repo_clone_url, temp_dir])

                # Recursively process the cloned directory for Terraform modules
                modules = process_local_directories(temp_dir)

                # Update catalog and module count
                for module in modules:
                    module_name, _, module_description, module_quality, module_size, module_score = module
                    catalog.append((module_name, repo_url, module_description, module_quality, module_size, module_score))

                # Print completion message
                print(f"Completed processing repository: {repo_name}")

            except subprocess.CalledProcessError as e:
                print(f"Failed to clone repository: {repo_name}")
                print(e)
                continue
    return catalog, total_repos, total_modules





def main():
    parser = argparse.ArgumentParser(description="Terraform Module Finder")
    parser.add_argument("--path", help="Path to local directory for processing")
    parser.add_argument("--github", action="store_true", help="Flag to process GitHub repositories")
    args = parser.parse_args()

    if args.path:
        # Process local directories
        modules = process_local_directories(args.path)
    elif args.github:
        # Process GitHub repositories
        org_name = os.getenv("GITHUB_ORGANIZATION")
        access_token = os.getenv("GITHUB_ACCESS_TOKEN")
        if not org_name or not access_token:
            print("Please set the GITHUB_ORGANIZATION and GITHUB_ACCESS_TOKEN environment variables.")
            sys.exit(1)
        modules, total_repos, total_modules = process_github_repositories(org_name, access_token)
    else:
        # Default option: Process current directory
        modules = process_local_directories(os.getcwd())

    # Check if any modules are found in the catalog
    if modules:
        catalog, total_repos, total_modules = modules

        # Write the catalog to a file
        with open("terraform_modules_catalog.txt", "w") as file:
            for module in catalog:
                module_name, module_path, module_description, module_quality, module_size, module_score = module
                file.write(f"* [{module_name}]({module_path})\n")
                file.write(f"    Description: {module_description}\n")
                file.write(f"    Quality: {module_quality}\n")
                file.write(f"    Size: {module_size} files\n")
                file.write(f"    Score: {module_score}\n\n")

        # Print statistics
        print("Catalog generation complete!")
        print(f"Total Repositories Scanned: {total_repos}")
        print(f"Total Modules Found: {total_modules}")
    else:
        print("No modules found.")



# Run the script
if __name__ == "__main__":
    main()