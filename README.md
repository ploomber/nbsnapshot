# nbsnapshot

CLI for doing snapshot testing on Jupyter notebooks.

## Install

```sh
pip install git+https://github.com/edublancas/nbsnapshot
```

## Example

See [examples/example.ipynb](examples/example.ipynb)

## Usage

First, [tag some cells](https://papermill.readthedocs.io/en/latest/usage-parameterize.html). 

Or, get a sample notebook:

```sh
```

Then, run the notebook and test it:

```sh
nbsnapshot test path/to/notebook.ipynb --run
```
