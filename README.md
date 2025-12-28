# quiz-admin

This is the admin client of a client-server quiz application. It aims to
provide a quiz game experience similar to **Kahoot**, but in a much lighter
and more open form as a CLI program.

The admin client controls the server and is operated by a lecturer. Asyncio is
used to control the game flow. It sends commands through **WebSockets** and
receives the state of the game.

The admin client loads quiz questions from a **YAML** file and verifies them
against the `Quiz` **data class** from the companion
[`quiz-common`](https://github.com/quiz-cli/quiz-common) package.

See the `data/` directory in this repository for reference quiz files.

## Usage

Install the `uv` tool:

```bash
$ uv tool install . --editable
```

Run the admin client as a module, pointing it to the quiz server address and
port, and a YAML quiz file:

```bash
$ quiz-admin <host:port> <quiz-file.yaml>
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
