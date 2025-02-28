from pathlib import Path
import sys, yaml

def prepare_primer3_input(input_dir: str, output_dir: str) -> None:

    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()

    with open("../config/config.yaml", "r") as infile:
        config_yaml = yaml.safe_load(infile)

    primer3_settings:dict = config_yaml["primer3_settings"]
    formated_settings:str ="\n".join([f'{key}={value}' for key, value in primer3_settings.items()])

    targeted_areas_fasta:list[Path] = list(input_dir.rglob("*.fasta")) 

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
    
    flag_file = output_path / "flag.done"
    with open(flag_file,"w") as infile :
            pass

if __name__ == "__main__":

    genome_dir, output_dir = sys.argv[1], sys.argv[2]

    # genome_dir = "/home/nponcelet/Documents/03-Script/00_Projet_Perso/02_Bioinfo/47_Multi_KEC/Test_data/Output/2_KEC_output"
    # output_dir = "."

    prepare_primer3_input(genome_dir, output_dir)
