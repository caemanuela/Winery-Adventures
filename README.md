# Winery Adventures

[Italiano](#versione-italiana) | [English](#english-version)

## Versione italiana

Winery Adventures è un progetto di analisi di dati provenienti da sensori utilizzati durante la fermentazione del vino. Il sistema elabora dati relativi a temperatura, pH e volume e calcola un indice di stress della fermentazione.

Il progetto combina programmazione a oggetti, trasformazione dei dati e tecniche di High-Performance Computing (HPC) per analizzare i dati e ridurre i tempi di calcolo.

## Funzionalità principali

- **Pipeline di elaborazione:** le diverse operazioni di trasformazione e analisi sono organizzate in una pipeline composta da più analyzer.
- **Trasformazione dei dati:** Polars viene utilizzato per calcolare statistiche per cisterna, informazioni relative ai vitigni e deviazioni dalla temperatura di riferimento.
- **Calcolo HPC:** il calcolo dello stress utilizza Numba per la compilazione JIT e Joblib per distribuire l'elaborazione tra più core.
- **Tracciamento dei risultati:** il progetto può utilizzare Weights & Biases (WandB) per registrare lo `stress_score`.
- **Documentazione:** la struttura e i principali componenti del progetto sono documentati con Sphinx e diagrammi UML.

## Tecnologie utilizzate

- **Gestione dell'ambiente e delle dipendenze:** uv
- **Data processing:** Polars, NumPy
- **HPC e parallelizzazione:** Numba, Joblib
- **Experiment tracking:** Weights & Biases
- **Testing:** Pytest
- **Code quality:** Ruff, Mypy
- **Documentazione:** Sphinx

## Prerequisiti

Prima di installare il progetto, assicurarsi di avere installato **Python 3.11 o 3.12** e **uv**, utilizzato per la gestione dell'ambiente virtuale e delle dipendenze.

Se `uv` non è già installato, è possibile seguire le istruzioni nella [documentazione ufficiale di uv](https://docs.astral.sh/uv/getting-started/installation/).

## Installazione

Clonare il repository e spostarsi nella directory del progetto:

```bash
git clone https://github.com/caemanuela/winery-adventures.git
cd winery-adventures
```

Sincronizzare l'ambiente con `uv`:

```bash
uv sync --all-groups
```

Questo installa le dipendenze del progetto nell'ambiente virtuale.

## Generazione dei dati

Il progetto include uno script per generare un dataset di sensori più grande, utile soprattutto per i test delle prestazioni:

```bash
uv run python data_generator.py
```

I dataset di grandi dimensioni generati dallo script non sono inclusi nel repository.

## Utilizzo della pipeline

La pipeline può essere eseguita dalla riga di comando specificando il dataset dei sensori:

```bash
uv run python winery_adventures/main.py --input-csv data/full_sensors.tsv
```

È possibile specificare anche il file con le informazioni sulle cisterne:

```bash
uv run python winery_adventures/main.py \
    --input-csv data/full_sensors.tsv \
    --tank-info-csv data/tank_info.tsv
```

Se `--output-csv` non viene specificato, il risultato viene salvato in `results.csv`.

È inoltre possibile specificare il nome del progetto WandB con `--project-name`.

## HPC e benchmark

Il calcolo dello stress confronta le diverse rilevazioni appartenenti alla stessa cisterna, con complessità `O(n²)`. Per questo motivo, il progetto utilizza Numba e Joblib per ridurre i tempi di esecuzione.

I benchmark permettono di confrontare:

- l'implementazione in Python puro con quella compilata con Numba;
- i tempi di esecuzione di Joblib utilizzando un numero diverso di core.

Per eseguire i benchmark:

```bash
uv run python benchmark.py
```

I grafici dei benchmark possono essere generati con:

```bash
uv run python visualization_generator.py
```

I risultati vengono utilizzati per valutare l'effetto della compilazione JIT e della parallelizzazione sul tempo di esecuzione.

## Weights & Biases

La pipeline può registrare lo `stress_score` su Weights & Biases.

Prima di eseguire la pipeline con il logging abilitato, è necessario autenticarsi:

```bash
uv run wandb login
```

Successivamente è possibile eseguire la pipeline con il logging attivo.

## Testing e code quality

Il progetto include unit test e acceptance test. I principali controlli possono essere eseguiti con un unico comando:

```bash
uv run python run_checks.py
```

Lo script esegue in sequenza:

1. controllo della formattazione con Ruff;
2. controllo del codice con Ruff;
3. type checking con Mypy;
4. test con Pytest e calcolo della coverage.

La configurazione di Pytest genera anche i report di coverage e i report XML/JUnit utilizzati dalla pipeline di CI.

Gli stessi controlli vengono eseguiti automaticamente tramite GitHub Actions quando viene effettuato un push o aperta una Pull Request verso `main`.

## Documentazione

La documentazione tecnica viene generata con Sphinx a partire dalle docstring del codice.

Per generarla:

```bash
uv run sphinx-build -b html docs docs/build/html
```

La documentazione HTML viene creata nella directory `docs/build/html`.

Il progetto contiene inoltre i diagrammi UML relativi alla struttura e al funzionamento del sistema nella directory `docs/uml-diagrams/`.

## Struttura del progetto

```
winery-adventures/
├── winery_adventures/
│   ├── base.py
│   ├── computations.py
│   ├── transformations.py
│   ├── pipeline.py
│   └── main.py
├── tests/
│   ├── unit/
│   └── acceptance/
├── data/
├── docs/
│   ├── uml/
│   ├── data_visualization/
│   └── reports/
├── benchmark.py
├── visualization_generator.py
├── data_generator.py
├── run_checks.py
└── pyproject.toml
```

---

Università degli Studi di Cagliari, CdL Informatica Applicata e Data Analytics

Ingegneria del Software, 2026

**Team:** Emanuela Cannas, Giada Orrù

## English version

Winery Adventures is a data analysis project based on sensor readings collected during wine fermentation. The system processes data such as temperature, pH, and volume and calculates a fermentation stress score.

The project combines object-oriented programming, data processing, and High-Performance Computing (HPC) techniques to analyse the data and reduce computation time.

## Main features

- **Processing pipeline:** the different transformation and analysis steps are organized into a pipeline made up of several analyzers.
- **Data transformation:** Polars is used to calculate tank-level statistics, grape variety information, and deviations from the reference fermentation temperature.
- **HPC computation:** Numba is used for JIT compilation, while Joblib is used to distribute computations across multiple CPU cores.
- **Experiment tracking:** the project can use Weights & Biases (WandB) to log the `stress_score`.
- **Documentation:** the main components and structure of the project are documented with Sphinx and UML diagrams.

## Technologies

- **Environment and dependency management:** uv
- **Data processing:** Polars, NumPy
- **HPC and parallel processing:** Numba, Joblib
- **Experiment tracking:** Weights & Biases
- **Testing:** Pytest
- **Code quality:** Ruff, Mypy
- **Documentation:** Sphinx

## Prerequisites

Before installing the project, make sure that **Python 3.11 or 3.12** and **uv** are installed. The project uses `uv` to manage the virtual environment and dependencies.

If `uv` is not already installed, follow the instructions in the [official uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

## Installation

Clone the repository and move into the project directory:

```bash
git clone https://github.com/caemanuela/winery-adventures.git
cd winery-adventures
```

Sync the project environment with `uv`:

```bash
uv sync --all-groups
```

This installs the project dependencies in the virtual environment.

## Data generation

The project includes a script for generating a larger sensor dataset, mainly for performance testing:

```bash
uv run python data_generator.py
```

The large datasets generated by the script are not included in the repository.

## Running the pipeline

The pipeline can be run from the command line by specifying the sensor dataset:

```bash
uv run python winery_adventures/main.py --input-csv data/full_sensors.tsv
```

A tank metadata file can also be provided:

```bash
uv run python winery_adventures/main.py \
    --input-csv data/full_sensors.tsv \
    --tank-info-csv data/tank_info.tsv
```

If `--output-csv` is not specified, the processed data is saved to `results.csv`.

The WandB project name can also be specified using `--project-name`.

## HPC and benchmarks

The stress calculation compares the different sensor readings belonging to the same tank, resulting in `O(n²)` complexity. Numba and Joblib are therefore used to improve the execution time.

The benchmark scripts compare:

- the pure Python implementation with the Numba implementation;
- Joblib execution using different numbers of CPU cores.

To run the benchmarks:

```bash
uv run python benchmark.py
```

The benchmark plots can be generated with:

```bash
uv run python visualization_generator.py
```

The results can then be used to evaluate the effect of JIT compilation and parallel processing on execution time.

## Weights & Biases

The pipeline can log the `stress_score` to Weights & Biases.

Before running the pipeline with logging enabled, authenticate with:

```bash
uv run wandb login
```

The pipeline can then be run with WandB logging enabled.

## Testing and code quality

The project includes unit tests and acceptance tests. The main checks can be run with a single command:

```bash
uv run python run_checks.py
```

The script runs the following checks in sequence:

1. Ruff formatting check;
2. Ruff linting;
3. Mypy type checking;
4. Pytest and coverage.

Pytest is also configured to generate coverage and XML/JUnit reports used by the CI pipeline.

The same checks are run automatically through GitHub Actions when changes are pushed or a Pull Request is opened against `main`.

## Documentation

The technical documentation is generated with Sphinx from the project's docstrings.

To build it locally:

```bash
uv run sphinx-build -b html docs docs/build/html
```

The generated HTML documentation is placed in `docs/build/html`.

The project also includes UML diagrams describing the structure and behaviour of the system in `docs/uml-diagrams/`.

## Project structure

```
winery-adventures/
├── winery_adventures/
│   ├── base.py
│   ├── computations.py
│   ├── transformations.py
│   ├── pipeline.py
│   └── main.py
├── tests/
│   ├── unit/
│   └── acceptance/
├── data/
├── docs/
│   ├── uml/
│   ├── data_visualization/
│   └── reports/
├── benchmark.py
├── visualization_generator.py
├── data_generator.py
├── run_checks.py
└── pyproject.toml
```

---

Università degli Studi di Cagliari, BSc Applied Computer Science and Data Analytics

Software Engineering, 2026

**Team:** Emanuela Cannas, Giada Orrù