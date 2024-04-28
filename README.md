# PR-Verify

PR-Verify is an automated LLM agent for reviewing and verifying Github PRs.

We verify that contributor code works as intended, by generating unit tests and executing the code with LLM-generated "oracle verifiers" (https://arxiv.org/html/2305.14591v3).

## setup

1. In repository settings

- Add OPENAI_AI_KEY to repo secrets
- Enable GH actions push access

2. Copy over GH action: `.github/workflows/pr-verify.yml`

That's it! Just add the `pr-verify` label and let PR-Verify do the rest.

---

## todo

- [ ] GH actions workflow, spin up docker container (code execution sandbox)
- [ ] automated repo installation setup (infer instructions from readme)
- [ ] synopsis/threat analysis comment on PR
