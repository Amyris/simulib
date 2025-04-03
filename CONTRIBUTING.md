# Contributing to Simulib

Thank you for your interest in contributing to Simulib! We welcome contributions from everyone and appreciate your help in making this project better.

## Getting Started

1.  **Read the README:** Familiarize yourself with the project's goals, structure, and setup instructions by reading the [README.md](README.md) file.
2.  **Code of Conduct:** Please review our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the standards of behavior we expect from contributors.
3.  **Issues:** Check the [issue tracker](https://github.com/Amyris/simulib/issues) for existing issues you might be interested in working on. If you have a new idea or encounter a bug, please open a new issue to discuss it.
4. **Fork the Repository:** Fork the Simulib repository to your own GitHub account. This will allow you to make changes without directly affecting the main repository.
5. **Clone Your Fork:** Clone your forked repository to your local machine:

    ```bash
    git clone https://github.com/Amyris/simulib.git
    cd simulib
    ```

## Development Workflow

1.  **Branching:** Create a new branch for your work. Use a descriptive name that reflects the purpose of your changes (e.g., `fix-typo-in-docs`, `add-new-kinetic-method`, `implement-steady-state-algorithm`).

    ```bash
    git checkout -b feature/my-new-feature
    ```

2.  **Development:** Make your changes, ensuring they align with the project's goals and coding style.
3.  **Testing:** Run the existing tests to ensure your changes haven't introduced any regressions. Add new tests if you're adding new functionality.

    ```bash
    docker-compose run --rm app uv run --with dfba pytest
    # or for a specific test file
    docker-compose run --rm app uv run --with dfba pytest "path/to/your/test.py"
    ```

4.  **Linting and Formatting:** Ensure your code adheres to our linting and formatting standards. We use `black` and `isort`.

    ```bash
    docker-compose run --rm app uv run black "path/to/your/file.py"
    docker-compose run --rm app uv run isort "path/to/your/file.py"
    ```

5.  **Commit:** This project uses Commitizen to enforce Conventional Commits and manage versioning.  
    The configuration is defined in the pyproject.toml file:
    ```yaml
    [tool.commitizen]
    name = "cz_conventional_commits"
    tag_format = "v$version"
    version_scheme = "pep440"
    version_provider = "pep621"
    update_changelog_on_bump = true
    major_version_zero = true
    ```
    *Installation*: Install Commitizen globally or as a development dependency:
    ```bash
    pip install commitizen
    ```
    *Creating commits*: Instead of running `git commit` directly, use Commitizen to create commits that follow the Conventional Commits format:
    ```bash
    git add .
    cz commit
    ```
    This command starts an interactive prompt that helps you format your commit message correctly. It will ask you questions about the type of change, scope, and a short description, ensuring your commit messages are consistent and clear.

6.  **Push:** Push your branch to your forked repository:

    ```bash
    git push origin feature/my-new-feature
    ```
7. **Bumping the Version** When you’re ready to release a new version, use:

    ```bash
    cz bump
    ```
    This command will:
    *  Bump the version following the PEP 440 scheme.
    *  Create a new tag in the format v<version> (e.g., v1.2.3).
    *  Automatically update the changelog since update_changelog_on_bump is set to true.

8.  **Pull Request:** Create a pull request (PR) from your branch to the main Simulib repository's `main` branch.
    *   Provide a clear title and description of your changes.
    *   Reference any related issues (e.g., "Fixes #123").
    *   Explain the purpose and scope of your changes.
    *   Include any relevant context or background information.

## Code Style and Conventions

*   **Python:** We follow the PEP 8 style guide for Python code.
*   **Documentation:** Write clear and concise documentation for your code, including docstrings for functions and classes.
*   **Testing:** Write unit tests for new features and bug fixes.

## Docker Development

We use Docker for development. Here are some common tasks:

*   **Starting/Stopping:**
    ```bash
    docker-compose up -d  # Start in detached mode
    docker-compose stop   # Stop containers
    docker-compose down   # Stop and remove containers
    ```
*   **Running Tests:**
    ```bash
    docker-compose run --rm app uv run --with dfba --with pytest pytest
    ```
*   **Shells:**
    ```bash
    docker-compose run --rm app bash  # Bash shell
    docker-compose exec app bash # Connect to a running container
    ```
*   **Adding Dependencies:**
    ```bash
    docker-compose run --rm app uv add <package>
    ```
*   **Upgrading Requirements:**
    ```bash
    docker-compose run --rm app uv lock --upgrade
    # or for a specific dependency
    docker-compose run --rm app uv lock --upgrade-package <package>
    ```

## Review Process

*   Your pull request will be reviewed by one or more maintainers.
*   They may provide feedback or request changes.
*   Be responsive to feedback and address any concerns.
*   Once the review is complete and all checks pass, your PR will be merged.

## Reporting Bugs

If you find a bug, please open an issue in the issue tracker. Provide as much detail as possible, including:

*   A clear description of the bug.
*   Steps to reproduce the bug.
*   Expected behavior.
*   Actual behavior.
*   Any relevant error messages or logs.
*   Your environment (OS, Python version, etc.).

## Suggesting Enhancements

If you have an idea for an enhancement, please open an issue to discuss it. Explain your idea clearly and provide any relevant context.

## Questions

If you have any questions, feel free to open an issue or reach out to us directly.

We look forward to your contributions!
