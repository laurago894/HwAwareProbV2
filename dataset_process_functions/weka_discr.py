import subprocess
import os
from util import functions
import csv
import itertools
import random

def weka_supervised_discr(input_dataset,output_name):

    weka_location = '/users/micas/lgalinde/Documents/Projects_share/weka/weka-3-8-0'

    if not os.path.exists('./datasets/' + output_name):
        os.makedirs('./datasets/' + output_name)

    f = open('./datasets/' + output_name + '/' + output_name + '_bin_weka.arff', 'w')

    process = subprocess.Popen(
        ['java', '-classpath', weka_location + '/weka.jar',
         'weka.filters.supervised.attribute.Discretize', '-i', input_dataset, '-c', 'last', '-D', '-R', 'first-last',
         '-precision', '6'],
        stdout=f)

    print("Discretized dataset written to " + '/datasets/' + output_name + '/' + output_name + '_bin_weka.arff')

    stdout, stderr = process.communicate()

    d_dict=rewite_arff(output_name)

    return d_dict


def rewite_arff(output_name):

    weka_discr = './datasets/' + output_name + '/' + output_name + '_bin_weka.arff'
    output_discr = './datasets/' + output_name + '/' + output_name + '_bin.csv'

    file_list=functions.read_file(weka_discr)

    # 5 folds is the default
    folds=5

    values=[]

    for line in file_list:
        if "@attribute" in line:
            values.append(line.split(' ')[2].strip('{').strip('}').split(','))


    dataset=file_list[(file_list.index('@data'))+2:]

    dataset_dict={}

    with open(output_discr, mode='w') as bin_file:
        writer = csv.writer(bin_file, delimiter=',')
        for il,line in enumerate(dataset):
            linelist = line.split(',')
            writer.writerow([val.index(dat) for dat, val in zip(linelist, values)])
            dataset_dict[il]=[val.index(dat) for dat, val in zip(linelist, values)]

    print('Writing reformatted binarized dataset to ', output_discr)


    return dataset_dict


