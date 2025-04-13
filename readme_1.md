# cMatch 

## Prerequisite

You need Python 3.9 and pip the package installer for Python [pip](https://pip.pypa.io/en/stable/)


## Install

Install a virtual environment if you want.

```
    $ python3 -m venv --prompt cmatch venv
    $ source ./venv/bin/activate
```

Install the dependencies

```
    $ pip install -r requirements.txt
```

## cMatch command line tool

run cmatch.py

```
    $ ./cmatch.py --help 
```


## Streamlit integration for visualisation

streamlit run cmatch.py [template file] [output file path ending in '.parquet'] [similarity threshold: float (0-1)] [overlap_tolerance: int (bases)] [sequence files (.seq or .fasta)]

Visualisation and storage has been developed for GFP constructs of 3 parts 
Further development is needed to generalise this.