from dataclasses import dataclass
from typing import List, Optional

from pandas import DataFrame


@dataclass
class Measurement:
    resource: str
    URL: str
    page_number: int
    page_size: int
    number_of_records: int
    elapsed_time: int
    http_status_code: int

    @staticmethod
    def to_DataFrame(
        measurements: List["Measurement"], df: Optional[DataFrame] = None
    ) -> DataFrame:
        """
        Converts or appends a list of Measurements to a DataFrame.

        Parameters
        ----------
        measurements: List[Measurement]
            A list of Measurements that will be loaded into the DataFrame
        df: DataFrame
            An optional initial DataFrame

        Returns
        -------
        DataFrame
            A new DataFrame, or the modified Dataframe if `df` is provided
        """
        if len(measurements) == 0:
            raise ValueError("Cannot accept an empty list")

        if df is None:
            df = DataFrame(data=measurements)
            df.rename(
                {
                    "resource": "Resource",
                    "page_number": "PageNumber",
                    "page_size": "PageSize",
                    "number_of_records": "NumberOfRecords",
                    "elapsed_time": "ElapsedTime",
                    "http_status_code": "StatusCode",
                },
                inplace=True,
                axis=1,
            )

        df.sort_values(by=["Resource", "PageNumber"], inplace=True)

        return df
