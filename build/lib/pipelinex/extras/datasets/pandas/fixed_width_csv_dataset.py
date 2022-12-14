from importlib.util import find_spec

import pandas as pd

if find_spec("kedro"):
    from kedro.extras.datasets.pandas.csv_dataset import CSVDataSet
else:
    from .csv_local import CSVLocalDataSet as CSVDataSet


class FixedWidthCSVDataSet(CSVDataSet):
    """``CSVDataSet`` loads/saves data from/to a CSV file using an underlying
    filesystem (e.g.: local, S3, GCS). It uses pandas to handle the CSV file.
    """

    def __init__(
        self,
        *args,
        enable_fixed_width: bool = True,
        num_decimal_places: int = 9,
        **kwargs
    ) -> None:
        """Creates a ``FixedWidthCSVDataSet`` pointing to a concrete CSV file
        on a specific filesystem.
        Args:
            filepath: Filepath in POSIX format to a CSV file prefixed with a protocol like `s3://`.
                If prefix is not provided, `file` protocol (local filesystem) will be used.
                The prefix should be any protocol supported by ``fsspec``.
                Note: `http(s)` doesn't support versioning.
            load_args: Pandas options for loading CSV files.
                Here you can find all available arguments:
                https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html
                All defaults are preserved.
            save_args: Pandas options for saving CSV files.
                Here you can find all available arguments:
                https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_csv.html
                All defaults are preserved, but "index", which is set to False.
            version: If specified, should be an instance of
                ``kedro.io.core.Version``. If its ``load`` attribute is
                None, the latest version will be loaded. If its ``save``
                attribute is None, save version will be autogenerated.
            credentials: Credentials required to get access to the underlying filesystem.
                E.g. for ``GCSFileSystem`` it should look like `{"token": None}`.
            fs_args: Extra arguments to pass into underlying filesystem class constructor
                (e.g. `{"project": "my-project"}` for ``GCSFileSystem``), as well as
                to pass to the filesystem's `open` method through nested keys
                `open_args_load` and `open_args_save`.
                Here you can find all available arguments for `open`:
                https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.spec.AbstractFileSystem.open
                All defaults are preserved, except `mode`, which is set to `r` when loading
                and to `w` when saving.
            enable_fixed_width: Save to a CSV file with each column width fixed among
                all the rows and theheader to improve readability for humans.
            num_decimal_places: Number of decimal places for float values to save.
        """
        self.enable_fixed_width = enable_fixed_width
        self.num_decimal_places = num_decimal_places
        super().__init__(*args, **kwargs)

    def _save(self, data: pd.DataFrame) -> None:
        if self.enable_fixed_width:
            fix_width(data, num_decimal_places=self.num_decimal_places)
        return super()._save(data)


def fix_width(df, num_decimal_places=9):
    import numpy as np

    for col in df.select_dtypes(["float64", "float32", "float16"]):
        sr = df[col].apply("{:.0f}".format)
        d = sr.astype(str).str.len().max()
        df[col] = df[col].apply(
            ("{:" + str(d) + "." + str(num_decimal_places) + "f}").format
        )

    for col in df.select_dtypes(["int64", "int32", "int16", "int8"]):
        sr = df[col].apply("{}".format)
        d = sr.astype(str).str.len().max()
        df[col] = df[col].apply(("{:" + str(d) + "d}").format)

    for col in df.select_dtypes(["object"]):
        df[col] = df[col].astype(str)
        d = df[col].str.len().max()
        df[col] = df[col].apply(("{:" + str(d) + "s}").format)

    for col in list(df.columns):
        df[col] = df[col].astype(str)
        w = max(df[col].str.len().max(), len(col))
        f = (" {:" + str(w) + "s} ").format
        df[col] = df[col].apply(f)
        df.rename(columns={col: f(col)}, inplace=True)
