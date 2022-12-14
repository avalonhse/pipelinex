from pathlib import Path
from typing import Any, Dict

import pandas as pd

from ..core import AbstractVersionedDataSet, DataSetError, Version


class PandasProfilingDataSet(AbstractVersionedDataSet):
    """``PandasProfilingDataSet`` is an ``AbstractVersionedDataSet`` to generate
    pandas profiling report.
    See https://github.com/pandas-profiling/pandas-profiling for details.
    """

    DEFAULT_SAVE_ARGS = dict()  # type: Dict[str, Any]

    def __init__(
        self,
        filepath: str,
        save_args: Dict[str, Any] = None,
        sample_args: Dict[str, Any] = None,
        version: Version = None,
    ) -> None:
        """Creates a new instance of ``PandasProfilingDataSet`` pointing to a concrete
        filepath.

        Args:
            filepath: path to a local yaml file.
            save_args: Arguments passed on to ``df.profile_report`` such as title.
                See https://pandas-profiling.github.io/pandas-profiling/docs/ for details.
                See https://github.com/pandas-profiling/pandas-profiling/blob/master/pandas_profiling/config_default.yaml for default values.
            sample_args: Arguments passed on to ``df.sample``.
                See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sample.html for details.
            version: If specified, should be an instance of
                ``kedro.io.core.Version``. If its ``load`` attribute is
                None, the latest version will be loaded. If its ``save``
                attribute is None, save version will be autogenerated.

        """
        super().__init__(
            filepath=Path(filepath), version=version, exists_function=self._exists
        )
        self._load_args = {}
        self._save_args = save_args
        self._sample_args = sample_args

    def _describe(self) -> Dict[str, Any]:
        return dict(
            filepath=self._filepath,
            save_args=self._save_args,
            sampling_args=self._sample_args,
            version=self._version,
        )

    def _load(self) -> Any:
        """loading is not supported."""
        return None

    def _save(self, data: pd.DataFrame) -> None:
        save_path = Path(self._get_save_path())
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if self._sample_args is not None:
            data = data.sample(**self._sample_args)
        profile = data.profile_report(**self._save_args)
        profile.to_file(output_file=save_path)

        load_path = Path(self._get_load_path())
        self._check_paths_consistency(load_path.absolute(), save_path.absolute())

    def _exists(self) -> bool:
        try:
            path = self._get_load_path()
        except DataSetError:
            return False
        return Path(path).is_file()
