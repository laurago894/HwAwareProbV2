import itertools
import random
import os, csv

def generate_folds(dataset_dict,folds,output_name):

    fold_size = int(len(dataset_dict) / folds)
    num_instances = range(len(dataset_dict))

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
        fold_test = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.test.data'
        fold_valid = './datasets/' + output_name + '/' + output_name + '_fold' + str(
            fold) + '/' + output_name + '_fold' + str(fold) + '.valid.data'

        if not os.path.exists('./datasets/' + output_name + '/' + output_name + '_fold' + str(fold)):
            os.makedirs('./datasets/' + output_name + '/' + output_name + '_fold' + str(fold))

        with open(fold_train, mode='w') as train_file, open(fold_test, mode='w') as test_file, open(fold_valid,
                                                                                                    mode='w') as valid_file:

            writer_train = csv.writer(train_file, delimiter=',')
            writer_test = csv.writer(test_file, delimiter=',')
            writer_valid = csv.writer(valid_file, delimiter=',')

            test_samples = ranges_dict[fold]
            train_folds = [f for f in list(range(folds)) if f != fold]
            train_samples = list(itertools.chain.from_iterable([ranges_dict[f] for f in train_folds]))

            # Randomly sample 10% for validation -- model learning purposes
            valid_samples = random.sample(train_samples, int(len(dataset_dict) / 10))
            [train_samples.pop(train_samples.index(num)) for num in valid_samples]

            # Check if sets are mutually exclusive
            # print(len(list(set(list(set(train_samples))+list(set(test_samples))+list(set(valid_samples))))))
            for sample in train_samples:
                writer_train.writerow(dataset_dict[sample])
            for sample in test_samples:
                writer_test.writerow(dataset_dict[sample])
            for sample in valid_samples:
                writer_valid.writerow(dataset_dict[sample])

    print('Writing folds to ', './datasets/' + output_name + '/' + output_name + '_foldx' )