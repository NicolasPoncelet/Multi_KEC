from pathlib import Path
import sys
import pandas as pd

def select_best_runs(csv_file:str, fasta_dir:str,report_path:str) -> list[Path] :
    
    fasta_dir = Path(fasta_dir).resolve()
    csv_file:Path = Path(csv_file).resolve()
    report_path:Path = Path(report_path).resolve()

    summary = pd.read_csv(csv_file, header=0, sep = ",")

    df_filtre = summary[summary['Step'] == "Exclude"] 
    df_filtre = df_filtre[df_filtre["seq_number"].notnull() & (df_filtre["seq_number"] != 0)]

    best_runs = df_filtre[df_filtre["seq_number"] == df_filtre.groupby("Genus")["seq_number"].transform("min")]
    best_runs.to_csv(report_path, index=False)

    selected_fasta_files:list[str] = []

    # Selecting best fasta files per genus

    best_runs = best_runs[["Genus","kmer_ex","kmer_in"]]

    for _, row in best_runs.iterrows():

        genus = row["Genus"]
        kmer_ex = row["kmer_ex"]
        kmer_in = row["kmer_in"]

        current_path = Path(f'{fasta_dir}/{genus}/{kmer_in}_{kmer_ex}/{genus}.fasta').resolve()

        print(current_path)
        
        selected_fasta_files.append(current_path)

    return selected_fasta_files


# summary ="/shared/ifbstor1/projects/lolium_gbs/04_Test_MultiKEC/source/script/summary.csv"
# fasta_dir = "/shared/home/nponcelet/lolium_gbs/04_Test_MultiKEC/Test_data/Output/2_KEC_output"
# best_run ="/shared/ifbstor1/projects/lolium_gbs/04_Test_MultiKEC/source/script/best_runs.csv"

if __name__ == "__main__" :

    summary, fasta_dir , report_path = sys.argv[1], sys.argv[2], sys.argv[3]


    select_best_runs(summary,
                    fasta_dir,
                    report_path)