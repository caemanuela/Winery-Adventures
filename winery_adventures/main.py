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
    """Esegue la pipeline completa di analisi aziendale:
    
    Trasformazione dei dati grezzi.
    Calcolo degli indicatori HPC (stress score).
    Orchestrazione ed eventuale logging su WandB."""
    raw_data_path = Path(raw_data_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Inizializza le componenti della pipeline
    transformer = WineryTransformer()
    computations = WineryHPCComputations()

    # 2. Inizializza la pipeline principale
    pipeline = WineryPipeline(
        transformer=transformer,
        computations=computations,
        wandb_config=wandb_config,
    )

    # 3. Esegue la pipeline e salva i risultati
    results = pipeline.run(input_path=raw_data_path, output_dir=output_dir)

    return results


if __name__ == "main":
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
