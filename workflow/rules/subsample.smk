import pandas as pd

samples_df = pd.read_csv(
        config["samples"],
        sep = "\t",
        )

SAMPLES = samples_df.sample_id.to_list()

datasets_params = { 
        '1M' : 100000,
        '2M' : 200000,
        '5M' : 500000,
        '10M': 10000000,
        '20M': 20000000
        }


def get_fastqs(wc):
    r1 = samples_df.loc[samples_df['sample_id'] == wc.sample]['R1'].values[0]
    r2 = samples_df.loc[samples_df['sample_id'] == wc.sample]['R2'].values[0]
    return list((r1,r2))

rule all:
    input:
        expand([
            "datasets/{dataset}/{sample}_{dataset}_R1.fastq.gz",
            "datasets/{dataset}/{sample}_{dataset}_R2.fastq.gz"
            ],
            dataset=["1M", "2M", "5M", "10M", "20M"],
            sample=SAMPLES,
            )

rule subsample:
    output:
        fq1 = "datasets/{dataset}/{sample}_{dataset}_R1.fastq.gz",
        fq2 = "datasets/{dataset}/{sample}_{dataset}_R2.fastq.gz"
    input:
        fqs = get_fastqs
    params:
        rseed = 11,
        no = lambda wc : datasets_params[wc.dataset]
    shell:
        "seqtk sample -s{params.rseed} {input.fqs[0]} {params.no}"
        "| gzip -c > {output.fq1} && "
        "seqtk sample -s{params.rseed} {input.fqs[1]} {params.no}"
        "| gzip -c > {output.fq2}"

