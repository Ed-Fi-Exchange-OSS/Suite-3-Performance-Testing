from pandas import DataFrame, Series
from os import path, makedirs


def _create_if_not_exists(directory: str) -> None:
    if not path.exists(directory):
        makedirs(directory)


def create_detail_csv(df: DataFrame, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "detail.csv")
    df.to_csv(file_path, index=False)


def create_detail_json(df: DataFrame, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "detail.json")

    # Apparently to_json is not in the type stub
    df.to_json(file_path, orient="records")  # type: ignore


def _calculate_statistics(df: DataFrame) -> DataFrame:
    summary = df.copy()

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


def create_statistics_csv(df: DataFrame, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "statistics.csv")
    _calculate_statistics(df).to_csv(file_path, index=False)


def create_statistics_json(df: DataFrame, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "statistics.json")

    # Apparently to_json is not in the type stub
    _calculate_statistics(df).to_json(file_path, orient="records")  # type: ignore


def create_summary_json(df: DataFrame, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "summary.json")

    # Apparently to_json is not in the type stub
    df.to_json(file_path, orient="records")  # type: ignore
