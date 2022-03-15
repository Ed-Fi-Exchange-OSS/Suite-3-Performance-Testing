from pandas import DataFrame
from os import path, mkdir


def create_detail_csv(df: DataFrame, output_dir: str, run_name: str) -> None:
    if not path.exists(output_dir):
        mkdir(output_dir)

    file_path = path.join(output_dir, f"{run_name}.detail.csv")
    df.to_csv(file_path, index=False)

