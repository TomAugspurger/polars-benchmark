from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

IoType: TypeAlias = Literal["skip", "parquet", "feather", "csv"]


class Paths(BaseSettings):
    answers: Path = Path("data/answers")
    tables: Path = Path("data/tables")

    timings: Path = Path("output/run")
    timings_filename: str = "timings.csv"

    plots: Path = Path("output/plot")

    model_config = SettingsConfigDict(
        env_prefix="path_", env_file=".env", extra="ignore"
    )


class LibCUDFEngineExecutorOptions(BaseSettings):
    ...

class DaskEngineExecutorOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="run_polars_dask_")
    parquet_blocksize: int = 1_000**3
    shuffle_method: Literal["rapidsmp", "tasks"] = "tasks"
    # bcast_join_limit": 2 if executor == "dask-cuda" else 32,
    # cardinality_factor: dict[str, float] = Field()
    # cardinality_factor": {
    #     "c_custkey": 0.05,
    #     "c_orderkey": 0.5,
    #     "l_orderkey": 1.0,
    # },

class DaskClusterOptions(BaseSettings):
    n_workers: int = 1
    """The number of workers to use for the Dask cluster."""
    dashboard_address: str = ":8585"
    """The address to use for the Dask dashboard."""
    protocol: Literal["ucx", "tcp"] = "ucx"
    """The protocol to use for the Dask cluster."""


class Run(BaseSettings):
    io_type: IoType = "parquet"

    log_timings: bool = False
    show_results: bool = False
    check_results: bool = False  # Only available for SCALE_FACTOR=1

    polars_show_plan: bool = False
    polars_eager: bool = False
    polars_streaming: bool = False
    polars_new_streaming: bool = False
    polars_gpu: bool = False  # Use GPU engine?
    polars_multi_gpu: bool = False  # Use multi-GPU engine?
    polars_gpu_executor: Literal["dask-experimental", "pylibcudf"] = "pylibcudf"
    polars_gpu_device: int = 0  # The GPU device to run on for polars GPU
    dask_cluster_options: DaskClusterOptions = Field(
        default_factory=DaskClusterOptions
    )

    @computed_field  # type: ignore[misc]
    @property
    def polars_gpu_executor_options(self) -> DaskEngineExecutorOptions | LibCUDFEngineExecutorOptions:
        if self.polars_multi_gpu:
            return DaskEngineExecutorOptions()
        else:
            return LibCUDFEngineExecutorOptions()

    # Which style of GPU memory resource to use
    # cuda -> cudaMalloc
    # cuda-pool -> Pool suballocator wrapped around cudaMalloc
    # managed -> cudaMallocManaged
    # managed-pool -> Pool suballocator wrapped around cudaMallocManaged
    # cuda-async -> cudaMallocAsync (comes with pool)
    # See https://docs.rapids.ai/api/rmm/stable/ for details on RMM memory resources
    use_rmm_mr: Literal[
        "cuda", "cuda-pool", "managed", "managed-pool", "cuda-async"
    ] = "cuda-async"

    modin_memory: int = 8_000_000_000  # Tune as needed for optimal performance

    spark_driver_memory: str = "2g"  # Tune as needed for optimal performance
    spark_executor_memory: str = "1g"  # Tune as needed for optimal performance
    spark_log_level: str = "ERROR"

    @computed_field  # type: ignore[misc]
    @property
    def include_io(self) -> bool:
        return self.io_type != "skip"

    model_config = SettingsConfigDict(
        env_prefix="run_", env_file=".env", extra="ignore"
    )


class Plot(BaseSettings):
    show: bool = False
    n_queries: int = 7
    y_limit: float | None = None

    model_config = SettingsConfigDict(
        env_prefix="plot_", env_file=".env", extra="ignore"
    )


class Settings(BaseSettings):
    scale_factor: float = 1.0

    paths: Paths = Paths()
    plot: Plot = Plot()
    run: Run = Run()

    @computed_field  # type: ignore[misc]
    @property
    def dataset_base_dir(self) -> Path:
        return self.paths.tables / f"scale-{self.scale_factor}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
