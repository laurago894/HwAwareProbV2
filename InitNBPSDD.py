import csv
import argparse
import sys
from util import functions
from operator import itemgetter
from itertools import groupby
import math

#Run the generate_vtrees_order.py if needed




#Condirional parameter estimation
def re_parameter(fname):



    reader=csv.reader(open(fname,'r'),delimiter=',',quoting=csv.QUOTE_NONNUMERIC)

    dataset=[]
    for line in reader:
        dataset.append(line)

    variables=[num+1 for num in  range(0,len(dataset[0]))]

    features={}
    for var in variables:
        features[var]=[]

    for row in dataset:
        for var in variables:
            features[var].append(row[var-1])

    class_var=variables[-1]

    negative_loc=[loc for loc,num in enumerate(features[class_var]) if num==0]
    positive_loc=[loc for loc,num in enumerate(features[class_var]) if num==1]


    cond_parameters={}

    cond_parameters[variables[-1]]=[len(negative_loc)/float(len(features[1])),len(positive_loc) / float(len(features[1]))]

    #For Laplace smoothing
    alpha=0.5

    for var in variables[:-1]:

        neg_class_instances=itemgetter(*negative_loc)(features[var])
        # neg_neg_class_instances=(len(neg_class_instances)-sum(neg_class_instances)) / float(len(neg_class_instances))
        pos_neg_class_instances=(sum(neg_class_instances)+alpha) / (float(len(neg_class_instances))+2*alpha)

        pos_class_instances=itemgetter(*positive_loc)(features[var])
        # neg_pos_class_instances=(len(pos_class_instances)-sum(pos_class_instances)) / float(len(pos_class_instances))
        pos_pos_class_instances=(sum(pos_class_instances)+alpha) / (float(len(pos_class_instances))+2*alpha)


        cond_parameters[var]=[pos_neg_class_instances,pos_pos_class_instances]  #Pr(var|notclass), Pr(var|class)

    # print(cond_parameters)

    return cond_parameters


def vtree_psdd(bench_name,fold,vtree_type,cond_parameters):


    header=['c ids of psdd nodes start at 0',
            'c psdd nodes appear bottom-up',
            'children before parents',
            'c',
            'c file syntax:',
            'c psdd count-of-sdd-nodes',
            'c L id-of-literal-sdd-node literal',
            'c T id-of-trueNode-sdd-node id-of-vtree trueNode variable log(litProb)',
            'c D id-of-decomposition-sdd-node id-of-vtree number-of-elements {id-of-prime id-of-sub log(elementProb)}*',
            'c']

    vtree_name = './learned_models/vtrees/'+ bench_name +'/' + bench_name + '_fold'+ str(fold) +'_' + vtree_type + '.vtree'


    print('Reading vtree from ', vtree_name)

    vtree=functions.read_file(vtree_name)

    vtree_lines=[vt.split(' ') for vt in vtree if 'c' not in vt and 'vtree' not in vt]
    node_types=[line[0] for line in vtree_lines]
    node_ids=[int(line[1]) for line in vtree_lines]
    grouped_L = [(k, sum(1 for i in g)) for k,g in groupby(node_types)]

    intervals=[]
    counter=0
    for group in grouped_L:
        intervals.append((group[0], [counter,group[1]+counter],node_ids[counter:group[1]+counter]))  #(node type, range, ids within range )
        counter+=group[1]


    psdd_id=0

    true_node_id={}  #
    psdd=[]

    for interval in intervals[:-2]:
        line_nums=range(interval[1][0], interval[1][1])
        lines = [vtree_lines[num] for num in line_nums]
        line_type = interval[0]
        for vtype in [0,1]:
            for line in lines:
                if line_type == 'L':
                    psdd_id += 3
                    vtree_id=line[1]
                    variable_num=line[2]
                    newline = 'T ' + str(psdd_id) + ' ' + vtree_id + ' ' + variable_num  + ' ' + str(math.log(cond_parameters[int(line[2])][vtype]+sys.float_info.min))
                    true_node_id[(vtree_id,vtype)]=[str(psdd_id),variable_num]

                if line_type == 'I':
                    vtree_id=line[1]
                    left_child_prime=line[2]
                    right_child_sub=line[3]
                    left_child_id=true_node_id[(left_child_prime,vtype)][0]
                    right_child_id = true_node_id[(right_child_sub, vtype)][0]
                    psdd_id+=1
                    newline='D ' + str(psdd_id) + ' ' + vtree_id + ' 1 ' + left_child_id +' ' + right_child_id + ' 0.0'
                    true_node_id[(vtree_id, vtype)] = [str(psdd_id)]
                psdd.append(newline)

    line_nums = range(intervals[-2][1][0], intervals[-2][1][1])
    lines = [vtree_lines[num] for num in line_nums]
    vtree_id=lines[0][1]
    variable_num = lines[0][2]
    psdd_id+=1
    newline='L ' +str(psdd_id) + ' ' + vtree_id + ' -' + variable_num
    true_node_id[(vtree_id, 0)] = [str(psdd_id)]
    psdd.append(newline)

    psdd_id+=1
    newline = 'L ' + str(psdd_id) + ' ' + vtree_id + ' ' + variable_num
    true_node_id[(vtree_id, 1)] = [str(psdd_id)]
    psdd.append(newline)

    last_line=vtree_lines[-1]
    psdd_id+=1
    vtree_id = last_line[1]

    left_child_prime = last_line[2]
    right_child_sub = last_line[3]

    left_child_id_sub = true_node_id[(left_child_prime, 0)][0]
    left_child_id_prime = true_node_id[(left_child_prime, 1)][0]
    right_child_id_sub = true_node_id[(right_child_sub, 0)][0]
    right_child_id_prime = true_node_id[(right_child_sub, 1)][0]


    newline = 'D ' + str(psdd_id) + ' ' + vtree_id + ' 2 ' + left_child_id_prime  + ' ' + right_child_id_prime + ' ' + str(math.log(cond_parameters[int(variable_num)][1])) \
              + ' ' + left_child_id_sub  + ' ' + right_child_id_sub + ' ' + str(math.log(cond_parameters[int(variable_num)][0]))
    psdd.append(newline)


    assert len(psdd)==(len(vtree_lines)*2)-1, ' wrong number of psdd lines'


    psdd_name='./learned_models/psdds/'+ bench_name +'/'+ bench_name +'_fold' + str(fold) + '_'+ vtree_type +'_init.psdd'
    print('Writing nb structured PSDD ', psdd_name)

    with open(psdd_name,'w') as psf:
        for line in header:
            psf.write(line+'\n')
        psf.write('psdd ' +str(len(psdd)) + '\n')
        for row in psdd[:-1]:
            psf.write(row+'\n')
        psf.write(psdd[-1])

    psf.close()


def run(args):

    bench_name=args.bench_name
    vtree_types = ['gen_mi', 'gen_cmi']

    for fold in range(5):

        dataset_name='./datasets/' + bench_name +'/'+ bench_name +'_fold' + str(fold) +'/'+ bench_name +'_fold' + str(fold) + '.train.data'

        cond_probs=re_parameter(dataset_name)

        for vt in vtree_types:
            vtree_psdd(bench_name,fold,vt,cond_probs)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Generate initial PSDD with naive Bayes like structure')
    parser.add_argument('bench_name', help='Provide the name of the benchmark')


    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())


