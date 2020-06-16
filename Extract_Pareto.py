import prune_PSDD
import argparse, sys
from util import Pareto_functions, functions

# -invtree
# /users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/vtrees/har_mv/har_mv_fold0_gen_cmi.vtree
# -inpsdd
# /users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/har_mv/har_mv_fold0_gen_cmi/models/0-152-prune1-25-50.psdd
# -prunef
# 26
# -outpsdd
# /users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/har_mv/har_mv_fold0_gen_cmi/models/0-152-prune1-25-50-26.psdd

def run(args):

    myfile=functions.read_file(args.inputFile)


    list_inpareto=[None]*(len(myfile)-1)
    for ii,line in enumerate(myfile[1:]):
        ll=[float(num) for num in line.split(',')[:3]]
        ll[-1]=ll[-1]/float(myfile[-1].split(',')[2])
        list_inpareto[ii]=tuple(ll)

    print(list_inpareto)

    pareto_list=Pareto_functions.pareto_acc_cost(list_inpareto)

    print(pareto_list)

    if args.outfile:
        outf=open(args.outfile,'w')
        for tup in pareto_list:
            outf.write(','.join([str(num) for num in list(tup)])+'\n')
        outf.close()
        print('Pareto list written to ', args.outfile)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('inputFile', help='Text file with dirs of models')
    parser.add_argument('-outfile','--outfile',type=str, default=None, help='Write pareto list to this file')
    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())