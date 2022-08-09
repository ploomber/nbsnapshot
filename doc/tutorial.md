---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Tutorial

This tutorial will show you how to use `nbsnapshot`.

To indicate that you want `nbsnapshot` to test a cell's output, you need to add a tag to the cell with any name ([see here](https://jupyterbook.org/en/stable/content/metadata.html) to learn how to add tags to cells). Then, when testing a notebook, `nbsnapshot` will create a JSON file and append the results.

Let's create a fake history to simulate that we ran a notebook 10 times. The fake cell will create random values drawn from a normal distribution centered at `10`:

```{code-cell} ipython3
import json
from pathlib import Path
import urllib.request

import numpy as np
import pandas as pd

from nbsnapshot import compare
from nbsnapshot.exceptions import SnapshotTestFailure

def create_fake_history(mean):
    """Creates a fake notebook history
    """
    history = [dict(metric=x) for x in np.random.normal(loc=mean, size=50)]
    _ = Path('constant.json').write_text(json.dumps(history))

def plot_history():
    """Plots records stored in notebook history
    """
    history = pd.read_json('constant.json')
    history['metric'].plot(kind='density')

# download example notebook
_ = urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/nbsnapshot/main/examples/constant.ipynb", "constant.ipynb")
```

```{code-cell} ipython3
create_fake_history(mean=10)
plot_history()
```

Let's now run the sample notebook (`constant.ipynb`), this notebook only contains a cell that prints the number 10. Since this number is within the boundaries of our fake history, the test passes:

```{code-cell} ipython3
try:
    compare.main('constant.ipynb')
except SnapshotTestFailure as e:
    print(e)
```

Now, overwrite the existing history, replace it with a simulation of numbers drawn from a normal distribution centered at 0:

```{code-cell} ipython3
create_fake_history(mean=0)
plot_history()
```

Run the notebook again. This time, the value in the notebook (10) deviates too much from the history, hence, the test fails:

```{code-cell} ipython3
try:
    compare.main('constant.ipynb')
except SnapshotTestFailure as e:
    print(e)
```
