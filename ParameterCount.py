import sys, os
import argparse
from PSDD_functions import PSDD_to_AC
from util import functions
from inference_functions import performance_est
import csv


def run(args):

    bench_name=args.inputBenchmark

    vtree_types = ['gen', 'gen_cmi']

    for fold in range(int(args.folds)):
        for vt in vtree_types:

            result_dir='./results/' + bench_name + '/'

            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            result_file= result_dir + 'param_count_' + bench_name + '_fold' + str(fold) + '_' + vt + '.csv'

            res_f=open(result_file,'w')
            res_f.write('Model,Accuracy,Params,Mults,Adds\n')

            writer = csv.writer(res_f, delimiter=',')

            model_location='./learned_models/psdds/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '_' + vt + '/models/'
            files=(os.listdir(model_location))

            print('\n\nFold: ', fold, ', type: ' ,vt)

            model_list = sorted([(int(file.split('-')[1].split('.')[0]), file) for file in files if 'psdd' in file and 'final' not in file])

            print(model_list)

            test_file = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name + '/' + bench_name + '_fold' + str(
                fold) + '/' + bench_name + '_fold' + str(fold) + '.test.data'

            print('tf',test_file)



            for model_t in model_list:
                print('\nNow in model  ', model_t[0], '...')

                psdd_name='learned_models/psdds/' + bench_name + '/' + bench_name + '_fold'+ str(fold) +'_'+ vt +'/models/'+ model_t[1]

                psdd=functions.read_file(psdd_name)
                param_count=0
                for line in psdd:
                    if line.split(' ')[0]!='c':
                        if 'T' in line and float(line.split( )[-1])!=0.0:
                            param_count+=2 #positive and negative
                        if 'D' in line:
                            children=int(line.split(' ')[3])
                            for child in range(children):
                                if float(line.split(' ')[6+(child*3)])!=0.0:
                                    param_count+=1

                print(param_count)
                writer.writerow([model_t[0]] + [param_count])



def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('inputBenchmark', help='Provide the name of the benchmark')
    parser.add_argument('-f', '--folds', type=str, default=None, help='How many folds')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())