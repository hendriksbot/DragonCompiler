# DragonCompiler

This repository compiles Dungeons & Dragons data from individual json files into a sqlite database.


## Set-up

1. Install python 3.11.2 or higher

2. Create a virtual environtment
    ```
    python -m venv .venv
    ```
3. Activate the virtual environment
    ```
    .venv\Scripts\activate
    ```
4. Install the required packages
    ```
    pip install -e .[dev]
    ```
5. Intstall pre-commit
    ```
    pre-commit install
    ```

6. Test pre-commit
    ```
    pre-commit run --all-files
    ```

## Compile a database

- For testing purpose, you could run just the build command. For help and more
details, run the following command
    ```
    dragon build --help
    ```
- For releasing a proper new database with, it is recommended to use the
release command. This will create a release folder

    - help:
        ```
        dragon release --help
        ```
    - release example:
        ```
        dragon release --source <spells_folder>
        ```
