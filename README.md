# converterm

Ever had programs you wish you could just serve on the browser without having to rewrite them?
converterm allows you to serve any program over the web directly!

# Usage
To install dependencies:

```bash
bun install
```

Edit .env or .env.local to set the program to run either in continuous or one-shot mode:

```env
COMMAND="your command" # e.g. COMMAND="python3 main.py" or COMMAND="ls"
CONTINUOUS=False
```
CONTINUOUS mode means COMMAND will be executed, then all user interaction are transmitted to its stdin.
Non-CONTINUOUS mode means COMMAND will be executed for each request with the user input as its arguments.


To run:

```bash
bun dev
```

