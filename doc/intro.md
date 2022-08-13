---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# nbsnapshot

`nbsnapshot` tests Jupyter notebook by benchmarking outputs with historical values.

```{code-cell} ipython3
:tags: ["remove-cell"]
import tempfile, os, shutil, atexit

tmp = tempfile.mkdtemp()
os.chdir(tmp)

@atexit.register
def delete_tmp():
    shutil.rmtree(tmp)
```

Download a notebook:

```{code-cell} ipython3
import urllib.request
from pathlib import Path
```


```{code-cell} ipython3
from nbsnapshot import compare
```

```{code-cell} ipython3
# download example notebook
_ = urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/nbsnapshot/main/examples/normal.ipynb", "example.ipynb")
```


Run it a few times (two needed to start testing):

```{code-cell} ipython3
compare.main("example.ipynb", run=True)
compare.main("example.ipynb", run=True)
```

Next call witll test the output:


```{code-cell} ipython3
compare.main("example.ipynb", run=True)
```


