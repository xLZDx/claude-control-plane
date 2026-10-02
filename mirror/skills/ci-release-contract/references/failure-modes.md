# ci-release-contract: failure modes

Load on demand. Each line is a defect class seen in practice.

- Required check missing from branch protection, so 'all green' hides it.
- Workflow green on a path filter that excluded the changed files.
- Approval recorded for head A, merged head B.
- Different dependency versions locally than in CI.
