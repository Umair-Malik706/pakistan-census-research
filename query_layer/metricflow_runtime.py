from functools import lru_cache
from pathlib import Path
from typing import Sequence

from dbt_metricflow.cli.cli_configuration import CLIConfiguration
from metricflow.engine.metricflow_engine import MetricFlowQueryRequest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt"
DBT_PROFILES_DIR = Path.home() / ".dbt"


@lru_cache(maxsize=1)
def get_metricflow_config() -> CLIConfiguration:
    config = CLIConfiguration()

    config.setup(
        dbt_profiles_path=DBT_PROFILES_DIR,
        dbt_project_path=DBT_PROJECT_DIR,
        configure_file_logging=False,
    )

    return config


def run_metricflow_query(
    metric_names: Sequence[str],
    group_by_names: Sequence[str] | None = None,
    where_constraints: Sequence[str] | None = None,
    order_by_names: Sequence[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, str]]:
    config = get_metricflow_config()

    request = MetricFlowQueryRequest.create(
        saved_query_name=None,
        metric_names=metric_names,
        group_by_names=group_by_names,
        limit=limit,
        time_constraint_start=None,
        time_constraint_end=None,
        where_constraints=where_constraints,
        order_by_names=order_by_names,
    )

    result = config.mf.query(
        mf_request=request
    )

    dataframe = result.result_df

    if dataframe is None:
        return []

    rows = []

    for row in dataframe.rows:
        rows.append(
            {
                column: (
                    "" if value is None else str(value)
                )
                for column, value in zip(
                    dataframe.column_names,
                    row,
                )
            }
        )

    return rows