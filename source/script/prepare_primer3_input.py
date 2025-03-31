from pathlib import Path
import sys, yaml
import pandas as pd

def prepare_primer3_input(file_list:list[Path], output_dir: str,report_file:str) -> None:

    report_file = Path(report_file).resolve()
    output_dir = Path(output_dir).resolve()

    with open("config/config.yaml", "r") as infile:
        config_yaml = yaml.safe_load(infile)
    
    analysis_dir:Path = Path(config_yaml["analysis_dir"]).resolve()

    primer3_settings:dict = config_yaml["primer3_settings"]
    formated_settings:str ="\n".join([f'{key}={value}' for key, value in primer3_settings.items()])

    #targeted_areas_fasta:list[Path] = file_list.rglob("*.fasta")

    #print(targeted_areas_fasta)
    primer_info:list = []

    for fasta_file in file_list :

        output_path = output_dir / fasta_file.stem 
        output_path.mkdir(parents=True, exist_ok=True) 
        
        sequences:dict = {}
        index = 0
        
        with open(fasta_file, "r") as infile:

            for line in infile :

                line = line.strip()

                if line.startswith(">") :
 
                    index +=1
                    key = f'{index}_{fasta_file.stem};{line.lstrip(">")}'
                    sequences[key] = ""

                if line.isalpha():
                    sequences[key] = line
                
                primer3_script_path:Path = output_path / f"{index}_{fasta_file.stem}.txt"

                with open(primer3_script_path,"w") as outfile :

                    outfile.write(f"""SEQUENCE_TEMPLATE={sequences[key]}
{formated_settings}
=
""")
        primer_info.append(sequences)

        flag_file = output_path / "flag.done"
        with open(flag_file,"w") as infile :
                pass
    
    primer_info = [key.split(";") for dic in primer_info for key in dic ]
    
    summary_file = pd.DataFrame.from_records(primer_info)
    summary_file.reset_index(drop=True, inplace=True)

    summary_file.to_csv(report_file)

if __name__ == "__main__":

    genome_dir, output_dir = sys.argv[1], sys.argv[2]

    prepare_primer3_input(genome_dir, output_dir)
