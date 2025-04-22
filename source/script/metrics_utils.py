from yaml import safe_load
from pathlib import Path
import sys

def compile_assemblies_info(assembly_dir:str,report_file:str) -> None :

    assembly_path:Path = Path(assembly_dir).resolve()

    report_path:Path = Path(report_file).resolve()
    report_content:str = "\t".join(["Genus","Assembly","Size","Scaffolds","GC_ratio","N_ratio"])

    assemblies:list[Path] = list(assembly_path.rglob("*/*.fasta"))

    for assembly in assemblies :
        
        genus = assembly.parent.name
        fasta_name = assembly.stem
        metrics = get_assembly_metrics(assembly)

        report_content += "\n"
        report_content += "\t".join([genus,fasta_name,*metrics])

    with open(report_path , "w") as ouftile :

        ouftile.write(report_content)

def get_assembly_metrics(assembly_path:Path) -> tuple[str] :

    scaffold_number:int =0
    sequence:list[str] = []

    with open(assembly_path,"r") as infile :

        for line in infile :

            if line.startswith(">") :

                scaffold_number += 1
            
            else :
                current_line:list[str] = list(line)
                sequence.extend(current_line)

    assembly_size:int = len(sequence)
    gc_content:int = len([base for base in sequence if base in ["G","C"] ])
    n_content:int = len([base for base in sequence if base == "N"])
    gc_ratio:float = round((gc_content / assembly_size)* 100 ,2 )
    n_ratio:float = round((n_content / assembly_size) *100 , 2)
    assembly_size_mb:int = round(assembly_size / 1000000,1)

    return (str(assembly_size_mb),str(scaffold_number), str(gc_ratio), str(n_ratio))

# report_file = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/source/report.txt"

# metrics = compile_assemblies_info(report_file)

if __name__ == "__main__" :

    assembly_dir, report_file = sys.argv[1], sys.argv[2]

    compile_assemblies_info(assembly_dir,report_file)