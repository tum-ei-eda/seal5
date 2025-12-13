# Contributing to Seal5

Thank you for your interest in contributing to **Seal5**! We welcome all contributions—bug fixes, documentation improvements, new features, or development help.

## 💬 Discussing Ideas

If you're unsure where to start or want to propose an idea, consider joining our **monthly user meetings**:
https://github.com/tum-ei-eda/seal5/discussions/104

You are also welcome to start a discussion on GitHub to gather early feedback.

## Porting Seal5 to new LLVM Releases

See [PORTING.md](PORTING.md) for more details!

## 🏁 Finding Something to Work On

We use labels to highlight contributor-friendly tasks:

- **[`type:good first issue`](https://github.com/tum-ei-eda/seal5/issues?q=is%3Aissue+state%3Aopen+label%3A%22type%3Agood+first+issue%22)** – small, self-contained tasks ideal for newcomers.
- **[`type:help wanted`](https://github.com/tum-ei-eda/seal5/issues?q=is%3Aissue+state%3Aopen+label%3A%22type%3Ahelp+wanted%22)** – issues that are actively seeking contributors.

If you decide to work on an issue, **please comment on it first** so others know it is in progress.

## 🐛 Reporting Bugs & Requesting Features

Please use the GitHub Issue templates provided in this repository.

For bugs, include:

- steps to reproduce
- expected vs. actual behavior
- logs or stack traces (if relevant)
- environment information (Python version, OS, etc.)

For feature requests, describe:

- the motivation
- the intended use-case
- possible alternatives

## 🔀 Submitting Changes (Pull Requests)

1. **Open a pull request** with a clear summary of your changes.
   (More info: https://help.github.com/pull-requests/)

2. **Follow our coding conventions** (see below).

3. **Write atomic commits** (one logical change per commit).
   For larger changes, use descriptive, multi-line commit messages such as:

   ```
   A brief summary of the commit

   A paragraph describing what changed, why it changed,
   and any potential implications or follow-ups.
   ```

4. **Ensure your code is documented and tested.**

5. **Keep your branch up to date** with the main branch to avoid conflicts.

## 🧹 Coding Conventions

- Use **Black** to auto-format all Python files:
  https://black.readthedocs.io/en/stable/
- Using **Pylint** is recommended but not required.
- Install development dependencies with:

  ```sh
  pip install -r requirements_dev.txt
  ```

## 🙌 Thank You

Every contribution—big or small—helps Seal5 grow and improve.
Thank you for your support!
