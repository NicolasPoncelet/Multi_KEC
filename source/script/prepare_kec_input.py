from pathlib import Path
import sys

def prepare_kec_input(input_dir: str, output_dir: str) -> None:

    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()

    subdirs = [subdir for subdir in input_dir.iterdir() if subdir.is_dir()]
    genome_dir = {subdir: list(subdir.glob("*.fasta")) for subdir in subdirs}

    for target in subdirs:

        target_path = output_dir / target.name / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        for fasta_file in genome_dir[target]:

            symlink = target_path / fasta_file.name

            if not symlink.exists():
                symlink.symlink_to(fasta_file)

        non_target_path = output_dir / target.name / "non_target"
        non_target_path.mkdir(parents=True, exist_ok=True)

        for non_target in [d for d in subdirs if d != target]:

            for fasta_file in genome_dir[non_target]:

                symlink = non_target_path / fasta_file.name

                if not symlink.exists():
                    symlink.symlink_to(fasta_file)

        flag_file = target_path.parent / "flag.done"
        with open(flag_file,"w") as infile :
            pass
        
if __name__ == "__main__":

    genome_dir, output_dir = sys.argv[1], sys.argv[2]

    prepare_kec_input(genome_dir, output_dir)
