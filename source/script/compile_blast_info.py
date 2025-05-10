from pathlib import Path
import pandas as pd

def compile_blast_info(file_dir:str,output_file:str) -> None :

    path_to_files:Path = Path(file_dir).resolve()
    blast_files:list[Path] = list(path_to_files.rglob("*/*/BLAST_out/*.txt"))
    blast_result:dict = {}

    for file in blast_files:
        primer_name, assembly = file.stem.split("_vs_")
        file_type = file.parent.parent.name  # “target” ou “non_target”
        genus = file.parent.parent.parent.name
        check_result = check_blast(file)

        key = primer_name

        if key not in blast_result:

            blast_result[key] = {
                "Path" : file,
                "Genus": genus,
                "Primer": primer_name,
                "target": [],
                "non_target": [],
            }

        blast_result[key][file_type].append(check_result)

    df = pd.DataFrame(blast_result.values())
    df["target"] = df["target"].apply(all)
    df["non_target"] = df["non_target"].apply(all)
    df["Pass"] = df["target"] & ~df["non_target"] # ~ inverse le bool 

    print(df)


def check_blast(blast_path: Path) -> bool:
    """Check if a BLAST file is non-empty and contains both 'plus' and 'minus' strands.

    Parameters
    ----------
    blast_path : Path
        Path to the BLAST output file.

    Returns
    -------
    bool
        True if file is non-empty and contains both 'plus' and 'minus', False otherwise.
    """
    if not blast_path.is_file() or blast_path.stat().st_size == 0:

        return False

    with open(blast_path, "r") as infile:

        content = infile.read()
        
        return "plus" in content and "minus" in content



# Test

path_to_fasta = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/5_BLAST/"

compile_blast_info(path_to_fasta,'.')


