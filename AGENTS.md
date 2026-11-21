# Phone House Messenger Bot — Codex Working Instructions

## Write authorization

Codex may implement changes in this repository when the CEO explicitly
assigns the task to Codex. Keep changes within the assigned scope.

## GitHub workflow

1. Read the relevant code and repository instructions before editing.
2. Use a dedicated branch for the task. If the CEO assigns an existing PR,
   use its branch after confirming that Codex is the assigned writer.
3. Run the relevant tests and report the results.
4. Commit and push the changes to the task branch. Open a pull request
   or update the assigned PR.
5. In the PR, summarize the changes, test results, and any remaining issues.

## Release and secrets

- Do not push directly to `main` or bypass branch protection.
- Get separate CEO approval before merging, deploying, or changing
  production settings. Follow any required independent review.
- Never commit credentials, bot tokens, or `.env` files with secrets.
