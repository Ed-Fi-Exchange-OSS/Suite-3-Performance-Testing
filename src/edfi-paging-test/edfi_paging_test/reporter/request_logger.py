from typing import List

from pandas import DataFrame

from edfi_paging_test.reporter.measurement import Measurement

_request_log: List[Measurement] = []


def log_request(
    resource: str,
    base_url: str,
    page: int,
    page_size: int,
    number_of_records: int,
    elapsed: float,
    status_code: int,
) -> None:
    m = Measurement(
        resource,
        base_url,
        page,
        page_size,
        number_of_records,
        elapsed,
        status_code,
    )

    _request_log.append(m)


def get_DataFrame() -> DataFrame:
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
    if len(_request_log) == 0:
        raise RuntimeError(
            "No measurements have been captured, therefore cannot create a DataFrame"
        )

    df = DataFrame(data=_request_log)
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
