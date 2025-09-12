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


def create_statistics_csv(statistics: Series, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "statistics.csv")
    statistics.to_csv(file_path, index=False)


def create_statistics_json(statistics: Series, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "statistics.json")

    # Apparently to_json is not in the type stub
    statistics.to_json(file_path, orient="records")  # type: ignore


def create_summary_json(df: DataFrame, output_dir: str, run_name: str) -> None:
    run_dir = path.join(output_dir, run_name)
    _create_if_not_exists(run_dir)

    file_path = path.join(run_dir, "summary.json")

    # Apparently to_json is not in the type stub
    df.to_json(file_path, orient="records")  # type: ignore
