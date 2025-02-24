from pathlib import Path
import sys, yaml

def prepare_kec_input(input_dir: str, output_dir: str) -> None:

    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()

    with open("config/config.yaml", "r") as infile:
        config_yaml = yaml.safe_load(infile)

    subdirs = [subdir for subdir in input_dir.iterdir() if subdir.is_dir()]
    genome_dir = {subdir: list(subdir.glob("*.fasta")) for subdir in subdirs}
    master_dic = config_yaml["master_per_genus"]

    for subdir in subdirs :

        master_dir = output_dir / subdir.name / "master"
        pool_dir = output_dir / subdir.name / "pool"
        target_dir = output_dir / subdir.name / "target"
        non_target_dir = output_dir / subdir.name / "non_target"
        
        for dir in [master_dir,pool_dir,target_dir,non_target_dir] :
            dir.mkdir(parents=True, exist_ok=True)
        
        for target in genome_dir[subdir] :

            if (target.stem or target.name) ==  master_dic[subdir.name] :
                symlink = master_dir / target.name
                
                if not symlink.exists():
                    symlink.symlink_to(target) 
            
            symlink = pool_dir / target.name

            if not symlink.exists():
                symlink.symlink_to(target) 

            for non_target in [d for d in subdirs if d != subdir]:

                for fasta in genome_dir[non_target]:

                    symlink = non_target_dir / fasta.name

                    if not symlink.exists():
                        symlink.symlink_to(fasta)
        
        flag_file = master_dir.parent / "flag.done"
        with open(flag_file,"w") as infile :
            pass

if __name__ == "__main__":

    genome_dir, output_dir = sys.argv[1], sys.argv[2]

    prepare_kec_input(genome_dir, output_dir)
