#!/usr/bin/env python

import argparse
from pathlib import Path
import logging
import pandas as pd


def parse_arguments():
    parser=argparse.ArgumentParser(
            description="Collect all benchmarks in one table"
            )

    optionalArgs = parser._action_groups.pop()
    optionalArgs.title = "Optional Arguments"

    requiredArgs = parser.add_argument_group("Required Arguments")

    requiredArgs.add_argument(
            "-i",
            "--input",
            type=lambda p: Path(p).resolve(strict=True),
            help="Path to benchmarks dir",
            dest="input",
            required=True,
            )
    requiredArgs.add_argument(
            "-o",
            "--output",
            type=lambda p: Path(p).resolve(),
            help="Output table",
            dest="output",
            required=True,
            )
    optionalArgs.add_argument(
            "-m",
            "--meta",
            required=False,
            action="append",
            dest="meta",
            nargs=3,
            metavar=("meta", "value", "pattern"),
            help="Specify a pattern to be used for grouping samples. e.g "
            "If you have samples from two different conditions, A,B and these "
            "are encoded in the sample names as A_sample1, B_sample1 "
            "this will generate a column 'meta' with the values of A or B "
            "included"
            )


    parser._action_groups.append(optionalArgs)

    return parser.parse_args()



def tsv_to_df(input_tsv, patterns=None):
    fp_name = input_tsv.name
    sample_id = fp_name.split('.')[0]
    rule_info = fp_name.split('.')[1]
    assembler = rule_info.split('_')[-1]
    rule = '_'.join(rule_info.split('_')[:-1])
    df = pd.read_csv(
            input_tsv,
            sep='\t',
            na_values='-'
            )
    df['sample_id'] = sample_id
    df['rule'] = rule
    df['assembler'] = assembler
    if patterns:
        for p in patterns:
            if sample_id.startswith(patterns[p][1]):
                df[patterns[p][0]] = p
    return df

def main():
    args = parse_arguments()

    if not args.output.parent.exists():
        args.output.parent.mkdir()

    cols = [
            'sample_id',
            'rule',
            'assembler',
            's',
            'h:m:s',
            'max_rss',
            'max_vms',
            'max_uss',
            'max_pss',
            'io_in',
            'io_out',
            'mean_load',
            'cpu_time'
            ]

    patterns=None
    if args.meta:
        patterns = {i[1] : (i[0],i[2]) for i in args.meta}
    
    all_dfs = []
    for path in args.input.iterdir():
        if path.is_file():
            all_dfs.append(tsv_to_df(path, patterns))

    master_df = pd.concat(all_dfs)
    if patterns:
        for p in patterns:
            if patterns[p][0] not in cols:
                cols.append(patterns[p][0])
    master_df = master_df[cols]
    master_df = master_df.sort_values(by='sample_id')
    master_df.to_csv(args.output, 
            sep="\t", 
            index=False,
            na_rep='-'
            )

if __name__ == '__main__':
    main()

