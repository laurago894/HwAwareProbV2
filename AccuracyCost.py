import sys, os
import argparse
from PSDD_functions import PSDD_to_AC
from util import functions
from inference_functions import performance_est
import csv


def run(args):

    bench_name=args.inputBenchmark

    data_location='./datasets/'
    # vtree_types = ['gen','gen_cmi','gen_mi']

    vt=args.vt

    for fold in range(int(args.folds)):


        result_dir='./results/' + bench_name + '/'

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        if args.dt=='train':
            result_file= result_dir + 'train_output_' + bench_name + '_fold' + str(fold) + '_' + vt + '.csv'
        elif args.dt=='test':
            result_file = result_dir + 'output_' + bench_name + '_fold' + str(fold) + '_' + vt + '.csv'

        res_f=open(result_file,'w')
        res_f.write('Model,Accuracy,Params,Mults,Adds\n')

        writer = csv.writer(res_f, delimiter=',')

        model_location='./learned_models/psdds/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '_' + vt + '/models/'
        files=(os.listdir(model_location))

        print('\n\nFold: ', fold, ', type: ' ,vt)

        model_list = sorted([(int(file.split('-')[1].split('.')[0]), file) for file in files if 'psdd' in file and 'final' not in file])

        print(model_list)

        if args.dt=='test':
            test_file = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name + '/' + bench_name + '_fold' + str(
            fold) + '/' + bench_name + '_fold' + str(fold) + '.test.data'
        elif args.dt=='train':
            test_file = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name + '/' + bench_name + '_fold' + str(
            fold) + '/' + bench_name + '_fold' + str(fold) + '.train.data'

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
    parser.add_argument('-f', '--folds', type=str, default=None, help='How many folds')
    parser.add_argument('-vt', '--vt', type=str, default=None, help='Vtree type (gen,gen_mi or gen_cmi)')
    parser.add_argument('-dt', '--dt', type=str, default=None, help='Dataset type (train,test)')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())