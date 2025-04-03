# Simulib: A Library for Metabolic Modeling

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/Amyris/simulib/main/pyproject.toml&query=project.version&label=version)](https://github.com/Amyris/simulib)

Simulib is a Python library designed for metabolic modeling and dynamic flux balance analysis (dFBA) simulation. It provides tools for defining, analyzing, and simulating metabolic networks, with a focus on kinetic modeling and steady-state analysis.

## Features

*   **Dynamic model definition:** Define and simulate metabolic networks using kinetic rate laws.
*   **Steady-State Analysis:** Perform steady-state flux analysis and other related calculations.
*   **DFBA Support:** The library supports Dynamic Flux Balance Analysis.
*   **Extensible:** Easily extend the library with new analysis methods and more.
*   **Modular Design:** The library is designed with a modular architecture, making it easy to understand and contribute to.


## Getting Started

### Prerequisites

*   Python 3.8 or higher
*   Docker (for development)

### Installation

Simulib is not yet available on PyPI. For now, you can install it directly from the repository:

1.  Clone the repository:

    ```bash
    git clone https://github.com/Amyris/simulib.git
    cd simulib
    ```

2.  Install the library using `uv` (inside the Docker container):

    ```bash
    docker-compose run --rm app uv sync
    ```
    or if you want to install the extras:
    ```bash
    docker-compose run --rm app uv sync --extra dfba
    ```

### Running Tests

To run the tests, use the following command inside the Docker container:

- If you want to run the core tests:
  ```bash
  docker-compose run --rm app uv run --with pytest pytest ./tests/core
  ```
- If you want to run the tests with the dfba extra:
  ```bash
  docker-compose run --rm app uv run --with dfba --with pytest pytest ./tests
  ```

## Development
### Docker Setup
We use Docker for development. Here's how to set up your development environment:

1. **Clone the Repository**:

```bash
git clone https://github.com/Amyris/simulib.git
cd simulib
```
2. **Start the Docker Environment**:

```bash
docker-compose up -d
```
3. **Enter the Docker Container**:

```bash
docker-compose run --rm app bash
```
## Development Workflow
1. **Branching**: Create a new branch for your work:

```bash
git checkout -b feature/my-new-feature
```
2. **Development**: Make your changes, ensuring they align with the project's goals and coding style.

 - Adding Dependencies:

```bash
docker-compose run --rm app uv add <package>
```
 - Upgrading Dependencies:

```bash
# Initial setup or after changes to uv.lock
docker-compose run --rm app uv sync
# Add a new dependency
docker-compose run --rm app uv add <package-name>
# Upgrade a specific dependency
docker-compose run --rm app uv update <package-name>
# Upgrade all dependencies
docker-compose run --rm app uv update
# Install/Sync with extras
docker-compose run --rm app uv sync --extra dev --extra test --extra dfba
```

3. **Testing**: Run the existing tests to ensure your changes haven't introduced any regressions. Add new tests if you're adding new functionality.

```bash
# Run all tests
docker-compose run --rm app uv run --with dfba --with pytest pytest
# Run core tests only
docker-compose run --rm app uv run --with pytest  pytest ./tests/core
# Run tests with dfba extra
docker-compose run --rm app uv run --with dfba --with pytest pytest ./tests/extras/extra_dfba
# Run a specific test file
docker-compose run --rm app uv run --with pytest pytest /path/to/mytest.py
```
4. **Linting and Formatting**: Ensure your code adheres to our linting and formatting standards. We use black and isort.

```bash
# Format a specific file with black
docker-compose run --rm app uv run black "path/to/your/file.py"
# Format all files with black
docker-compose run --rm app uv run black .
# Sort imports in a specific file with isort
docker-compose run --rm app uv run isort "path/to/your/file.py"
# Sort imports in all files with isort
docker-compose run --rm app uv run isort .
```

5. **Commit**: Commit your changes with clear and concise commit messages using Commitizen.
```bash
# install cz
pip install commitizen
# stage modified files
git add .
# create commit and follow instructions
cz c
```

6. **Push**: Push your branch to your forked repository.

7. **Pull Request**: Create a pull request to the main repository.

### Using Dev Containers in VS Code

For a streamlined development experience, you can use Visual Studio Code's Dev Containers feature:

1. **Install VS Code and the Remote - Containers Extension**: Ensure you have Visual Studio Code installed along with the Remote - Containers extension.

2. **Open the Repository in VS Code**: Open the simulib repository folder in VS Code.

3. **Reopen in Container**: A .devcontainer configuration is provided and VS Code should prompt you to reopen the project in a container. If not, open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and select:

```makefile
Remote-Containers: Reopen in Container
```
VS Code will build the container as specified in the .devcontainer folder and attach to it, giving you an isolated development environment that mirrors the Docker setup.

4. **Working Inside the Container**: Once inside the container, you can use the integrated terminal to run commands, tests, or any other development tasks as outlined above.

5. **Rebuilding the Container**
If you make changes to the container configuration, you can rebuild the container by using the Command Palette and selecting:

```makefile
Remote-Containers: Rebuild Container
```

**Note**: To have `git` working correctly within the dev container, one must match the `USER_ID` build argument to your own user_id (`echo $UID`).

## Changelog

This project uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) and `commitizen` to manage the changelog. The `CHANGELOG.md` file is automatically generated based on commit messages.

### Code Style
**Python**: We follow the PEP 8 style guide.
**Formatting**: We use black for code formatting.
**Imports**: We use isort for import sorting.

## Contributing
We welcome contributions from everyone! Please see our CONTRIBUTING.md for more information on how to get involved.

## Code of Conduct
Please review our CODE_OF_CONDUCT.md to understand the standards of behavior we expect from contributors.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
If you have any questions or need help, please open an issue or reach out to us directly.