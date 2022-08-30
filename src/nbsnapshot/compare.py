import base64
from io import BytesIO
import json
from pathlib import Path
import statistics
from collections.abc import Mapping

import click
import papermill as pm
from ploomber_core.telemetry.telemetry import Telemetry
from sklearn_evaluation import NotebookIntrospector
from sklearn_evaluation.nb.NotebookIntrospector import _safe_literal_eval

from nbsnapshot import __version__
from nbsnapshot.exceptions import SnapshotTestFailure

telemetry = Telemetry(
    api_key="phc_P9SpSeypyPwxrMdFn2edOOEooQioF2axppyEeDwtMSP",
    package_name="nbsnapshot",
    version=__version__,
)


def _remove_non_supported_types(record):
    clean = dict()
    show_warning = False

    for key, value in record.items():
        if isinstance(value, (int, float, bool)):
            clean[key] = value
        elif isinstance(value, Image):
            clean[key] = value.to_json_serializable()
        else:
            show_warning = True

    if show_warning:
        click.echo(f'Got unsupported data type ({type(value).__name__}), '
                   'ignoring... (only int, float and bool are supported)')

    return clean


def _str2arr(data):
    from PIL import Image
    import numpy as np

    bytes_ = base64.b64decode(data)
    image = Image.open(BytesIO(bytes_))
    return np.array(image, dtype=np.float64)


def _mean_squared_error(image0, image1):
    import numpy as np
    return np.mean((image0 - image1)**2, dtype=np.float64)


def _compare_images(arrs):
    for image0, image1 in zip(arrs, arrs[1:]):
        yield _mean_squared_error(image0, image1)


def _can_test(stored, key, is_number, echo=True):
    minimum = 3 if is_number else 2
    # we need at least two observations to compute standard deviation
    # plus the observation to compare
    len_ = len(stored)

    # TODO: add a CLI argument to control the minimum observations
    # to start testing
    if len_ < minimum:
        if echo:
            needed = (minimum - 1) - len_
            if needed:
                click.echo(f'Added {key!r} to history, {needed} more '
                           'needed for testing...')
            else:
                click.echo(f'Added {key!r} to history, next call '
                           'will start testing...')

        # skip the rest of the function
        return False
    else:
        return True


def _equal_sizes(arrs, key):
    shapes = set(arr.shape for arr in arrs)
    same_size = len(shapes) == 1

    if same_size:
        return True
    else:
        click.secho(
            f'Testing {key!r} - FAIL! Images '
            f'with multiple sizes: {shapes}',
            fg='red')
        return False


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

    def compare(self, key, current):
        stored = self[key] + [current]

        # no history
        if not len(stored):
            return True

        if isinstance(stored[0], (int, float)):
            is_number = True
        elif isinstance(stored[0], Mapping):
            is_number = False
        else:
            click.secho(
                'Got unrecognized type of '
                f'data: {type(stored[0]).__name__}, ignoring...',
                fg='yellow')

            return True

        # check if we can test - numbers need 3, image need 2 obs
        can_test = _can_test(stored, key, is_number)

        if can_test:
            if is_number:
                return self._compare_numeric(stored, key)
            else:
                return self._compare_image(stored, key)
        else:
            return True

    def _compare_image(self, stored, key):
        arrs = [_str2arr(image['data']) for image in stored]
        equal_sizes = _equal_sizes(arrs, key)

        if not equal_sizes:
            return False

        errors = list(_compare_images(arrs))

        # check if we have enough errors to compare
        can_test = _can_test(errors, key, is_number=True, echo=False)

        if can_test:
            return self._compare_numeric(errors, key)
        else:
            # this means we only checked image size
            click.secho(f'Testing [image size]: {key!r} - OK!', fg='green')
            return True

    def _compare_numeric(self, stored, key):
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
                f"({value:.2f}), expected one "
                f"between {low:.2f} and {high:.2f}",
                fg='red')
        elif value > high:
            success = False
            click.secho(
                f"Testing {key!r} - FAIL! "
                "Value is too high "
                f"({value:.2f}), expected one "
                f"between {low:.2f} and {high:.2f}",
                fg='red')
        else:
            click.secho(f'Testing: {key!r} - OK!', fg='green')

        return success


def _load_json(path):
    return json.loads(Path(path).read_text())


class Image:

    def __init__(self, data):
        self._data = data

    def to_json_serializable(self):
        return dict(mimetype='image/png', data=self._data)


# modified from sklearn-evaluation's source code
def _parse_output(output, literal_eval):
    if 'image/png' in output:
        return Image(output['image/png'])
    elif 'text/plain' in output:
        out = output['text/plain']
        return out if not literal_eval else _safe_literal_eval(out,
                                                               to_df=False)


def _extract_data(path):
    nb = NotebookIntrospector(path)
    data = {
        k: _parse_output(
            v,
            literal_eval=True,
        )
        for k, v in nb.tag2output_raw.items()
    }

    return data


@telemetry.log_call('compare-main')
def main(path_to_notebook: str, run: bool = False):
    if run:
        click.echo('Running notebook...')
        pm.execute_notebook(path_to_notebook,
                            path_to_notebook,
                            progress_bar=False)

    path_to_history = Path(path_to_notebook).with_suffix('.json')

    data = _extract_data(path_to_notebook)

    history = History(path_to_history)

    success = True

    for key, value in data.items():
        if hasattr(value, 'to_json_serializable'):
            value = value.to_json_serializable()

        if not history.compare(key, value):
            success = False

    if not success:
        raise SnapshotTestFailure('Some tests failed.')
    else:
        history.append(data)
