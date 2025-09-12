from typing import List

from pandas import DataFrame, Series

from edfi_paging_test.reporter.paging_measurement import PagingMeasurement


class PaggingRequestLogger:

    def __init__(self):
        self.request_log: List[PagingMeasurement] = []

    def log_request(
        self,
        resource: str,
        base_url: str,
        page: int,
        page_size: int,
        number_of_records: int,
        elapsed: float,
        status_code: int,
    ) -> None:
        m = PagingMeasurement(
            resource,
            base_url,
            page,
            page_size,
            number_of_records,
            elapsed,
            status_code,
        )

        self.request_log.append(m)

    def get_DataFrame(self) -> DataFrame:
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
        if len(self.request_log) == 0:
            raise RuntimeError(
                "No measurements have been captured, therefore cannot create a DataFrame"
            )

        df = DataFrame(data=self.request_log)
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

    def get_statistics(self):
        summary = self.get_DataFrame()

        # Need multiple columns in order to perform three different aggregations
        summary["MeanTime"] = summary["ElapsedTime"]
        summary["StDeviation"] = summary["ElapsedTime"]

        # This is a fascinating capability. Found mention in Medium article,
        # though not at all clear from the Pandas documentation. Type check
        # does not like it, because not covered in the type stub
        summary = summary.groupby(by=["Resource", "PageSize"], as_index=False).apply(
            lambda s: Series(
                {
                    "NumberOfPages": s[s["StatusCode"] < 400]["PageNumber"].count(),
                    "NumberOfRecords": s["NumberOfRecords"].sum(),
                    "TotalTime": s["ElapsedTime"].sum(),
                    "MeanTime": s["MeanTime"].mean(),
                    # "Unbiased" estimate of standard deviation for a sample
                    # (ddof=1, panda's default). Equivalent of Excel STDEV.S()
                    "StDeviation": s["StDeviation"].std().round(6),  # type: ignore
                    "NumberOfErrors": s[(s["StatusCode"] >= 400)]["StatusCode"].count(),
                }
            )
        )  # type: ignore

        summary.fillna(value=0, inplace=True)

        return summary
