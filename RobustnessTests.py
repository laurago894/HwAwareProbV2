import sys, os
import argparse
from PSDD_functions import PSDD_to_AC
from util import functions
from inference_functions import performance_est
import csv


def run(args):

    bench_name=args.inputBenchmark

    vtree_types = ['gen', 'gen_cmi']

    # fail_sets = [0.5, 0.25, 0.125]
    fail_sets = [0.125]

    for vt in vtree_types:

        #Open file with best model per type
        # csv_reader = csv.reader(open('results/' + bench_name + '/best_fold/' + bench_name + '_' + vt + '_restricted.csv'), delimiter=',')
        csv_reader = csv.reader(open('results/' + bench_name + '/best_fold/train_tuned_' + bench_name + '_' + vt + '.csv'), delimiter=',')

        models=[]
        for row in csv_reader:
            models.append(int(row[-1]))

        print(models)

        for fold in range(5):

            model_best=models[fold]

            result_dir='./results/' + bench_name + '/feature_fail/'

            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            # result_file= result_dir + 'fail_output_' + bench_name + '_fold' + str(fold) + '_' + vt + '.csv'

            result_file= result_dir + 'train_tuned_fail_output_' + bench_name + '_fold' + str(fold) + '_' + vt + '.csv'

            res_f=open(result_file,'w')

            writer = csv.writer(res_f, delimiter=',')


            print('\n\nFold: ', fold, ', type: ' ,vt)


            test_file = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name + '/' + bench_name + '_fold' + str(
                fold) + '/' + bench_name + '_fold' + str(fold) + '.test.data'

            print('tf',test_file)

            test=functions.read_file(test_file)
            feature_set = list(range(1, len(test[0].split(','))))


            print('\nNow in model  ', model_best, '...')

            file_mod='learned_models/psdds/' + bench_name + '/' + bench_name + '_fold'+ str(fold) +'_'+ vt +'/models/0-'+ str(model_best) +'.psdd'

            if not os.path.isfile(file_mod):
                file_mod = 'learned_models/psdds/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '_' + vt + '/models/last_0-' + str(model_best) + '.psdd'

            ac_model = PSDD_to_AC.convert_psdd(file_mod)

            accs= performance_est.metric_est_feature_fail(ac_model, test, feature_set,fail_sets)
            print('Accuracy', accs)

            for ff in accs:
                writer.writerow(accs[ff])

        #

def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('inputBenchmark', help='Provide the name of the benchmark')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())