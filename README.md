# benchmark_assembly

[WIP]

# Quickstart

You need conda.

```
$ git clone
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

# Benchmarking

The assembly steps are wrapped around some monitoring bash magic that gets 
running stats for the processes every 300 seconds by default (configurable).

Note that if you manually interrupt the workflow or it exits abnormally during
any of the assembly steps (rules metaspades and megahit) you will have to
manually kill the process.

Some resource limitation is included in there to run each assembly step 
separately. This is highly dependant on your setup. `max_mem` must be set 
to the maximum available on your machine to ensure the assembly jobs are 
submitted one by one.

For all other rules, the dedicated `benchmark` directive is used to collect 
runtime stats.


# Output

All results are stored within a dedicated `results` dir within this folder.
This will look like this:

```
$ tree -L 2 -d results
tree -d -L 1 results/
results/
├── benchmarks
├── logs
├── qc
├── sample1
├── sample2
├── sampleX
```

Note that the `qc` dir is manually included in there.

Assuming all your raw fastq files are in a directory `/path/to/raw_reads`:
```
$ mkdir results/qc
$ fastqc --no-extract -t 8 -o results/qc path/to/raw_reads/* 
```
will get you there.

The benchmark dir stores all information from the `benchmark` rules.

Results are stored per sample and look like:

```
sampleX/
├── assembly
│   ├── megahit
│   ├── megahit_tmp
│   ├── metaspades
│   ├── quast_megahit
│   └── quast_metaspades
├── CAT
│   ├── megahit
│   └── metaspades
└── mapping
    ├── megahit_index
    ├── metaspades_index
    └── stats

```
The `logs` dir has runtime logs (captured `stdout` and `stderr` where 
appropriate) per rule.


