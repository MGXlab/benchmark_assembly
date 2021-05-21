#!/usr/bin/env python

import argparse
from pathlib import Path

def parse_arguments():
    parser=argparse.ArgumentParser(
            description="Create a ktImportText compatible file from RAT's "
            "<prefix>.complete.abundance.txt"
            )

    optionalArgs = parser._action_groups.pop()
    optionalArgs.title = "Optional Arguments"

    requiredArgs = parser.add_argument_group("Required Arguments")

    requiredArgs.add_argument(
            "-i",
            "--input",
            type=lambda p: Path(p).resolve(strict=True),
            help="Path to the complete.abundance.txt file produced by RAT",
            dest="input",
            required=True,
            )

    requiredArgs.add_argument(
            "-o",
            "--output",
            type=lambda p: Path(p).resolve(),
            help="Path to a tsv file suitable for ktImportText",
            dest="output",
            required=True,
            )

    requiredArgs.add_argument(
            "-n",
            "--names-dmp",
            dest="names_dmp",
            help="The names.dmp file available from NCBI Taxonomy. This "
            "should be included in the CAT_taxonomy.<timestamp> directory",
            required=True,
            type=lambda p: Path(p).resolve(strict=True)
            )

    optionalArgs.add_argument(
            "--include-stars",
            dest="include_stars",
            action="store_true",
            help="Include suggestive classifications, marked with '*' "
            "[default = False]",
            default=False,
            required=False,
            )
    

    optionalArgs.add_argument(
            "--count-value",
            dest="colname",
            choices=['number', 'fraction', 'cor_fraction'],
            default='number',
            help="Specify which counts to use [default='number']",
            required=False
            )

    parser._action_groups.append(optionalArgs)

    return parser.parse_args()



def parse_official_names(names_dmp):
    '''
    Get the scientific names for the numeric taxids 
    '''
    tax_dic = {}
    with open(names_dmp, 'r') as fin:
        for line in fin:
            fields = [f.strip() for f in line.split('|')]
            tax_id = fields[0]
            if fields[3] == 'scientific name':
                tax_dic[tax_id] = fields[1]
    return tax_dic

def which_col_index(colname):
    try:
        if colname == 'number':
            return 1
        if colname == 'fraction':
            return 2
        if colname == 'cor_fraction':
            return 4
    except:
        print('Please provide a valid value for count-value')
        print('You specified {}'.format(colname))
        raise
        

def is_star(lineage_string):
    if '*' in lineage_string:
        return True
    else:
        return False


def translate_to_human_readable(lineage_string, tax_dic):
    '''
    Translate a numeric lineage string to human readable
    '''
    human_tokens = []
    for taxid in lineage_string.split(';'):
        try:
            taxname = tax_dic[taxid]
            human_tokens.append(taxname)
            human_string = ';'.join(human_tokens)
        except:
            print(lineage_string)
            raise
    return human_string

def parse_complete_abundance_tsv(input_fp, 
        tax_dic, 
        col_index=1, 
        include_stars=False
        ):

    stats = {}
    with open(input_fp, 'r') as fin:
        for line in fin:
            if not line.startswith('#'):
                fields = [f.strip() for f in line.split('\t')]
                lineage = fields[0]
                value = fields[col_index]
                if lineage == 'unmapped':
                    stats['unmapped'] = fields[1]
                elif lineage == 'unclassified':
                    stats['unclassified'] = fields[1]

                elif (is_star(lineage) is True) and (include_stars is True):
                    lineage_ = lineage.replace('*', '')
                    hr_lineage = translate_to_human_readable(lineage_ , tax_dic)
                    stats[hr_lineage] = value
                elif (is_star(lineage) is True) and (include_stars is False):
                    print("Skipping {}. No stars allowed".format(lineage))
                    continue
                else:
                    hr_lineage = translate_to_human_readable(lineage, tax_dic)
                    stats[hr_lineage] = value
    
    return stats


def write_stats_to_file(stats, output_fp):
    with open(output_fp, 'w') as fout:
        for lineage, value in stats.items():
            lineage_string = '\t'.join(lineage.split(';'))
            fout.write('{}\t{}\n'.format(value, lineage_string))



def main():
    args = parse_arguments()

    tax_dic = parse_official_names(args.names_dmp)

    col_index = which_col_index(args.colname)

    stats = parse_complete_abundance_tsv(args.input,
            tax_dic, 
            col_index=col_index, 
            include_stars=True
            )

    if 'root' in stats:
        if args.colname in ['fraction', 'cor_fraction']:
            stats['root'] = float(stats['root']) + float(stats['unclassified'])
        else:
            stats['root'] = int(stats['root']) + int(stats['unclassified'])

        stats.pop('unclassified')

    write_stats_to_file(stats, args.output)

if __name__ == '__main__':
    main()

