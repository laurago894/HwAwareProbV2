import argparse
import sys, os
import subprocess

def run(args):

    bench_name=args.bench_name
    vtree_types = ['gen_cmi']
    # vtree_types = ['gen','gen_mi', 'gen_cmi']

    learner_jar = '/users/micas/lgalinde/Documents/code_2019/PSDDlearn_alt/Scala-LearnPsdd/target/scala-2.11/psdd.jar'

    for fold in range(5):

        train='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name +'/'+ bench_name +'_fold' + str(fold) +'/'+ bench_name +'_fold' + str(fold) + '.train.data'
        valid = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '/' + bench_name + '_fold' + str(fold) + '.valid.data'
        test = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '/' + bench_name + '_fold' + str(fold) + '.test.data'

        os.chdir('/users/micas/lgalinde/Documents/code_2019/PSDDlearn_alt/Scala-LearnPsdd/')

        for vtree_type in vtree_types:

            out_location = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '_' + vtree_type + '/'

            if not os.path.exists(out_location):
                os.makedirs(out_location)

            vtree_name = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/vtrees/' + bench_name + '/' + bench_name + '_fold' + str(fold) + '_' + vtree_type + '.vtree'

            if vtree_type=='gen':

                command = 'java -jar ' + learner_jar + ' learnPsdd search -m l-1 -d ' + train + ' -b ' + valid + ' -t ' + test + ' -v ' + vtree_name + ' -o ' + out_location
                print(command)

                code = subprocess.call(command, shell=True)

            else:

                # init_psdd='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/'+ bench_name +'/'+ bench_name +'_fold' + str(fold) + '_'+ vtree_type +'_init.psdd'
                #
                # command = 'java -jar '+ learner_jar +' learnPsdd search -m l-1 -d ' + train + ' -b ' + valid + ' -t ' + test + ' -v ' + vtree_name + ' -o ' + out_location + ' -p ' + init_psdd
                # print(command)
                #
                # code = subprocess.call(command, shell=True)


                out_location2 = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/' + bench_name + '/' + bench_name + '_fold' + str(
                    fold) + '_' + vtree_type + '_factorized_init/'

                init_psdd='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/'+ bench_name +'/'+ bench_name +'_fold' + str(fold) + '_'+ vtree_type +'_init.psdd'

                command = 'java -jar '+ learner_jar +' learnPsdd search -m l-1 -d ' + train + ' -b ' + valid + ' -t ' + test + ' -v ' + vtree_name + ' -o ' + out_location2
                print(command)

                code = subprocess.call(command, shell=True)



def main(argv=None):
    parser = argparse.ArgumentParser(description='Generate initial PSDD with naive Bayes like structure')
    parser.add_argument('bench_name', help='Provide the name of the benchmark')


    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())

