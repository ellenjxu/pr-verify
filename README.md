# PR-Verify

PR-Verify is an automated LLM agent for reviewing and verifying Github PRs.

We verify that contributor code works as intended, by generating unit tests and executing the code with LLM-generated ["oracle verifiers"](https://arxiv.org/html/2305.14591v3).

> Won "Best Pear Hack" at OpenAI x PearVC hackathon.

## How it works

The workflow is runs on GH Actions:

1. Event triggers on label "pr-verify"
2. Runner generates unit tests using for the PR, checks if it is valid Python code using guardrails
3. Runner tests the merged code on the unit tests in subprocess sandbox
4. Creates a synopsis (with threat score and analysis) on the PR (todo)

[demo video](https://www.loom.com/share/1569250d090b434da6e64abb8c284e60?sid=58f32c61-ff5f-4d4c-8c6d-93b87cc50bed)

## Setup

the quick & easy setup:

1. In repository settings

- Add OPENAI_AI_KEY to repo secrets
- Enable GH actions push access

2. Copy over GH action: `.github/workflows/pr-verify.yml`

That's it! Just add the `pr-verify` label and let PR-Verify do the rest.

## todo

- [ ] GH actions workflow, spin up docker container (code execution sandbox)
- [ ] automated repo installation setup (infer instructions from readme)
- [ ] synopsis/threat analysis comment on PR
- [ ] merging conflicts in feature branch?
- [ ] PR-Verify on GH Action marketplace
