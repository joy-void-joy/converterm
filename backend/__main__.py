import click
from environs import Env
from hypercorn.__main__ import main as hypercorn_main

env = Env()
env.read_env()
env.read_env(".env.local", override=True)


@click.group()
def cli():
    pass


@cli.command()
def dev():
    hypercorn_main(
        [
            "backend.app:asgi",
            "--bind",
            f"localhost:{env.str('VITE_BACKEND_PORT')}",
            "--reload",
            "--debug",
        ]
    )


if __name__ == "__main__":
    cli()
