import pytest

from nbsnapshot import compare, exceptions

from conftest import _make_notebook_with_cells, _load_json


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
        ("Testing 'first' - FAIL! Value is too high "
         "(200.00), expected one between 2.00 and 2.00")
    ],
    [
        '-100 - 100',
        ("Testing 'first' - FAIL! Value is too low "
         "(-200.00), expected one between 2.00 and 2.00")
    ],
])
def test_compare_raises_error_if_deviates(tmp_empty, source, error, capsys):
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

    with pytest.raises(exceptions.SnapshotTestFailure) as excinfo:
        compare.main('nb.ipynb')

    captured = capsys.readouterr()
    assert error in captured.out
    assert 'Some tests failed.' == str(excinfo.value)
    # should not add the new record to the history
    assert len(_load_json('nb.json')) == 3


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
