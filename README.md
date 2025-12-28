# quiz-admin

This is the admin side of the client-server quiz application. It tries to
provide the quiz game experience similar to **Kahoot** but in much lighter and
open manner as a CLI program.

The admin client controls the server and is operated by a lecturer.  Asyncio is
used to control the game flow. It sends commands through **WebSockets** and
receives the state of the game.

The admin client loads quiz questions from a **YAML** file and verifies them
against the `Quiz` **data class** from the companion
[`quiz-common`](https://github.com/quiz-cli/quiz-common) package.

See the `data/` directory in this repository for reference quiz files.

## Usage

Get the `uv` tool.

```bash
$ uv tool install . --editable
```

Run the admin client as a module, pointing it to the quiz server and a YAML quiz file:

```bash
$ quiz_admin <host:port> <quiz-file.yaml>
```

The admin client then connects via WebSocket and will prompt you to send commands
(e.g. press `y` to move to the next question).

## Contributing

The code needs to comply with:

```bash
$ uv run ruff format
```

```bash
$ uv run ruff check
```
