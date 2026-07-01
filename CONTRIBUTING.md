Contributing to fastapi-mail
=========================================

We welcome contributions to [fastapi-mail](https://github.com/sabuhish/fastapi-mail)

Issues
------

Feel free to submit issues and enhancement requests.

[Fatapi-Mail Issues](https://github.com/sabuhish/fastapi-mail/issues)

Contributing
------------

Please refer to each project's style and contribution guidelines for submitting patches and additions. In general, we follow the "fork-and-pull" Git workflow.

 1. **Fork** the repo on GitHub
 2. **Clone** the project to your own machine
 3. **Commit** changes to your own branch
 4. **Push** your work
 5. Submit a **Pull request** so that we can review your changes

### Before Start

`fastapi-mail` uses [Poetry](https://python-poetry.org/) for dependency management.
After forking and cloning the repo, install the project together with its
development dependencies from the project root:

```sh
pip install poetry
poetry install      # installs fastapi-mail plus the dev tools (pytest, black, isort, flake8, mypy)
poetry shell        # activate the virtual environment Poetry created
```

NOTE: Be sure to merge the latest from "upstream" before making a pull request!

### Testing

Run the test suite (pytest with coverage) via the Makefile:

```sh
make test
```

or run pytest directly:

```sh
pytest
```

Before opening a pull request, run the linters and type checks, and format the code:

```sh
make lint          # isort, black, flake8, mypy
make format_code   # auto-format with isort + black
```
