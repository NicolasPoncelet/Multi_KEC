from pathlib import Path
from itertools import product
import yaml
import pandas as pd
import shutil
def extract_fasta(metadata_file,output_dir) -> None :

    metadata_file:Path = Path(metadata_file).resolve() 

    output_path:Path = Path(output_dir).resolve()

    metadata:pd.DataFrame = pd.read_csv(metadata_file)

    trimmed_metadata:pd.DataFrame = metadata[["Genus","Primer_file_name","Primer", "PRIMER_LEFT_SEQUENCE", "PRIMER_RIGHT_SEQUENCE"]]

    for idx, row in trimmed_metadata.iterrows():

        genus = row['Genus']
        sequence_name= row['Primer_file_name']
        primer_number = row['Primer']
        fwd_seq= row['PRIMER_LEFT_SEQUENCE']
        rev_seq = row['PRIMER_RIGHT_SEQUENCE']

        fasta_subdir:Path = output_path / genus / "primer"

        if not fasta_subdir.exists() :
            fasta_subdir.mkdir(parents=True, exist_ok=True)

        fasta_file_name = fasta_subdir / f' {sequence_name}_{primer_number}.fasta'

        with open(fasta_file_name, "w") as infile :

            infile.write(f""">{sequence_name}_{primer_number}
{fwd_seq}NNN{rev_seq}""")

def prepare_blast_input(reference_dir: str, output_dir: str,config_file: str = "config/config.yaml") -> None:
    """
    """

    reference_dir = Path(reference_dir).resolve()
    output_dir = Path(output_dir).resolve()

    with open(config_file, "r") as infile:
        config_yaml = yaml.safe_load(infile)

    subdirs = [dir for dir in reference_dir.iterdir() if dir.is_dir()]

    genome_files = { subdir: list(subdir.glob("*.fasta")) for subdir in subdirs}

    for subdir in subdirs:

        genus = subdir.name

        target_dir = output_dir / genus / "target"
        non_target_dir = output_dir / genus /  "non_target"

        for dir in [ target_dir, non_target_dir]:

            dir.mkdir(parents=True, exist_ok=True)

        for fasta_file in genome_files[subdir]:

            dest = target_dir / fasta_file.name

            if not dest.exists():

                shutil.copy(fasta_file, dest)

        for other_subdir in [d for d in subdirs if d.name != genus]:

            for fasta_file in genome_files[other_subdir]:
                
                dest = non_target_dir / fasta_file.name

                if not dest.exists():
                    shutil.copy(fasta_file, dest)

        flag_path = output_dir / genus /  "flag.done"

        if not flag_path.exists():
            flag_path.touch()


# Test

# metadata_file = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/0_Final/primer_summary.csv"
# output_dir ="/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/0_Final/"

# extract_fasta(metadata_file,output_dir) 

