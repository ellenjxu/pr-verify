"""Generates test suite for a given PR."""

import os
import requests
from guardrails.hub import ValidPython
from guardrails import Guard
from openai import OpenAI
from github import Github
from verify import PrValidator

def get_pr_data(github_token, pr_url):
    g = Github(github_token)
    
    repo_url = '/'.join(pr_url.split('/')[-4:-2])
    repo = g.get_repo(repo_url)
    pr = repo.get_pull(int(pr_url.split('/')[-1]))
    
    diff_response = requests.get(pr.diff_url)
    pr_code = diff_response.text if diff_response.status_code == 200 else "Diff not available"

    feature_branch = pr.head.ref
    
    return pr_code, pr.body, feature_branch

def get_unit_tests(desc, code, client, model="gpt-3.5-turbo") -> str:
    prompt = f"""
    Generate unit tests for the following PR:\nDescription: {desc}\nCode:\n{code}. The tests should only be for the code in the pull request, do not write tests for the codebase.
    
    Your response should only return the code itself, do not return any additional information.
    """
    instructions = "You are an experienced developer and open-source Github contributor. Your job is to write code and generate a suite of unit tests for the given pull request, which can be run as a test suite script. The tests should be comprehensive and cover all the edge cases."

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.1
        )
        answer = response.choices[0].message.content
        answer = '\n'.join(answer.split('\n')[1:-1]) # first and last line are ```python```
        print(answer)

        try:
            guard.validate(answer)
            os.makedirs('pr-verify', exist_ok=True)
            with open('pr-verify/unit_tests.py', 'w') as f:
                f.write(answer)
            return answer
        except Exception as e:
            print("Error: ", e)
            prompt = f" An error occurred: {str(e)}. Please correct the issues and generate the unit tests again.\nDescription: {desc}\nCode:\n{code}. Only return your revised code, do not return any additional information."
            continue

def get_installation_commands(repo_url, branch, client, model="gpt-3.5-turbo"):
    prompt = f"""
    Given a Python project repository located at {repo_url} on branch {branch}, analyze the repository structure and content to determine the necessary commands to install all dependencies. You mah check if common dependency files like requirements.txt, setup.py, or environment-specific files might be present. Assume that the repo has already been cloned to a local directory.

    Your response should only return the commands, do not return any additional information. If None, return an empty string.
    """
    instructions = "Generate a list of shell commands for setting up the project dependencies. Separate each command by newline without any additional characters."

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.5
    )

    return response.choices[0].message.content.strip().split('\n') 

if __name__ == "__main__":
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    pr_url = os.getenv('PR_URL')

    client = OpenAI(api_key=openai_api_key)
    guard = Guard().use(ValidPython, on_fail="exception") 

    # testing
    code, desc, branch = get_pr_data(github_token, pr_url) 
    unit_tests = get_unit_tests(desc, code, client, model="gpt-3.5-turbo")
    print(unit_tests)
 
    # install_cmds = get_installation_commands(pr_url, branch, client, model="gpt-3.5-turbo")
    # print(install_cmds)

    # run unit tests
    # validator = PrValidator(pr_url, unit_tests)
    # result = validator.validate(None, {"branch": branch, "install_cmds": install_cmds})
    # print(result)