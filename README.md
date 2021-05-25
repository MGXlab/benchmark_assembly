# benchmark_assembly

[WIP]

# Quickstart

You need conda.

```
$ git clone git@github.com:MGXlab/benchmark_assembly.git
$ cd benchmark_assembly
$ conda env create -n bass -f=environment.yml
$ conda activate bass

# Fill in the config/config.yaml
(bass)$ snakemake --use-conda --conda-frontend mamba -j 32
```

# Description

No trimming/adapter removal is done for now.
It is assumed you have run fastqc manually and a `qc` dir is present in the 
results dir.

For every sample in the samplesheet:

* Assembles reads with megahit and metaspades
* Raw assembly stats are calculated with QUAST
* Reads are mapped back to the assemblies.
* Mapping stats are calculated with `samtools stats` and `flagstat`

Raw assembly fasta files are filtered for scaffolds > 1500bp and
* They get taxonomically annotated with CAT.
* Read counts are produced with an in-house add on for CAT (not yet merged 
upstream but soon...)

# Benchmarking

The assembly steps are wrapped around some monitoring bash magic that gets 
running stats for the processes every 300 seconds by default (configurable).

Note that if you manually interrupt the workflow or it exits abnormally during
any of the assembly steps (rules `metaspades` and `megahit`) you will have to
manually kill the process. This is because the process is sent to the 
background (notice the trailing `&` of the `time` command). This somehow 
escapes from snakemake monitoring and needs special care.

> Maybe use `trap`?

The assembly step is resource limited to the maximum available on the host 
machine. That means, each of the assembly steps are run sequentially and not 
in parallel. For large datasets and `metaspades` this might even be desirable.

> Since `megahit` is quite cheap to run even on large datasets, maybe make 
> this configurable?

For all other rules, the dedicated `benchmark` directive is used to collect 
runtime stats. See 
[snakemake's docs](https://snakemake.readthedocs.io/en/stable/tutorial/additional_features.html#benchmarking) 
and [this table](https://stackoverflow.com/a/66872577/15514684) for more info 
on the reported values meaning.

# Output

All results are stored within a dedicated `results` dir within this folder.
This will look like this:

```
$ tree -L 2 -d results

results/
├── benchmarks
├── krona.html
├── logs
├── multiqc_data.zip
├── multiqc_report.html
├── qc
├── RAT_krona.html
├── runtime_stats
└── samples
```

Note that the `qc` dir is manually included in there.

Assuming all your raw fastq files are in a directory `/path/to/raw_reads`:
```
$ mkdir results/qc
$ fastqc --no-extract -t 8 -o results/qc path/to/raw_reads/* 
```
will get you there.

* The `benchmarks` dir stores all information from the benchmark rules.

All raw results (assemblies, bams, cat/rat output) are stored per sample 
within the `samples` dir. Each subdir is named based on the `sample_id` 
column provided with the samplesheet.

A full run, with both assemblers enabled, should look like this:

```
$ tree -d results/samples/sampleX
results/samples/sampleX/
├── assembly
│   ├── megahit
│   ├── megahit_tmp
│   ├── metaspades
│   │   ├── misc
│   │   ├── pipeline_state
│   │   └── tmp
│   ├── quast_megahit
│   │   └── basic_stats
│   └── quast_metaspades
│       └── basic_stats
├── CAT
│   ├── megahit
│   └── metaspades
├── mapping
│   ├── megahit_index
│   ├── metaspades_index
│   └── stats
└── RAT
    ├── megahit
    └── metaspades
```

If one of the available assemblers is skipped, its respective dirs will not 
be present.

The `logs` dir has runtime logs (captured `stdout` and `stderr` where 
appropriate) per rule.

# Report

```
$ snakemake --report report/home.html
```
