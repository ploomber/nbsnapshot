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

# Tutorial: testing images

Beginning in `nbsnapshot` 0.2, testing images is supported. Let's download a notebook that plots an image using matplotlib:

```{code-cell} ipython3
import urllib.request


from nbsnapshot import compare
from nbsnapshot.exceptions import SnapshotTestFailure

# download example notebook
_ = urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/nbsnapshot/main/examples/image.ipynb", "image.ipynb")
```

Run it once to generate the base image:

```{code-cell} ipython3
compare.main("image.ipynb", run=True)
```

Next call witll test the output:

```{code-cell} ipython3
compare.main("image.ipynb", run=True)
```
