from pathlib import Path
import pandas as pd
import numpy as np
import sys

def get_input_path(primer3_script_path:str) -> list[str]:
    """
    Generate paths for extracted sequences based on BLAST results.

    Parameters
    ----------
    report_path : str
        Path to the BLAST result report file.
    config : dict
        Configuration dictionary defining extraction mode and frame handling.

    Returns
    -------
    list[str]
        List of file paths corresponding to extracted sequences.
    """

    input_path:Path = Path(primer3_script_path)

    return list(str(path) for path in input_path.rglob("*.txt") )

# Test
if __name__ == "__main__":

    input_dir = sys.argv[1]

    get_input_path(input_dir)
