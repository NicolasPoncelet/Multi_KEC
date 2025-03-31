from pathlib import Path
import sys
import pandas as pd
import re

def get_primer_info(primer_file: Path) -> dict:

    primer_name = primer_file.stem
    genus_name = primer_file.parent.name

    primer_info = {}  
    common_info = {"Genus":genus_name,
                "Primer_file_name": primer_name} 

    with open(primer_file, "r") as infile:

        for line in [line for line in infile if line != "=" ]:

            key, value = line.split("=")

            key = key.strip()
            value = value.strip()

            match = re.search(r'PRIMER_.*_(\d+)(?:_|$)', key)

            if match:

                primer_id = match.group(1)
                primer_key = f"Primer_{primer_id}"

                if primer_key not in primer_info:

                    primer_info[primer_key] = {}

                remove_pattern = f'_{primer_id}'
                formated_key = key.replace(remove_pattern,"")

                primer_info[primer_key][formated_key] = value

            else:

                common_info[key] = value

    for d in primer_info.values():

        d.update(common_info)

    list_of_primers = []

    for primer_key, single_primer_dict in primer_info.items():
        flattend_dic = {"Primer": primer_key}
        flattend_dic.update(single_primer_dict)
        list_of_primers.append(flattend_dic)

    return list_of_primers

def compile_primer_info(primer_dir:str,output_file:str) -> None :

    primer_path:Path = Path(primer_dir).resolve()
    output_path:Path = Path(output_file).resolve()

    primers_to_compile:list[Path] = list(primer_path.rglob("*.primer"))

    compiled_infos:list[dict] = []

    for primer in primers_to_compile :

        current_dic = get_primer_info(primer)

        compiled_infos.extend(current_dic)

    primer_df:pd.DataFrame = pd.DataFrame.from_dict(compiled_infos)
    primer_df.to_csv(output_path)

# test = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/4_Primer3_output"
# output = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/0_Final/primer_summary.csv"
# compile_primer_info(test,output)

# primer_file = Path("/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/4_Primer3_output/Bipolaris/1_Bipolaris.primer")


