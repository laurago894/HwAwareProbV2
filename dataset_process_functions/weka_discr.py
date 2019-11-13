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

    f = open('./datasets/' + output_name + '/' + output_name + 'discr_weka.arff', 'w')

    process = subprocess.Popen(
        ['java', '-classpath', weka_location + '/weka.jar',
         'weka.filters.supervised.attribute.Discretize', '-i', input_dataset, '-c', 'last', '-R', 'first-last',
         '-precision', '6'],
        stdout=f)

    stdout, stderr = process.communicate()


    fb = open('./datasets/' + output_name + '/' + output_name + '_bin_weka.arff', 'w')


    process2 = subprocess.Popen(
        ['java', '-classpath', weka_location + '/weka.jar',
         'weka.filters.supervised.attribute.NominalToBinary', '-i', './datasets/' + output_name + '/' + output_name + 'discr_weka.arff', '-c', 'last'],stdout=fb)

    stdout, stderr = process2.communicate()


    print("Discretized dataset written to " + '/datasets/' + output_name + '/' + output_name + '_discr_weka.arff')

    print("Binarized dataset written to " + '/datasets/' + output_name + '/' + output_name + '_bin_weka.arff')

    d_dict=rewrite_arff(output_name)

    return d_dict


def rewrite_arff(output_name):

    weka_discr = './datasets/' + output_name + '/' + output_name + '_bin_weka.arff'
    output_discr = './datasets/' + output_name + '/' + output_name + '_bin.csv'

    file_list=functions.read_file(weka_discr)

    values=[]

    attr_locs=[line for line in file_list if "@attribute" in line]
    class_values=attr_locs[-1].split(' ')[2].strip('{').strip('}').split(',')

    for line in file_list:
        if "@attribute" in line:
            values.append(line.split(' ')[2].strip('{').strip('}').split(','))


    dataset=file_list[(file_list.index('@data'))+2:]

    features={}

    #Remove variables that are always 0
    for il, line in enumerate(dataset):
        for inn,num in enumerate(line.split(',')[:-1]):
            if il==0:
                features[inn]=[int(num)]
            else:
                features[inn]=features[inn]+[int(num)]

    remove_f=[]
    for feat in features:
        if sum(features[feat])==0:
            remove_f.append(feat)

    print('There are ', len(features), ' binary features')
    print('Ignoring features ', remove_f)

    dataset_dict={}

    with open(output_discr, mode='w') as bin_file:
        writer = csv.writer(bin_file, delimiter=',')
        for il,line in enumerate(dataset):

            linelist =[num for inum,num in enumerate(line.split(',')) if inum not in remove_f]
            feature_list=list(range(0,len(linelist)-1))
            if len(class_values)==2:
                linelist[-1]=class_values.index(linelist[-1])
                classes_list=[len(linelist)-1]
            else:
                classes_list = list(range(len(feature_list),len(feature_list)+len(class_values) ))
                classlist=[0]*len(class_values)
                classlist[class_values.index(linelist[-1])]=1
                del linelist[-1]
                linelist=linelist+classlist
            writer.writerow(linelist)
            dataset_dict[il]=linelist

    print('Writing reformatted binarized dataset to ', output_discr)
    return dataset_dict,feature_list,classes_list


