import csv
import argparse
import sys, os
from util import functions
from operator import itemgetter
from itertools import groupby

import math


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)



#Condirional parameter estimation
def re_parameter(dataset,nclasses):


    fold=0
    fname = './datasets/' + dataset + '/' + dataset + '_fold' + str(
        fold) + '/' + dataset + '_fold' + str(fold) + '.train.data'

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

    class_vars=variables[-nclasses:]
    feature_vars = variables[:-nclasses]
    print('Class variables are ', class_vars)

    negative_locs_perclass={}
    positive_locs_perclass = {}

    checksum=0

    for cl in class_vars: #Find instances of 1 or 0 for each class

        negative_loc=[loc for loc,num in enumerate(features[cl]) if num==0]
        positive_loc=[loc for loc,num in enumerate(features[cl]) if num==1]

        negative_locs_perclass[cl]=negative_loc
        positive_locs_perclass[cl] =positive_loc

        checksum+=len(positive_loc)

    assert checksum==len(features[1]), ' Class variables are not mutually exclusive, labelling overlaps'



    cond_parameters={}

    cond_parameters[variables[-1]]=[len(negative_loc)/float(len(features[1])),len(positive_loc) / float(len(features[1]))]
    alpha=0.5 #For Laplace smoothing
    for var in feature_vars:
        probs=[]
        print('\n\n for feature ', var)
        for cl in class_vars:

            print('class ', class_vars.index(cl))

            # neg_class_instances=itemgetter(*negative_locs_perclass[cl])(features[var])
            # pos_neg_class_instances=sum(neg_class_instances) / float(len(neg_class_instances))

            pos_class_instances=itemgetter(*positive_locs_perclass[cl])(features[var])
            pos_pos_class_instances=(sum(pos_class_instances)+(1*alpha)) / float(len(pos_class_instances)+(2*alpha))

            # print 'Pr(', var, '|not',cl, ')=', pos_neg_class_instances
            print('Pr(', var, '|', cl, ')=', pos_pos_class_instances)

            probs.append(pos_pos_class_instances)

        cond_parameters[(var)]=probs #Pr(var|notclass), Pr(var|class)

    ## Conditional probabilities of class variables
    ## We encode mutual exclusitivy in the vtree and the initial PSDD
    ## The vtree structure and resulting PSDD requires the following probabilities:
    ## Pr(Cn-1|~Cn),Pr(~Cn-1|~Cn)
    ## Pr(Cn-2|~Cn,~Cn-1), Pr(~Cn-2|~Cn,~Cn-1)
    ## Pr(Cn-3|~Cn,~Cn-1,~Cn-2), Pr(~Cn-3|~Cn,~Cn-1,~Cn-2)
    ## Pr(Cn-4|~Cn,~Cn-1,~Cn-2,~Cn-3), Pr(~Cn-4|~Cn,~Cn-1,~Cn-2,~Cn-3)
    ## ...

    class_nums=range(0,len(class_vars))

    conditioning_var=[]
    disallowed_locations=[] #Instances where the conditionung class is positive

    cond_class_probs={}

    for icl,cl in zip(reversed(class_nums),reversed(class_vars)): #Find instances of 1 or 0 for each class

        print('\nClass ', icl, ' varn ', cl)

        feat_vect=features[cl]

        print('THere are ', len(disallowed_locations), ' disallowed locations')

        complying_feat_vect=[num for inum,num in enumerate(feat_vect) if inum not in disallowed_locations]

        assert len(complying_feat_vect)==len(feat_vect)-len(disallowed_locations), ' Conditions not met '

        neg_condprob=(len(complying_feat_vect)-sum(complying_feat_vect) + alpha) / (len(complying_feat_vect)+ (2*alpha))    #Pr( not current class | condition of negation on class it depends on)
        pos_condprob=(sum(complying_feat_vect) + alpha)/(len(complying_feat_vect) + (2*alpha))   #Pr(current class | condition of negation on class it depends on)

        cond_class_probs[cl]=[neg_condprob,pos_condprob]

        print('Pr(~', cl, '|larger classes)',neg_condprob)
        print('Pr(', cl, '|larger classes)',pos_condprob)

        print('Class ', cl, ' has ', len(positive_locs_perclass[cl]), ' positive instances')

        disallowed_locations=disallowed_locations+positive_locs_perclass[cl]

    return (cond_parameters,cond_class_probs,feature_vars,class_vars)


def vtree_psdd(dataset,vtree_type,fold,cond_parameters): #Load vtree

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

    conditional_probs=cond_parameters[0]
    conditional_class_probs = cond_parameters[1]
    feature_variables=cond_parameters[2]
    class_variables=cond_parameters[3]


    bench_name=dataset
    vtree_name = './learned_models/vtrees/'+ bench_name +'/' + bench_name + '_fold'+ str(fold) +'_' + vtree_type + '.vtree'


    print('\n\nReading vtree from ', vtree_name)

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



    variable_type = ['neg', 'pos']

    psdd_id=0

    true_node_id={}  # {vtree_id:[psdd_id,variable_num]}
    psdd=[]

    for interval in intervals[:-(2*len(class_variables))]:
        line_nums=range(interval[1][0], interval[1][1])
        lines = [vtree_lines[num] for num in line_nums]
        line_type = interval[0]

        for vtype in range(0,len(class_variables)):
            for line in lines:
                if line_type == 'L':
                    psdd_id += 3
                    vtree_id=line[1]
                    variable_num=line[2]
                    newline = 'T ' + str(psdd_id) + ' ' + vtree_id + ' ' + variable_num  + ' ' + str(math.log(conditional_probs[int(line[2])][vtype]+sys.float_info.min))

                    true_node_id[(vtree_id,vtype)]=[str(psdd_id),variable_num]

                if line_type == 'I':
                    vtree_id=line[1]
                    left_child_prime=line[2]
                    right_child_sub=line[3]
                    #Find psdd id of vtree node
                    left_child_id=true_node_id[(left_child_prime,vtype)][0]
                    right_child_id = true_node_id[(right_child_sub, vtype)][0]
                    psdd_id+=1
                    newline='D ' + str(psdd_id) + ' ' + vtree_id + ' 1 ' + left_child_id +' ' + right_child_id + ' 0.0'
                    true_node_id[(vtree_id, vtype)] = [str(psdd_id)]

                psdd.append(newline)

    last_lines=2*len(class_variables)
    int_final=intervals[-last_lines:]
    # PSDD_mutal_exc(conditional_class_probs, class_variables,int_final,vtree_lines,psdd_id)


    pairs_lines=[]

    for leaf_line, inode_line in pairwise(intervals[-(2*len(class_variables)):]):
        pairs_lines.append((leaf_line,inode_line))

    nclasses=len(class_variables)

    revclass=[n for n in reversed(class_variables)]

    for nc,ndec in enumerate(reversed(range(1,nclasses+1))):


        linterval=pairs_lines[nc][0]
        ninterval=pairs_lines[nc][1]

        #Insert leaves
        line_nums = range(linterval[1][0], linterval[1][1])
        lines = [vtree_lines[num] for num in line_nums]
        vtree_id = lines[0][1]
        variable_num = lines[0][2]
        psdd_id += 1
        # print 'Vtree id ', vtree_id, ' variable num ', variable_num, ' psdd id ', psdd_id
        newline = 'L ' + str(psdd_id) + ' ' + vtree_id + ' -' + variable_num
        true_node_id[(vtree_id, 0)] = [str(psdd_id)]
        psdd.append(newline)
        true_node_id[(vtree_id, 'neg')] = [str(psdd_id), variable_num]

        psdd_id += 1
        newline = 'L ' + str(psdd_id) + ' ' + vtree_id + ' ' + variable_num
        true_node_id[(vtree_id, 0)] = [str(psdd_id)]
        psdd.append(newline)
        true_node_id[(vtree_id, 'pos')] = [str(psdd_id), variable_num]


        line_nums = range(ninterval[1][0], ninterval[1][1])
        lines = [vtree_lines[num] for num in line_nums]
        vtree_id = lines[0][1]
        variable_num = lines[0][2]


        left_child_prime = lines[0][2]
        right_child_sub = lines[0][3]
        for dec in range(ndec):
            psdd_id += 1
            # Find psdd id of vtree node
            # print 'Inserting decision node corresponding to ', dec, ' of ', ndec

            #Normally the first decision node will have two children, expect for the first (rightmost) class
            if nc==0:
                # print 'This decision node has one child'
                if dec==0:
                    #Here the curent class is positice
                    left_child_id = true_node_id[(left_child_prime, 'pos')][0]
                    right_child_id = true_node_id[(right_child_sub, dec)][0]
                else:
                    #Hre the current class is negative
                    left_child_id = true_node_id[(left_child_prime, 'neg')][0]
                    right_child_id = true_node_id[(right_child_sub, dec)][0]
                newline=  'D ' + str(psdd_id) + ' ' + vtree_id + ' 1 ' + left_child_id + ' ' + right_child_id + ' 0.0'
                psdd.append(newline)
                true_node_id[(vtree_id, dec)] = [str(psdd_id), variable_num]

            if nc>0:
                if dec==0:
                    # print 'This decision node has two children'
                    #Here the curent class is positice

                    prime_left_child=true_node_id[(left_child_prime, 'pos')][0]#This is the true node of the current class
                    prime_right_child=true_node_id[(right_child_sub, nc)][0]  # This is the last inserted decision node, corresponds to current class

                    sub_left_child=true_node_id[(left_child_prime, 'neg')][0]#This is the true node of the current class
                    sub_right_child=true_node_id[(right_child_sub, nc-1)][0]  # This is the last inserted decision node, corresponds to current class

                    # print 'The class parameter is ', revclass[nc+1]

                    newline = 'D ' + str(psdd_id) + ' ' + vtree_id + ' 2 ' + prime_left_child + ' ' + prime_right_child + ' ' \
                              + str(math.log(conditional_class_probs[class_variables[nc]][1])) \
                              + ' ' + sub_left_child + ' ' + sub_right_child + ' ' + str(math.log(conditional_class_probs[class_variables[nc]][0]+sys.float_info.min))

                    psdd.append(newline)
                    true_node_id[(vtree_id, dec+nc)] = [str(psdd_id), variable_num]
                    # print 'Updating true node id with [vtree=', vtree_id, ' classn dec=', dec, ']=[', str(
                    #     psdd_id), variable_num, ']'
                else:
                    # print 'This decision node has one child'
                    # print 'Left child is negative'
                    left_child = true_node_id[(left_child_prime, 'neg')][0]
                    # print 'For right chilc class is ', dec+1, 'dec is ', dec
                    right_child=true_node_id[(right_child_sub, nc+dec)][0]  # This is the last inserted decision node, corresponds to current class
                    # print 'Left  child ', left_child, ' right child ', right_child
                    newline = 'D ' + str(psdd_id) + ' ' + vtree_id + ' 1 ' + left_child + ' ' + right_child + ' 0.0'

                    psdd.append(newline)
                    true_node_id[(vtree_id, dec+nc)] = [str(psdd_id), variable_num]

    ####Write PSDD to file

    # assert len(psdd)==(len(vtree_lines)*2*nclasses)-1, ' wrong number of psdd lines, it has ' + str(len(psdd)) +' should be '+str((len(vtree_lines)*2*nclasses)-1)

    psdd_name = './learned_models/psdds/' + bench_name + '/' + bench_name + '_fold' + str(
            fold) + '_' + vtree_type + '_init.psdd'

    if not os.path.exists('./learned_models/psdds/' + bench_name + '/'):
        os.makedirs('./learned_models/psdds/' + bench_name + '/')

    with open(psdd_name,'w') as psf:
        for line in header:
            psf.write(line+'\n')
        psf.write('psdd ' +str(len(psdd)) + '\n')
        for row in psdd[:-1]:
            psf.write(row+'\n')
        psf.write(psdd[-1])

    psf.close()

    print('Writing  naive bayes psdd to ', psdd_name)




def run(args):

    dataset=args.inputBenchmark
    nclasses = int(args.class_num)

    vtree_types = ['gen_mi', 'gen_cmi']

    for fold in range(5):

        (cond_probs,class_cond_probs,feature_vars,class_vars)=re_parameter(dataset,nclasses)


        for vt in vtree_types:
            vtree_psdd(dataset,vt,fold,(cond_probs,class_cond_probs,feature_vars,class_vars))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Re-write PSDD to AC and test WMC without evidence')
    parser.add_argument('inputBenchmark', help='Provide the name of the benchmark')
    parser.add_argument('-class_num', '--class_num', type=str, default='1', help='How many class variables are  there')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())


