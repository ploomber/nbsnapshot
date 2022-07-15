import json
from pathlib import Path
import statistics

import click
import papermill as pm
from sklearn_evaluation import NotebookIntrospector

from nbsnapshot.exceptions import SnapshotTestFailure


def _remove_non_supported_types(record):
    clean = dict()
    show_warning = False

    for key, value in record.items():
        if isinstance(value, (int, float, bool)):
            clean[key] = value
        else:
            show_warning = True

    if show_warning:
        click.echo('Got unsupported data type, ignoring... '
                   '(only int, float and bool are supported)')

    return clean


# NOTE: we could store the history as metadata in the same ipynb
# this could even allow us to plot the history below each cell
class History:
    def __init__(self, path):
        if not path.exists():
            path.write_text(json.dumps([]))

        self._path = path
        self._data = _load_json(path)

    def __getitem__(self, key):
        return [
            data.get(key) for data in self._data if data.get(key) is not None
        ]

    def keys(self):
        keys = set()

        for data in self._data:
            keys = keys | set(data.keys())

        return list(keys)

    def append(self, record):
        # TODO: add _timestamp
        record_clean = _remove_non_supported_types(record)

        if record_clean:
            self._data.append(record_clean)
            Path(self._path).write_text(json.dumps(self._data))

    def __len__(self):
        return len(self._data)

    def compare(self, key):
        stored = self[key]

        # we need at least two observations to compute standard deviation
        # plus the observation to compare
        len_ = len(stored)

        # TODO: add a CLI argument to control the minimum observations
        # to start testing
        if len_ < 3:
            if 2 - len_:
                click.echo(
                    f'Added {key!r} to history, 1 more needed for testing...')
            else:
                click.echo(f'Added {key!r} to history, next call '
                           'will start testing...')

            # skip the rest of the function
            return True

        # TODO: add a comparing function depending on the type
        # int/float and bool

        # ignore the last one since that's the same as the value
        stdev = statistics.stdev(stored[:-1])
        mean = statistics.mean(stored[:-1])
        low, high = mean - 3 * stdev, mean + 3 * stdev

        # last value is the one we'll use for comparison
        value = stored[-1]

        success = True

        if value < low:
            success = False
            click.secho(
                f"Testing {key!r} - FAIL! "
                "Value is too low "
                f"({value}), expected one "
                f"between {low:.2f} and {high:.2f}",
                fg='red')
        elif value > high:
            success = False
            click.secho(
                f"Testing {key!r} - FAIL! "
                "Value is too high "
                f"({value}), expected one "
                f"between {low:.2f} and {high:.2f}",
                fg='red')
        else:
            click.secho(f'Testing: {key!r} - OK!', fg='green')

        return success


def _load_json(path):
    return json.loads(Path(path).read_text())


def main(path_to_notebook: str, run: bool = False):
    if run:
        click.echo('Running notebook...')
        pm.execute_notebook(path_to_notebook,
                            path_to_notebook,
                            progress_bar=False)

    path_to_history = Path(path_to_notebook).with_suffix('.json')

    nb = NotebookIntrospector(path_to_notebook)
    data = nb.to_json_serializable()

    history = History(path_to_history)
    history.append(data)

    success = True

    # TODO: compare and add then record (add record even if compare fails)
    for key in data.keys():
        if not history.compare(key):
            success = False

    # NOTE: if the test fails, we should not add the last observation to
    # history, perhaps add a nother command "nbsnapshot" that only adds the
    # current values to the history without testing?
    if not success:
        raise SnapshotTestFailure('Some tests failed.')
