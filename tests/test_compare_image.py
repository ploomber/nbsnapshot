from unittest.mock import ANY

import pytest

from nbsnapshot import compare, exceptions
from conftest import _make_notebook_with_cells, _load_json


def test_compare_creates_history(tmp_empty, capsys):
    _make_notebook_with_cells([
        ('plt.plot([1, 2, 3])', 'plot'),
    ],
                              top_cell="""
import matplotlib.pyplot as plt
""")

    compare.main('nb.ipynb')

    history = _load_json('nb.json')

    assert history == [{'plot': {'mimetype': 'image/png', 'data': ANY}}]


def test_compare_image(tmp_empty, capsys):
    _make_notebook_with_cells([
        ('plt.plot([1, 2, 3])', 'plot'),
    ],
                              top_cell="""
import matplotlib.pyplot as plt
""")

    compare.main('nb.ipynb')

    _make_notebook_with_cells([
        ('plt.plot([3, 2, 1])', 'plot'),
    ],
                              top_cell="""
import matplotlib.pyplot as plt
""")

    compare.main('nb.ipynb')

    _make_notebook_with_cells([
        ('plt.plot([1, 2, 3])', 'plot'),
    ],
                              top_cell="""
import matplotlib.pyplot as plt
""")

    compare.main('nb.ipynb')

    _make_notebook_with_cells([
        ('plt.plot([3, 1, 2])', 'plot'),
    ],
                              top_cell="""
import matplotlib.pyplot as plt
""")

    with pytest.raises(exceptions.SnapshotTestFailure) as excinfo:
        compare.main('nb.ipynb')

    captured = capsys.readouterr()
    assert "Testing 'plot' - FAIL!" in captured.out
    assert 'Some tests failed.' == str(excinfo.value)


def test_error_if_different_sizes(tmp_empty, capsys):
    make_plot_cell = """
import matplotlib.pyplot as plt

def make_plot(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    _ = ax.plot([1, 2, 3])
"""

    _make_notebook_with_cells([
        ('make_plot(1, 1)', 'plot'),
    ],
                              top_cell=make_plot_cell)

    compare.main('nb.ipynb')

    _make_notebook_with_cells([
        ('make_plot(2, 2)', 'plot'),
    ],
                              top_cell=make_plot_cell)

    with pytest.raises(exceptions.SnapshotTestFailure) as excinfo:
        compare.main('nb.ipynb')

    captured = capsys.readouterr()
    assert "Testing 'plot' - FAIL!" in captured.out
    assert 'Some tests failed.' == str(excinfo.value)
