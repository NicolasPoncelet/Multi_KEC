import yaml
from pathlib import Path

from script.prepare_kec_input import prepare_kec_input
from script.prepare_primer3_input import prepare_primer3_input
from script.generate_input_path import get_input_path
from script.compile_logs import compile_logs
from script.select_best_runs import select_best_runs
from script.prepare_blast_input import prepare_blast_input, extract_fasta
from script.compile_primer_info import compile_primer_info
from script.generate_blast_path import generate_blast_path
from script.metrics_utils import compile_assemblies_info

configfile: "config/config.yaml"

with open("config/config.yaml", "r") as infile:
    config_yaml = yaml.safe_load(infile)

GENOME_DIR = Path(config_yaml["genomes_dir"]).resolve()
OUTPUT_DIR = Path(config_yaml["analysis_dir"]).resolve()
KEC_TOOL = Path("../tools/kec-linux-x64").resolve()
KMER_INCLUDE = config["kec_include_settings"]["kmer_values"]
KMER_EXCLUDE = config["kec_exclude_settings"]["kmer_values"]

genera = [d.name for d in GENOME_DIR.iterdir() if d.is_dir()]

rule all:
    input:
        genome_report = f"{OUTPUT_DIR}/0_Final/genome_report.csv",
        kec_ex = expand(
            f"{OUTPUT_DIR}/2_KEC_output/{{genus}}/{{kmer_in}}_{{kmer_ex}}/{{genus}}.fasta",
            genus=genera,
            kmer_in=KMER_INCLUDE,
            kmer_ex=KMER_EXCLUDE
        ),
        primer3_output_flags = expand(
            f"{OUTPUT_DIR}/4_Primer3_output/{{genus}}/primer3.done",
            genus=genera
        ),
        final_flag =expand( f"{OUTPUT_DIR}/5_BLAST/{{genus}}/flag.done",
            genus=genera ),
        db_blast_done = expand(f'{OUTPUT_DIR}/5_BLAST/{{genus}}/{{type}}/blast_db.done',
                        genus = genera,
                        type = ["target","non_target"]
                        ),
        blast_target = expand(f'{OUTPUT_DIR}/5_BLAST/{{genus}}/{{type}}/BLAST_out/blast.done',
                        genus=genera,
                        type=["target", "non_target"]
                        )

rule calculate_assemblies_metrics:
    input:
        genomes = GENOME_DIR
    output:
        genome_report = f"{OUTPUT_DIR}/0_Final/genome_report.csv"
    run:
        compile_assemblies_info(
            assembly_dir = input.genomes,
            report_file = output.genome_report
        )

rule prepare_input:
    input:
        dir=GENOME_DIR
    output:
        done_flags=expand(
            "{analysis_dir}/1_KEC_input/{genus}/{k_in}_{k_ex}/flag.done",
            analysis_dir=str(OUTPUT_DIR),
            genus=genera,
            k_in=KMER_INCLUDE,
            k_ex=KMER_EXCLUDE
        )
    run:
        prepare_kec_input(
            input_dir=str(input.dir),
            output_dir=str(OUTPUT_DIR / "1_KEC_input"),   
            kmer_includes=KMER_INCLUDE,
            kmer_excludes=KMER_EXCLUDE,
            config_file="config/config.yaml"
        )

rule kec_include:
    input:
        flag = rules.prepare_input.output.done_flags
    output:
        target_files = f"{OUTPUT_DIR}/1_KEC_input/{{genus}}/{{kmer_in}}_{{kmer_ex}}/target/{{genus}}.fasta"
    params:
        kec_include_settings = config_yaml["kec_include_settings"]["kec_params"],
        master_dir = f"{OUTPUT_DIR}/1_KEC_input/{{genus}}/{{kmer_in}}_{{kmer_ex}}/master",
        pool_dir = f"{OUTPUT_DIR}/1_KEC_input/{{genus}}/{{kmer_in}}_{{kmer_ex}}/pool"
    shell:
        """
        {KEC_TOOL} include \
        -m {params.master_dir} \
        -p {params.pool_dir} \
        -o {output.target_files} \
        -k {wildcards.kmer_in} \
        {params.kec_include_settings}
        """

rule kec_exclude:
    input:
        target = rules.kec_include.output.target_files,
    output:
        fasta_files = f"{OUTPUT_DIR}/2_KEC_output/{{genus}}/{{kmer_in}}_{{kmer_ex}}/{{genus}}.fasta"
    params:
        kec_exclude_settings = config_yaml["kec_exclude_settings"]["kec_params"],
        non_target = f"{OUTPUT_DIR}/1_KEC_input/{{genus}}/{{kmer_in}}_{{kmer_ex}}/non_target"
    shell:
        """
        {KEC_TOOL} exclude \
        -t {input.target} \
        -n {params.non_target} \
        -o {output.fasta_files} \
        -k {wildcards.kmer_ex} \
        {params.kec_exclude_settings}
        """

rule compile_run_infos:
    input:
        expand(
            f"{OUTPUT_DIR}/2_KEC_output/{{genus}}/{{kmer_in}}_{{kmer_ex}}/{{genus}}.fasta",
            genus=genera,
            kmer_in=KMER_INCLUDE,
            kmer_ex=KMER_EXCLUDE
        )
    output:
        kec_report = f"{OUTPUT_DIR}/0_Final/KEC_run_info.csv"
    run:
        compile_logs(
            log_dir="./logs",  
            output_file=output.kec_report
        )

rule prepare_primer3_input:
    input:
        kec_report = rules.compile_run_infos.output.kec_report,
    output:
        primer3_flag = f"{OUTPUT_DIR}/3_Primer3_input/{{genus}}/flag.done"
    run:

        fasta_files = select_best_runs(
            rules.compile_run_infos.output.kec_report,
            f"{OUTPUT_DIR}/2_KEC_output/",
            f"{OUTPUT_DIR}/0_Final/KEC_best_run.csv")

        prepare_primer3_input(
            fasta_files,
            f"{OUTPUT_DIR}/3_Primer3_input/",
            f"{OUTPUT_DIR}/0_Final/KEC_summary.csv"
        )

rule primer3:
    input: 
        primer3_input_flag = rules.prepare_primer3_input.output.primer3_flag
    output: 
        primer3_output_flag = f"{OUTPUT_DIR}/4_Primer3_output/{{genus}}/primer3.done"
    conda:
        "envs/primer3.yaml"  
    params:
        input_dir = f"{OUTPUT_DIR}/3_Primer3_input/{{genus}}",
        output_dir = f"{OUTPUT_DIR}/4_Primer3_output/{{genus}}"
    shell:
        """
        mkdir -p {params.output_dir}
        for txt_file in {params.input_dir}/*.txt; do
            primer3_core "$txt_file" > {params.output_dir}/$(basename "$txt_file" .txt).primer
        done
        touch {output.primer3_output_flag}
        """

rule prepare_blast_files:
    input:
        primer3_done_flag = rules.primer3.output.primer3_output_flag
    output:
        prepare_blast_done_flag = f"{OUTPUT_DIR}/5_BLAST/{{genus}}/flag.done"
    run:

        compile_primer_info(
            primer_dir = f"{OUTPUT_DIR}/4_Primer3_output/",
            output_file = f"{OUTPUT_DIR}/0_Final/primer_summary.csv"
            )

        extract_fasta(
            metadata_file = f"{OUTPUT_DIR}/0_Final/primer_summary.csv",
            output_dir = f"{OUTPUT_DIR}/5_BLAST/"
            )

        prepare_blast_input(
            reference_dir = str(GENOME_DIR),
            output_dir = f"{OUTPUT_DIR}/5_BLAST/",
            config_file = "config/config.yaml"
        )

rule make_BLAST_db:
    input:
        flag_done = f"{OUTPUT_DIR}/5_BLAST/{{genus}}/flag.done",
        assemblies = lambda wildcards: generate_blast_path(f'{OUTPUT_DIR}/5_BLAST/{wildcards.genus}/{wildcards.type}')
    output:
        blast_db_flag = f'{OUTPUT_DIR}/5_BLAST/{{genus}}/{{type}}/blast_db.done'
    conda:
        "envs/blast.yaml"
    shell:
        """
        for fasta in {input.assemblies}; do
        
            fasta_path=$(realpath "$fasta")
            fasta_dir=$(dirname "$fasta_path")
            fasta_name=$(basename "$fasta_path" .fasta)

            makeblastdb \
                -in "$fasta_path" \
                -dbtype nucl \
                -out "$fasta_dir/${{fasta_name}}"
        done

        touch {output.blast_db_flag}
        """

rule BLASTN_query:
    """BLASTN query in Database_nuc"""
    input:
        db_done = rules.make_BLAST_db.output.blast_db_flag,
    output:
        blast_target = f'{OUTPUT_DIR}/5_BLAST/{{genus}}/{{type}}/BLAST_out/blast.done'
    params:
        output_dir = f'{OUTPUT_DIR}/5_BLAST/{{genus}}/{{type}}/BLAST_out',
        assemblies_dir = f'{OUTPUT_DIR}/5_BLAST/{{genus}}/{{type}}',
        primer_dir = f'{OUTPUT_DIR}/5_BLAST/{{genus}}/primer'
    conda:
        "envs/blast.yaml"
    shell:
        """
        mkdir -p {params.output_dir}

        for assembly_db in {params.assemblies_dir}/*.fasta; do

            db_name=$(basename "$assembly_db" .fasta)

            for primer in {params.primer_dir}/*.fasta; do
                primer_name=$(basename "$primer" .fasta)
                blastn -task blastn-short \
                    -query "$primer" \
                    -db "{params.assemblies_dir}/$db_name" \
                    -out "{params.output_dir}/${{primer_name}}_vs_${{db_name}}.txt" \
                    -dust no \
                    -soft_masking false \
                    -penalty -3 \
                    -reward 1 \
                    -gapopen 5 \
                    -gapextend 2 \
                    -evalue 1e-3 \
                    -outfmt '6 qseqid sseqid pident length qframe sframe sstrand mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq'
            done
        done

        touch {output.blast_target}
        """

