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

# Use case: ML re-training

You can use `nbsnapshot` to monitor ML re-training jobs, to get alerted when the training performance is unexpected.

Let's download a notebook that train a classifier:

```{code-cell} ipython3
from pathlib import Path
import urllib.request

import pandas as pd

from nbsnapshot import compare
from nbsnapshot.exceptions import SnapshotTestFailure

# download example notebook
_ = urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/nbsnapshot/main/examples/ml-classifier.ipynb", "ml-classifier.ipynb")

# delete history, if it exists
history = Path("ml-classifier.ipynb")

if history.exists():
    history.unlink()
```

Let's run  the notebook 10 times:

```{code-cell} ipython3
:tags: [hide-output]

for i in range(10):
    print(f'**Iteration {i}**')
    compare.main('ml-classifier.ipynb', run=True)
```

The tests passed, let's look at the history:

```{code-cell} ipython3
df = pd.read_json('ml-classifier.json')
```

```{code-cell} ipython3
df.plot(kind='density')
```

`nbsnapshot` uses 3 standard deviations from the mean as threshold. Let's compute the range:

```{code-cell} ipython3
mean, std = df['accuracy'].mean(), df['accuracy'].std()
low, high = mean - 3 * std, mean + 3 * std
```

```{code-cell} ipython3
print(f'Range: {low:.2f}, {high:.2f}')
```

If a new test falls outside this range, the test will fail.
