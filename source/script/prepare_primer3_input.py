from pathlib import Path
import sys, yaml
import pandas as pd

def prepare_primer3_input(input_dir: str, output_dir: str) -> None:

    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()

    with open("config/config.yaml", "r") as infile:
        config_yaml = yaml.safe_load(infile)
    
    analysis_dir:Path = Path(config_yaml["analysis_dir"]).resolve()

    primer3_settings:dict = config_yaml["primer3_settings"]
    formated_settings:str ="\n".join([f'{key}={value}' for key, value in primer3_settings.items()])

    targeted_areas_fasta:list[Path] = list(input_dir.rglob("*.fasta")) 
    primer_info:list = []

    for fasta_file in targeted_areas_fasta :

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

                if line.isalpha() :
                    sequences[key] = line.strip("\n")
                
                primer3_script_path:Path = output_path / f"{index}_{fasta_file.stem}.txt"

                with open(primer3_script_path,"w") as outfile :

                    outfile.write(f"""SEQUENCE_TEMPLATE={sequences[key]}{formated_settings}
=
""")
        primer_info.append(sequences)

        flag_file = output_path / "flag.done"
        with open(flag_file,"w") as infile :
                pass
    
    primer_info = [key.split(";") for dic in primer_info for key in dic ]
    
    summary_file = pd.DataFrame.from_records(primer_info)
    summary_file.reset_index(drop=True, inplace=True)

    print(summary_file)
    summary_file.to_csv(analysis_dir / "summary.csv")

# import yaml

# with open(Path("../config/config.yaml"), "r") as infile:
#     config_yaml = yaml.load(infile, Loader=yaml.SafeLoader)

# report_path = "/home/nponcelet/Documents/03-Script/00_Projet_Perso/02_Bioinfo/42_Multi_BLAST/Test_data/Output/BLAST_results/compiled_results.csv"
# report_path = Path(report_path)

# get_extracted_seqs(report_path,config_yaml)

if __name__ == "__main__":

    #genome_dir, output_dir = sys.argv[1], sys.argv[2]

    genome_dir = "/home/nponcelet/Documents/03-Script/00_Projet_Perso/02_Bioinfo/47_Multi_KEC/Test_data/Output/2_KEC_output"
    output_dir = "/home/nponcelet/Documents/03-Script/00_Projet_Perso/02_Bioinfo/47_Multi_KEC/Test_data/Output/3_Primer3_input"

    prepare_primer3_input(genome_dir, output_dir)
