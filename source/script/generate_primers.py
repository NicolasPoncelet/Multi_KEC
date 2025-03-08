from pathlib import Path
import pandas as pd
import sys
import yaml


def sort_primers(primer_path:Path) -> None :
    
    with open("config/config.yaml", "r") as infile:
        config_yaml = yaml.safe_load(infile)
    
    intput_dir = Path(config_yaml["analysis_dir"] / "4_Primer3_output").resolve()
    
    primers_range = config_yaml["primer3_settings"]["PRIMER_PRODUCT_SIZE_RANGE"]
    primers_range = [int(number) for number in primers_range.split("-")]

    current_value = primers_range[0]

    while current_value < primers_range[1] :

        new_dir:Path = intput_dir / current_value
        new_dir.mkdir(parents=True, exist_ok=True)
        current_value += primers_range[0]
