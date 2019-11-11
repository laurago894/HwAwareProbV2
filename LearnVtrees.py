import subprocess, argparse, sys, os


# Written by Laura on Nov. 2019.
#Runs the vtree learner from the PSDDlearn package
#Saves learned vtree in ./learned_models/output/....vtree

# java -jar target/scala-2.11/psdd.jar learnVtreeCMI -d Density-Estimation-Datasets-master/datasets/uci_har_c3/uci_har_c3.train.data -o vtrees/uci_har_c3_cmi_vt_noclass


def run(args):

    learner_jar='/users/micas/lgalinde/Documents/code_2019/PSDDlearn_alt/Scala-LearnPsdd/target/scala-2.11/psdd.jar'
    out_location='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/vtrees/' + args.dataset + '/'

    folds=5

    if not os.path.exists(out_location):
        os.makedirs(out_location)


    os.chdir('/users/micas/lgalinde/Documents/code_2019/PSDDlearn_alt/Scala-LearnPsdd/')

    for fold in range(folds):

        print(os.getcwd())

        train_data_gen='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + args.dataset + '/' + args.dataset + '_fold' +str(fold)+ '/' + args.dataset + '_fold' + str(fold) + '.train.data'
        train_data_gen_discr = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/' + args.dataset + '/' + args.dataset + '_fold' + str(
            fold) + '/' + args.dataset + '_fold' + str(fold) + '_noclass.train.data'


        vtree_gen=out_location + args.dataset + '_fold' + str(fold) + '_gen'
        vtree_discr = out_location + args.dataset + '_fold' + str(fold) + '_gen_mi_noclass'
        vtree_discr_cmi = out_location + args.dataset + '_fold' + str(fold) + '_gen_cmi_noclass'


        process1 = subprocess.Popen(['java','-jar',learner_jar, 'learnVtree', '-d', train_data_gen, '-o', vtree_gen])

        stdout, stderr = process1.communicate()

        process2 = subprocess.Popen(['java','-jar',learner_jar, 'learnVtree', '-d', train_data_gen_discr, '-o', vtree_discr])

        stdout, stderr = process2.communicate()

        process3 = subprocess.Popen(['java','-jar',learner_jar, 'learnVtreeCMI', '-d', train_data_gen, '-o', vtree_discr_cmi])

        stdout, stderr = process3.communicate()

        print('Writing vtrees')
        print(vtree_gen)
        print(vtree_discr)
        print(vtree_discr_cmi)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Learn vtrees')
    parser.add_argument('dataset', help='Dataset name (must be) stored in datasets/dataset/foldx...')
    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())