import itertools
import random
import os, csv
import random

def generate_folds(dataset_dict,folds,output_name,feature_list,class_list):

    fold_size = int(len(dataset_dict) / folds)
    num_instances = list(range(len(dataset_dict)))
    random.shuffle(num_instances)


    ranges_dict = {}
    fold_num = 0
    for i in range(0, len(dataset_dict), fold_size):
        ra = (num_instances[i:i + fold_size])

        if fold_num > folds - 1:
            ranges_dict[fold_num - 1] = ranges_dict[fold_num - 1] + list(ra)
        else:
            ranges_dict[fold_num] = list(ra)

        fold_num += 1


    for fold in ranges_dict:
        fold_train = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.train.data'
        fold_train_a = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.train.arff'
        fold_train_a_cmi = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '_cmi.train.data'
        fold_train_nc = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '_noclass.train.data'
        fold_test = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.test.data'
        fold_test_a = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.test.arff'
        fold_valid = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.valid.data'
        fold_valid_a = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.valid.arff'



        if not os.path.exists('./datasets/' + output_name + '/' + output_name + '_fold' + str(fold)):
            os.makedirs('./datasets/' + output_name + '/' + output_name + '_fold' + str(fold))

        with open(fold_train, mode='w') as train_file, open(fold_train_a, mode='w') as train_file_a, open(fold_train_a_cmi, mode='w') as train_file_a_cmi, open(fold_train_nc, mode='w') as train_file_nc, \
                open(fold_test, mode='w') as test_file, open(fold_test_a, mode='w') as test_file_a,\
                open(fold_valid,mode='w') as valid_file,open(fold_valid_a,mode='w') as valid_file_a:

            writer_train = csv.writer(train_file, delimiter=',')
            writer_test = csv.writer(test_file, delimiter=',')
            writer_valid = csv.writer(valid_file, delimiter=',')

            writer_train_a = csv.writer(train_file_a, delimiter=',')
            writer_train_a_cmi = csv.writer(train_file_a_cmi, delimiter=',')
            writer_test_a = csv.writer(test_file_a, delimiter=',')
            writer_valid_a = csv.writer(valid_file_a, delimiter=',')

            writer_train_nc = csv.writer(train_file_nc, delimiter=',')


            test_samples = ranges_dict[fold]
            train_folds = [f for f in list(range(folds)) if f != fold]
            train_samples = list(itertools.chain.from_iterable([ranges_dict[f] for f in train_folds]))

            # Randomly sample 10% for validation -- model learning purposes
            valid_samples = random.sample(train_samples, int(len(dataset_dict) / 10))
            [train_samples.pop(train_samples.index(num)) for num in valid_samples]

            # Check if sets are mutually exclusive
            print('Are data points in fold', fold, ' mutually exclusive? ' ,len(list(set(list(set(train_samples))+list(set(test_samples))+list(set(valid_samples))))) == len(dataset_dict))

            #Header for arff file

            train_file_a.write('% Generated by /HwAwareProbV2/BinarizeDataset.py\n')
            train_file_a.write('@Relation ' + output_name + '_train_fold_' + str(fold)+'\n')

            test_file_a.write('% Generated by /HwAwareProbV2/BinarizeDataset.py\n')
            test_file_a.write('@Relation ' + output_name + '_test_fold_' + str(fold) + '\n')

            valid_file_a.write('% Generated by /HwAwareProbV2/BinarizeDataset.py\n')
            valid_file_a.write('@Relation ' + output_name + '_valid_fold_' + str(fold) + '\n')

            featnum=len(dataset_dict[0])-1

            for feat in feature_list:
                train_file_a.write('@attribute feature_' + str(feat) +' {0,1}\n')
                test_file_a.write('@attribute feature_' + str(feat) + ' {0,1}\n')
                valid_file_a.write('@attribute feature_' + str(feat) + ' {0,1}\n')

            if len(class_list)==2:
                class_str='{0,1}'
            else:
                class_str='{'+ (',').join([str(num) for num in range(0,len(class_list))]) + '}'

            train_file_a.write('@attribute class '+ class_str +'\n@data\n\n')
            test_file_a.write('@attribute class '+ class_str +'\n@data\n\n')
            valid_file_a.write('@attribute class '+ class_str +'\n@data\n\n')


            for sample in train_samples:
                writer_train.writerow(dataset_dict[sample])
                if len(class_list) ==1:
                    writer_train_nc.writerow(dataset_dict[sample][:-1])
                    writer_train_a.writerow(dataset_dict[sample])
                    writer_train_a_cmi.writerow(dataset_dict[sample])
                else:
                    writer_train_nc.writerow(dataset_dict[sample][:-len(class_list)])
                    cl_li=[dataset_dict[sample][-len(class_list):].index(1)]
                    writer_train_a.writerow(dataset_dict[sample][:-len(class_list)]+cl_li)
                    writer_train_a_cmi.writerow(dataset_dict[sample][:-len(class_list)] + cl_li)
            for sample in test_samples:
                writer_test.writerow(dataset_dict[sample])
                if len(class_list) == 1:
                    writer_test_a.writerow(dataset_dict[sample])
                else:
                    cl_li=[dataset_dict[sample][-len(class_list):].index(1)]
                    writer_test_a.writerow(dataset_dict[sample][:-len(class_list)]+cl_li)
            for sample in valid_samples:
                writer_valid.writerow(dataset_dict[sample])
                if len(class_list) == 1:
                    writer_valid_a.writerow(dataset_dict[sample])
                else:
                    cl_li=[dataset_dict[sample][-len(class_list):].index(1)]
                    writer_valid_a.writerow(dataset_dict[sample][:-len(class_list)]+cl_li)

    print('Writing folds to ', './datasets/' + output_name + '/' + output_name + '_foldx' )