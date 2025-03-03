# Multi_KEC

## Introduction

Multi_KEC est un pipeline basé sur Snakemake conçu pour automatiser les recherches BLAST sur plusieurs assemblages de référence.
Il simplifie la création de bases de données BLAST, l'exécution des recherches, l'extraction des séquences pertinentes et la compilation des résultats dans des formats structurés.
Cet outil est idéal pour mener des analyses de génomique comparative à grande échelle.

Ce dépôt contient un pipeline de traitement de données utilisant Snakemake pour lancer des recherches BLAST sur des fichiers FASTA en les comparant à des assemblages de référence.

![Schéma du pipeline](assets/rulegraphe.png)

## Structure du Pipeline

Le pipeline se décompose en plusieurs étapes :

1. Création de la base de données BLAST  
   Génération de bases de données BLAST nucléotidiques à partir des assemblages.

2. Exécution de BLAST  
   Lancement des recherches BLASTn, TBLASTX ou TBLASTN sur les assemblages de référence.

3. Compilation des résultats  
   Agrégation des fichiers de sortie BLAST dans un format CSV structuré.

4. Extraction des séquences  
   Extraction des séquences en fonction des hits BLAST.

5. Sortie finale  
   Génération d'un fichier FASTA compilé contenant l'ensemble des séquences extraites.

## Structure du Dépôt

L'arborescence du dépôt est la suivante :

Multi_KEC/
|-- LICENSE
|-- README.md
|-- assets
    `-- rulegraphe.png
`-- source
    |-- config
    |   |-- cluster.yaml
    |   `-- config.yaml
    |-- envs
    |   `-- blast.yaml
    |-- ressource
    |-- script
    |   |-- __init__.py
    |   |-- blast_results.py      # Agrège les résultats BLAST en CSV
    |   |-- extract_utils.py      # Outils pour extraire les séquences des résultats BLAST
    |   |-- fasta_utils.py        # Outils pour manipuler les fichiers FASTA
    |   |-- output_extract_files.py  # Gestion des chemins de sortie pour les séquences extraites
    |   `-- output_files.py       # Génération des chemins pour les sorties attendues
    `-- snakefile                 # Définition du pipeline Snakemake

## Utilisation

1. Cloner le dépôt :

   git clone git@github.com:NicolasPoncelet/Multi_KEC.git <nom_du_dossier>
   cd <nom_du_dossier>

2. Configurer le pipeline :  
   Modifie le fichier source/config/config.yaml pour indiquer les chemins vers tes fichiers FASTA, les assemblages de référence et le répertoire de sortie.

3. Exécuter le pipeline :

   snakemake --cores <nombre_de_coeurs>

## Dépendances

- Python 3.11.0
- Snakemake 7.32.4
- pandas 2.2.3


## Feuille de Route

- Ajout de la validation des entrées
- Intégration de la gestion SLURM
- Refactorisation du code redondant
- Ajout de requêtes NCBI pour la récupération des séquences

## Auteurs ✉️

Ce projet a été développé et est maintenu par Nicolas Poncelet.

## Contribuer

Les contributions sont les bienvenues !
Que ce soit pour signaler un bug, suggérer des fonctionnalités ou améliorer la documentation, n'hésite pas à soumettre une pull request ou à ouvrir une issue.

## Licence

Ce dépôt est sous licence MIT (voir le fichier LICENSE).

## À Propos

Pas de description, site web ou sujets spécifiés pour le moment.
