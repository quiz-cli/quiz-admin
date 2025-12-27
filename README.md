# quiz-admin

This is the admin client side of the client-server quiz application. It tries to
provide the quiz game experience similar to **Kahoot** but in much lighter and
open manner as a CLI program.

The admin client controls the server and it is operated by a lecturer. It sends the commands through the **WebSockets** and receives the state of the game.

The **Asyncio** is used to control the server. It provides asynchronous network
communication with clients in JSON (sending questions, receiving answers),
showing the information and proceeding with the quiz questions.

Most of the program entities are implemented as **Data Classes** (`Players`,
`Player`, `Quiz`, `Questions`, `Question`, `Option`). It loads the quiz
questions from a **YAML** file.
