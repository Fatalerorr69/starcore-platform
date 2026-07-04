import typer

app = typer.Typer()


@app.command()
def version():
    print("STARCORE Platform 0.1.0-dev")


@app.command()
def health():
    print("System OK")


if __name__ == "__main__":
    app()
