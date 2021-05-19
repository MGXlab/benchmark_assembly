#!/usr/bin/env python

import argparse
from pathlib import Path
from collections import Counter


def parse_arguments():
    parser=argparse.ArgumentParser(
            description="Translate CAT output to ktImportText compatible table"
            )

    optionalArgs = parser._action_groups.pop()
    optionalArgs.title = "Optional Arguments"

    requiredArgs = parser.add_argument_group("Required Arguments")

    requiredArgs.add_argument(
            "-i",
            "--input",
            type=lambda p: Path(p).resolve(strict=True),
            help="<prefix>.contig2classification.txt output from CAT contigs",
            dest="input",
            required=True,
            )
    requiredArgs.add_argument(
            "-o",
            "--output",
            type=lambda p: Path(p).resolve(),
            help="A ktImportText compatible file",
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
            default=False
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


def cat_classifications_to_list(cat_input):
    '''
    Make a list out of all cat classifications
    '''
    assigned = []
    unassigned = 0
    with open(cat_input, 'r') as fin:
        for line in fin:
            if not line.startswith('#'):
                fields = [f.strip() for f in line.split('\t')]
                classification = fields[1]
                if classification == 'taxid assigned':
                    assigned.append(fields[3])
                elif classification == 'no taxid assigned':
                    unassigned += 1
    
    return assigned, unassigned


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



def translate_classification_list(
        class_list, 
        tax_dic, 
        include_stars=False
        ):
    '''
    Map for the poor.
    '''
    translated_list = []
    for i in class_list:
        if is_star(i) and include_stars is True:
            this_i = i.replace('*', '')
            hr = translate_to_human_readable(this_i, tax_dic)
            translated_list.append(hr)
        elif is_star(i) and include_stars is False:
            print("Skipping {}. No stars allowed".format(i))
            continue
        else:
            hr = translate_to_human_readable(i,tax_dic)
            translated_list.append(hr)
    return translated_list


def counter_to_tsv(count_dic, outfile):
    '''
    Write the counts per taxonomy to a file
    '''
    with open(outfile, 'w') as fout:
        for k, v in count_dic.items():
            taxonomy = k.replace(';', '\t')
            fout.write('{}\t{}\n'.format(v, taxonomy))


def main():
    args = parse_arguments()
    
    tax_dic = parse_official_names(args.names_dmp)

    assigned, unassigned = cat_classifications_to_list(args.input)

    print("Assigned: {}".format(len(assigned)))
    print("Unassigned: {}".format(unassigned))
    print("Total: {}".format(sum([len(assigned), unassigned])))

    translated_list = translate_classification_list(
            assigned, tax_dic, include_stars=args.include_stars)

    count_dic = Counter(translated_list)

    if 'root' in count_dic:
        count_dic['root'] += unassigned

    counter_to_tsv(count_dic, args.output)


if __name__ == '__main__':
    main()

