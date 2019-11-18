import sys
import argparse
from dataset_process_functions import weka_discr, generate_folds


# Written by Laura on Nov. 2019.

# Binarizes the input dataset with the default supervised discretization of weka
# Generates 5 folds (preserving dataset order)
# Args:
#   dataset: full name of dataset (include path)
#   output: output dataset name, to be stored in ./datasets/output/output_bin.csv

def run(args):

    #Use weka's supervised discretization
    dataset_dict,feats_list,cl_list=weka_discr.weka_supervised_discr(args.dataset,args.output)

    # fold generation
    folds=5
    generate_folds.generate_folds(dataset_dict, folds, args.output,feats_list,cl_list)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Binarize datasets and generate folds')
    parser.add_argument('dataset', help='Full dataset')
    parser.add_argument('-o', '--output', type=str, default=None,help='Output name')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())