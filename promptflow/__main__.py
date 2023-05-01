"""Main entry point for the promptflow application."""
import os
from promptflow.src.app import App
from promptflow.src.state import State
from promptflow.src.options import Options


def main():
    state = State()

    if os.path.exists("promptflow/options.json"):
        options = Options.parse_file("promptflow/options.json")
    else:
        options = Options()

    app = App(initial_state=state, options=options)

    app.run()


if __name__ == "__main__":
    main()
