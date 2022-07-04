# nbsnapshot

CLI for doing snapshot testing on Jupyter notebooks. [Blog post here.](https://ploomber.io/blog/snapshot-testing/)

![header](header.png)

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
curl -O https://raw.githubusercontent.com/edublancas/nbsnapshot/main/examples/normal.ipynb
```

Then, run the notebook and test it (pass `--run` to run the notebook before doing the snapshot test):

```sh
# install dependencies
pip install matplotlib numpy pandas

# run test
nbsnapshot test normal.ipynb --run
```

*Note:* You'll need to run the command a few times to start generating the history. If you want to fail the test, modify the notebook and add replace the cell that contains `np.random.normal()` with the number `100`.