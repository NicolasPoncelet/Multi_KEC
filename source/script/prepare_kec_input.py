from pathlib import Path
from itertools import product
import yaml

def prepare_kec_input(
    input_dir: str,
    output_dir: str,
    kmer_includes: list,
    kmer_excludes: list,
    config_file: str = "config/config.yaml"
) -> None:
    """
    Crée pour chaque 'genus' trouvé dans input_dir
    ET pour chaque couple (k_in, k_ex) venant de kmer_includes/kmer_excludes :
      - un sous-répertoire <genus>/<k_in>_<k_ex>/
      - y place les symlinks appropriés dans 'master/', 'pool/', 'non_target/'
      - crée 'flag.done' dans <genus>/<k_in>_<k_ex>/

    Paramètres
    ----------
    input_dir      : Chemin du répertoire racine contenant des sous-répertoires par genre,
                     chacun contenant des .fasta
    output_dir     : Chemin racine où sera construite l’arborescence pour KEC
    kmer_includes  : Liste de valeurs de k-mer à inclure (ex: [12, 13, 14])
    kmer_excludes  : Liste de valeurs de k-mer à exclure (ex: [20, 30, 40])
    config_file    : Fichier YAML contenant au moins "master_per_genus"
                     (exemple : { "master_per_genus": {"Bipolaris": "Bipolaris_oryzae_...", ...} })
    """

    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()

    with open(config_file, "r") as infile:
        config_yaml = yaml.safe_load(infile)

    master_dic = config_yaml["master_per_genus"]

    subdirs = [dir for dir in input_dir.iterdir() if dir.is_dir()]

    genome_files = {
        subdir: list(subdir.glob("*.fasta"))
        for subdir in subdirs
    }

    # Pour chaque genre, on va créer l'arborescence
    # pour TOUTES les combinaisons k_in, k_ex
    for subdir in subdirs:
        genus = subdir.name

        # On parcourt toutes les combinaisons possibles de kmer_in et kmer_ex
        for k_in, k_ex in product(kmer_includes, kmer_excludes):

            # Prépare les répertoires (master, pool, target, non_target)
            # en insérant k_in_k_ex dans le chemin
            master_dir = output_dir / genus / f"{k_in}_{k_ex}" / "master"
            pool_dir = output_dir / genus / f"{k_in}_{k_ex}" / "pool"
            target_dir = output_dir / genus / f"{k_in}_{k_ex}" / "target"
            non_target_dir = output_dir / genus / f"{k_in}_{k_ex}" / "non_target"

            for dir in [master_dir, pool_dir, target_dir, non_target_dir]:
                dir.mkdir(parents=True, exist_ok=True)

            # Pour chaque fasta du *même genre* (subdir),
            # - si c'est le "master" => symlink dans master_dir
            # - sinon => symlink quand même dans pool_dir
            # (ou en fait "master" ira aussi dans pool_dir si on suit le script initial)
            for fasta_file in genome_files[subdir]:
                if fasta_file.stem == master_dic.get(genus, ""):

                    link_m = master_dir / fasta_file.name
                    if not link_m.exists():
                        link_m.symlink_to(fasta_file)

                else :

                    link_p = pool_dir / fasta_file.name

                    if not link_p.exists():
                        link_p.symlink_to(fasta_file)

            # Pour chaque autre genre, on met leurs .fasta dans non_target
            for other_subdir in [d for d in subdirs if d != subdir]:
                for fasta_file in genome_files[other_subdir]:
                    link_n = non_target_dir / fasta_file.name
                    if not link_n.exists():
                        link_n.symlink_to(fasta_file)

            # Crée un petit flag pour tracer l’existence de ce répertoire
            flag_path = output_dir / genus / f"{k_in}_{k_ex}" / "flag.done"
            if not flag_path.exists():
                flag_path.touch()
