(Development)=
# Development

## Development Environment

The current environment can be installed simply from the `requirements.txt` file. Install into a virtual environment if you want to keep your system clean.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

(Running)=
## Running

Promptflow can be run with Python from the commandline:

```bash
python promptflow/main.py
```

If you're having trouble ensure your `PYTHONPATH` is set correctly:

```bash
export PYTHONPATH=$PYTHONPATH:.
```

## Starting Point: Adding a Node

Creating a new [`Node`](Node) is a good starting point for understanding the codebase. Let's take a look at the [`RandomNumber`](RandomNumber) node:

```{literalinclude} ../promptflow/src/nodes/random_number.py
```

1. We import the necessary libraries, including the `Node` base class, aptly named `NodeBase`.

2. We create a new class, `RandomNumber`, that inherits from `NodeBase`.

    a. We can specify the color of the node by setting the `node_color` to a hex string. In this case, we inherit from the `monokai` color scheme.

    b. We set the default `min` and `max`. 

    c. We initialize the `OptionsPopup` to `None`; it will later be used to set `min` and `max` at runtime.

3. `run_subclass` is the most important function in the `Node` class. It is called when the node is run. In this case, we simply return a random number between `min` and `max`.

4. `edit_options` is called when the node is double-clicked. It opens the `OptionsPopup` and sets the `min` and `max` values. The main window waits until the popup is closed before continuing execution. Finally, we set the `min` and `max` values to the values in the popup.