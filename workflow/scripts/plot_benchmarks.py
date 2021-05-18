#!/usr/bin/env python

import argparse
from pathlib import Path
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


def parse_arguments():
    parser=argparse.ArgumentParser(
            description="Plot s, max_rss, io_out per sample group."
            "Produces .png, .svg, .pdf, .eps for all metrics"
            )

    optionalArgs = parser._action_groups.pop()
    optionalArgs.title = "Optional Arguments"

    requiredArgs = parser.add_argument_group("Required Arguments")

    requiredArgs.add_argument(
            "-i",
            "--input",
            type=lambda p: Path(p).resolve(strict=True),
            help="The aggregated benchmarking results",
            dest="input_tsv",
            required=True,
            )
    requiredArgs.add_argument(
            "-o",
            "--output",
            type=lambda p: Path(p).resolve(),
            help="A directory where the figures will be stored",
            dest="output",
            required=True,
            )
    

    parser._action_groups.append(optionalArgs)

    return parser.parse_args()



def plot(data, output_dir, formats=['png','pdf', 'svg', 'eps']):
    variables = {
        's' : 'Runtime (seconds)',
        'max_rss': 'Memory usage - RSS (MB)',
        'io_out' : 'Output written (MB)',
        'cpu_time' : 'Total CPU time'
    }

    rule_order= [
        'quast', 
        'bwa_index', 
        'bwa_mem', 
        'samtools_flagstat', 
        'samtools_stats', 
        'filter', 
        'cat_contigs', 
        'cat_names', 
        'cat_summary'
    ]

    for var in variables:
        with sns.color_palette('deep') as palette:
            g = sns.catplot(
                x='rule', y=var, 
                hue='assembler', col='company', 
                col_wrap = 1, 
                kind = "box",
                data=data,
                palette={'metaspades': palette[0], 'megahit': palette[3]},
                order=rule_order,
                height=4, aspect=2, 
                sharey=False,
            )
            ax = plt.gca()
            g.set_xticklabels(ax.get_xticklabels(), rotation=60)
            g.set_titles(col_template="{col_name}", size=14)
            g.set_ylabels(f'{variables.get(var)}', size=12)
            g.set_xlabels('Rule', size=14)

            for fmt in formats:
                fout_base = f'{var}.{fmt}'
                fout_path = output_dir / Path(fout_base)
                g.fig.savefig(fout_path,
                        dpi=300,
                        bbox_inches='tight'
                        )

def main():
    args = parse_arguments()

    data = pd.read_csv(args.input_tsv, sep='\t', na_values='-')
    plot(data, args.output)


if __name__ == '__main__':
    main()

