import sys, os
import argparse
from PSDD_functions import PSDD_to_AC
from util import functions
from inference_functions import performance_est
import csv


def run(args):

    bench_name=args.inputBenchmark

    data_location='./datasets/'
    vtree_types = ['gen', 'gen_mi', 'gen_cmi']
    # vtree_types = ['gen_mi']

    for fold in range(5):
        for vt in vtree_types:

            result_dir='./results/' + bench_name + '/'

            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            result_file= result_dir + 'output_' + bench_name + '_fold' + str(fold) + '_' + vt + '.csv'

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

            test=functions.read_file(test_file)
            feature_set = list(range(1, len(test[0].split(','))))

            for model_t in model_list:
                print('\nNow in model  ', model_t[0], '...')

                ac_model = PSDD_to_AC.convert_psdd('learned_models/psdds/' + bench_name + '/' + bench_name + '_fold'+ str(fold) +'_'+ vt +'/models/'+ model_t[1])

                metrics= performance_est.metric_est(ac_model, test, feature_set)
                print('Accuracy', metrics[0])

                writer.writerow([model_t[0]]+metrics)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('inputBenchmark', help='Provide the name of the benchmark')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())