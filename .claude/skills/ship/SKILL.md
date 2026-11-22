---
name: ship
description: Run the test suite, then show the working-tree changes and draft a commit message. Does not commit or push.
disable-model-invocation: true
---

Prepare this project for a commit. Do not commit or push unless the user asks you to in a separate message.

1. Run the test suite from the project root:

   ```bash
   .venv/bin/pytest -q
   ```

2. If any tests fail, report the failing test names and the key error lines from the output. Then stop. Do not continue to the next steps.

3. If all tests pass, run these two commands and show their output:

   ```bash
   git status
   git diff --stat
   ```

   Include untracked files from `git status` in your summary even though `git diff --stat` does not list them.

4. Draft a commit message based on the changes shown. Use this format:
   - A subject line of 72 characters or fewer, in the imperative mood (for example `feat: add streak display to habit list`).
   - A blank line, then a short body of plain sentences explaining what changed and why.

   Show the draft to the user and say it has not been committed.

5. Finish by asking whether the user wants you to commit with this message. Do not run `git add`, `git commit`, or `git push` yourself.
