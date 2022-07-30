import json
import os
from pathlib import Path

import papermill as pm
import nbformat
import pytest


@pytest.fixture
def tmp_empty(tmp_path):
    """
    Create temporary path using pytest native fixture,
    them move it, yield, and restore the original path
    """
    old = os.getcwd()
    os.chdir(str(tmp_path))
    yield str(Path(tmp_path).resolve())
    os.chdir(old)


def _load_json(path):
    return json.loads(Path(path).read_text())


def _new_cell(source, tag):
    return nbformat.v4.new_code_cell(source=source, metadata=dict(tags=[tag]))


def _make_notebook_with_cells(cells, name='nb', top_cell=None):
    nb = nbformat.v4.new_notebook()

    if top_cell:
        top = nbformat.v4.new_code_cell(source=top_cell)
        nb.cells = [top]
    else:
        nb.cells = []

    nb.cells.extend(_new_cell(source, tag) for source, tag in cells)
    path = f'{name}.ipynb'
    nbformat.write(nb, path)
    pm.execute_notebook(path, path, kernel_name='python3')
