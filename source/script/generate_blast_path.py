from pathlib import Path
from yaml import safe_load

def generate_blast_path(output_path:str) -> list[str] :

    output_path:Path = Path(output_path).resolve()

    fasta_files:list[str] = [str(fasta) for fasta in output_path.glob("*.fasta")]

    return fasta_files

# test = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/5_BLAST/Bipolaris/target"

# liste = generate_blast_path(test)

# print(*liste, sep = "\n")