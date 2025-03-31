from pathlib import Path
import sys
from re import findall
import pandas as pd

def compile_logs(log_dir:str,output_file:str) -> None :

    output_path = Path(output_file).resolve()
    log_dir = Path(log_dir).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True) 

    out_files:list[Path] = list(log for log in log_dir.glob("*.out") if log.stem.startswith("kec_"))
    print(*out_files,sep = '\n')
    results:list = []

    for log in out_files :

        current_result = {}

        with open(log, 'r') as infile:
            
            content = infile.read()

        pattern_number_seq = findall(r'Found (\d+)(?: unique)? sequences', content)
        number_seq = int(pattern_number_seq[0]) if pattern_number_seq else None

        genus,kmer_ex,kmer_in = findall(r'genus=(\w+).+kmer_ex=(\d+).+kmer_in=(\d+)', str(log))[0]

        current_result = {"Genus" : genus,
                        "kmer_ex" : kmer_ex,
                        "kmer_in" : kmer_in,
                        "Run" : log.stem,
                        "Step" : "Include" if "include" in log.name else "Exclude",
                        "seq_number":number_seq }

        results.append(current_result)

    summary = pd.DataFrame.from_dict(results)
    summary.to_csv(output_path)


if __name__ == "__main__" :

    log_dir, output_csv = sys.argv[1], sys.argv[2]

    compile_logs(log_dir,output_csv)

