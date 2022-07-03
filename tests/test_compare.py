import json
from pathlib import Path

import pytest
import nbformat
import papermill as pm

from nbsnapshot import compare, exceptions


def _load_json(path):
    return json.loads(Path(path).read_text())


def _new_cell(source, tag):
    return nbformat.v4.new_code_cell(source=source, metadata=dict(tags=[tag]))


def _make_notebook_with_cells(cells, name):
    nb = nbformat.v4.new_notebook()
    nb.cells = [_new_cell(source, tag) for source, tag in cells]
    path = f'{name}.ipynb'
    nbformat.write(nb, path)
    pm.execute_notebook(path, path, kernel_name='python3')


def test_compare_creates_history(tmp_empty):
    _make_notebook_with_cells([
        ('1 + 1', 'first'),
        ('2.2', 'second'),
        ('print(True)', 'third'),
    ], 'nb')

    compare.main('nb.ipynb')

    history = _load_json('nb.json')

    assert history == [{'first': 2, 'second': 2.2, 'third': True}]


def test_compare_appends_to_history(tmp_empty):
    _make_notebook_with_cells([
        ('1 + 1', 'first'),
        ('2 + 2', 'second'),
    ], 'nb')

    compare.main('nb.ipynb')
    compare.main('nb.ipynb')

    history = _load_json('nb.json')

    assert history == [
        {
            'first': 2,
            'second': 4
        },
        {
            'first': 2,
            'second': 4
        },
    ]


@pytest.mark.parametrize('source, error', [
    [
        '100 + 100',
        ("Test for cell 'first' failed: Current value is too high "
         "(200), expected a value between 2.0 and 2.0")
    ],
    [
        '-100 - 100',
        ("Test for cell 'first' failed: Current value is too low "
         "(-200), expected a value between 2.0 and 2.0")
    ],
])
def test_compare_raises_error_if_deviates(tmp_empty, source, error):
    _make_notebook_with_cells([
        ('1 + 1', 'first'),
        ('2 + 2', 'second'),
    ], 'nb')

    compare.main('nb.ipynb')
    compare.main('nb.ipynb')
    compare.main('nb.ipynb')

    _make_notebook_with_cells([
        (source, 'first'),
        ('2 + 2', 'second'),
    ], 'nb')

    with pytest.raises(exceptions.SnapshotTestFailed) as excinfo:
        compare.main('nb.ipynb')

    assert error in str(excinfo.value)


@pytest.mark.parametrize('cells, expected', [
    [
        [
            ('[1, 2, 3]', 'first'),
            ('dict(a=1, b=2)', 'second'),
        ],
        [],
    ],
    [
        [
            ('[1, 2, 3]', 'first'),
            ('1', 'second'),
        ],
        [dict(second=1)],
    ],
])
def test_compare_ignores_non_numbers(tmp_empty, cells, expected):
    _make_notebook_with_cells(cells, 'nb')

    compare.main('nb.ipynb')

    history = _load_json('nb.json')

    assert history == expected


def test_adds_new_cells_to_history(tmp_empty):
    _make_notebook_with_cells([
        ('1', 'first'),
    ], 'nb')

    compare.main('nb.ipynb')

    assert _load_json('nb.json') == [{'first': 1}]

    _make_notebook_with_cells([
        ('2', 'first'),
        ('3', 'second'),
    ], 'nb')
    compare.main('nb.ipynb')

    assert _load_json('nb.json') == [{'first': 1}, {'first': 2, 'second': 3}]
