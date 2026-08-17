from pathlib import Path
from typing import Any, Dict, Optional

from winery_adventures.computations import WineryHPCComputations
from winery_adventures.pipeline import WineryPipeline
from winery_adventures.transformations import WineryTransformer


def run_full_pipeline(
    raw_data_path: Path | str,
    output_dir: Path | str,
    wandb_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Runs the complete business analysis pipeline:

    Raw data transformation.
    Computation of HPC indicators (stress score).
    Orchestration and optional WandB logging.
    """
    raw_data_path = Path(raw_data_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Initialize pipeline components
    transformer = WineryTransformer()
    computations = WineryHPCComputations()

    # 2. Initialize main pipeline
    pipeline = WineryPipeline(
        transformer=transformer,
        computations=computations,
        wandb_config=wandb_config,
    )

    # 3. Run the pipeline and save results
    results = pipeline.run(input_path=raw_data_path, output_dir=output_dir)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Winery Adventures CLI Runner")
    parser.add_argument(
        "--data-path",
        type=str,
        required=True,
        help="Path to the raw input data directory/file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Directory where output artifacts will be saved",
    )
    args = parser.parse_args()

    run_full_pipeline(raw_data_path=args.data_path, output_dir=args.output_dir)