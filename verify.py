"""
This template is intended for creating simple validators.

If your validator is complex or requires additional post-installation steps, consider using the template repository instead.

The template repository can be found here: https://github.com/guardrails-ai/validator-template
"""
    
from typing import Any, Callable, Dict, Optional
import subprocess
import os

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/pr_validator", data_type="string")
class PrValidator(Validator):
    """# Overview

    | Developed by | Ellen Xu |
    | Date of development | Apr 27, 2024 |
    | Validator type | Format |
    | License | Apache 2 |
    | Input/Output | Output |

    # Description
    Verifies the unit tests generated are valid and runs them on the merged repository.
    
    ## Requirements

    * Dependencies:
        - guardrails-ai>=0.4.0
        - git
        - pytest
        - {FIXME: Include any other dependencies you need here}

    * Dev Dependencies:
        - pytest
        - pyright
        - ruff
        - {FIXME: Include any other dev dependencies you need here}

    * Foundation model access keys:
        - OPENAI_API_KEY


    # Installation

    ```bash
    $ guardrails hub install hub://guardrails/pr_validator
    ```

    # Usage Examples

    ## Validating string output via Python

    In this example, we apply the validator to a string output generated by an LLM.

    ```python
    # Import Guard and Validator
    from guardrails.hub import PrValidator
    from guardrails import Guard

    # Setup Guard
    guard = Guard.use(
        PrValidator({FIXME: list any args here})
    )

    guard.validate({FIXME: Add an input that should pass the validator})  # Validator passes
    guard.validate({FIXME: Add an input that should fail the validator})  # Validator fails
    ```
    """  # noqa

    def __init__(
        self,
        github_pr_link: str,
        unit_test_code: str,
        on_fail: Optional[Callable] = None,
    ):
        """Initializes a new instance of the PrValidator class.
        
        Args:
            github_pr_link (str): The GitHub PR link to clone and test.
            unit_test_code (str): The unit test code to run on the merged code.
            on_fail`** *(str, Callable)*: The policy to enact when a validator fails.  If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
        """
        super().__init__(on_fail=on_fail)
        self.github_pr_link = github_pr_link
        self.unit_test_code = unit_test_code

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validates that the unit tests run successfully on the merged PR code.
        
        Args:
            value (Any): The value to validate.
            metadata (Dict): The metadata to validate against.

            FIXME: Add any additional args you need here in metadata.
            | Key | Description |
            | --- | --- |
            | a | b |
        """
        
        tmp_repo = "/tmp/repo"
        base_repo_url = "/".join(self.github_pr_link.split("/")[:-2])

        print("Cloning repo: ", base_repo_url)
        if os.path.exists(tmp_repo):         # remove and reclone if already exists
            subprocess.run(["rm", "-rf", tmp_repo])
        subprocess.run(["git", "clone", base_repo_url, tmp_repo])
        subprocess.run(["git", "checkout", metadata["branch"]], cwd=tmp_repo)  # Assuming PR is fetched
        subprocess.run(["git", "merge", "origin/main"], cwd=tmp_repo)

        # set up venv for dependencies
        venv_path = os.path.join(tmp_repo, "venv")
        subprocess.run(["python", "-m", "venv", venv_path], cwd=tmp_repo)
        activate_script = os.path.join(venv_path, "bin", "activate")
        subprocess.run(metadata["install_cmds"], cwd=tmp_repo, shell=True, executable="/bin/bash")
        if os.path.exists(os.path.join(tmp_repo, "requirements.txt")):
            pip_install_cmd = f"source {activate_script} && pip install -r requirements.txt"
            print("Installing dependencies: ", pip_install_cmd)
            subprocess.run(pip_install_cmd, cwd=tmp_repo, shell=True, executable="/bin/bash")
        else:
            print("No requirements.txt found. Skipping dependency installation.")

        # test to make sure unit test code is valid
        print("Running tests on branch: ", metadata["branch"])
        test_file_path = os.path.join(tmp_repo, "test_pr_output.py")
        with open(test_file_path, "w") as f:
            f.write(self.unit_test_code)
        
        # run tests
        pytest_cmd = f"source {activate_script} && pytest {test_file_path}"
        result = subprocess.run(pytest_cmd, cwd=tmp_repo, shell=True, executable="/bin/bash", capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        if result.returncode == 0:
            return PassResult()
        else:
            return FailResult(
                error_message=f"Unit tests failed",
                fix_value="Review the unit tests for errors."
            )

# # Run tests via `pytest -rP ./pr_validator.py`
# class TestPrValidator:
#     def test_success_case(self):
#         # FIXME: Replace with your custom test logic for the success case.
#         validator = PrValidator("https://github.com/ellenjxu/test/pull/1", "import unittest\n\nclass TestSum(unittest.TestCase):\n    def test_sum(self):\n        self.assertEqual(sum([1, 2, 2]), 5, 'Should be 5')\n\nif __name__ == '__main__':\n    unittest.main()")
#         result = validator.validate(None, {})
#         assert isinstance(result, PassResult) is True

#     def test_failure_case(self):
#         # FIXME: Replace with your custom test logic for the failure case.
#         validator = PrValidator("https://github.com/user/repo/pull/123", "import unittest\n\nclass TestSum(unittest.TestCase):\n    def test_sum(self):\n        self.assertEqual(sum([1, 2, 2]), 6, 'Should be 5')\n\nif __name__ == '__main__':\n    unittest.main()")
#         result = validator.validate(None, {})
#         assert isinstance(result, FailResult) is True
#         assert result.error_message == "Unit tests failed."
#         assert result.fix_value == "Review the unit tests for errors."