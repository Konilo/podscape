# Podscape
## 

## Running python interactively in the Docker container via VS Code

- Add the following shortcut:
```
{
    "key": "ctrl+enter",
    "command": "python.execSelectionInTerminal",
    "when": "editorTextFocus && !editorReadonly && editorLangId == 'python'"
}
```
- If you're under Windows: run `wsl` and start Docker Desktop.
- Run `make run-dev-env`.
- In the "Remote Explorer" tab (found in the Side Bar), find the Docker container, and select "Attach in Current Window".
- Open the `app/` folder.
- Extensions are not always mirrored from VS Code in the local OS to VS Code in the container. Install the extensions you want. The recommended python extension is mandatory.
- Open a python file and set the interpreter as `/usr/local/bin/python`.
- You're all set: use Ctrl+Enter to run python interactively, command-by-command in the Docker container using the dockerized python version and python libs. You can also use the VS Code "Run and Debug" features.
