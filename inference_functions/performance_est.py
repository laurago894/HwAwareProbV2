from inference_functions import ac_inference
import sys
import random


def accuracy_estimation_mc(validation_set,indicator_dict,variable_list,NodesEv,init_weight,
                        operations_index,operation,content_ac,thres,classv):


    class_mv = NodesEv[-classv:]

    print('class mv is', class_mv)

    correct_count=0


    for test in validation_set:

        if test:
            observation = [int(t) for t in test.split(',')]

            gt = observation[-classv:]


            #Skip denominator computation, since we only need to find the largest class psterior prob,
            ratios = []
            nn=[]

            for class_num in class_mv:

                # chnage observation value of class variable
                observation[class_num-1] = 1

                makezero = [num for num in class_mv if class_num != num]

                for ma in makezero:
                    observation[ma - 1] = 0

                obs_var_num = NodesEv

                # print('Observation is ', observation)
                # print('obsvarnum', obs_var_num)

                # chnage observation value of class variable

                position_neg_num = [indicator_dict[variable_list[var] + '_' + str(value)] for value, var in
                                    zip(observation, variable_list) if var in obs_var_num]

                psn_num = [pos for position in position_neg_num for pos in position]

                init_weight_num = [w for w in init_weight]

                for psnum in psn_num:
                    init_weight_num[psnum] = 0


                wmc_num, w_num = ac_inference.performWMC(operations_index, operation, init_weight_num,
                                                          content_ac)

                # print(w_num)
                nn.append(w_num)

                rati = w_num


                ratios.append(rati)

            # print('gt:',gt,gt.index(1))
            # print('ratios:',ratios,ratios.index(max(ratios)))
            if gt.index(1) == ratios.index(max(ratios)):
                correct_count += 1

    accuracy = float(correct_count) / float(len(validation_set))


    return accuracy


def accuracy_estimation(validation_set,indicator_dict,variable_list,obs_var_den,init_weight,
                        operations_index,operation,content_ac,classes,obs_var_num,thres,**kwargs):

    correct_count=0
    all_ratios=[]

    for test in validation_set:

        if test:
            observation = [int(t) for t in test.split(',')]

            gt = observation[-1]

            #Set indicator values according to observation
            position_neg_den = [indicator_dict[variable_list[var] + '_' + str(value)] for value, var in
                                zip(observation, variable_list) if var in obs_var_den ]

            psn_den = [pos for position in position_neg_den for pos in position]

            init_weight_den = [w for w in init_weight]

            for psden in psn_den:
                init_weight_den[psden] = 0

            wmc_den, w_den= ac_inference.performWMC(operations_index, operation, init_weight_den,content_ac)

            w_den+= sys.float_info.min  #Avoid division by 0

            #Collect num/den ratio
            ratios = []
            nn=[]

            for classv in classes:

                # chnage observation value of class variable
                observation[-1] = classv
                position_neg_num = [indicator_dict[variable_list[var] + '_' + str(value)] for value, var in zip(observation, variable_list) if var in obs_var_num]

                psn_num = [pos for position in position_neg_num for pos in position]


                init_weight_num = [w for w in init_weight]

                for psnum in psn_num:
                    init_weight_num[psnum] = 0


                wmc_num, w_num= ac_inference.performWMC(operations_index, operation, init_weight_num,content_ac)

                nn.append(w_num)
                rati = w_num / w_den

                ratios.append(rati)
            all_ratios.append(ratios)

            conditions = [loc for loc, num in enumerate(ratios) if num >= thres]

            if len(conditions) == 1:
                if int(conditions[0]) == gt:
                    correct_count += 1
            elif len(conditions) > 1:
                if int(conditions.index(max(conditions))) == gt:
                    correct_count += 1

    accuracy=float(correct_count) / (len(validation_set))

    return accuracy

def metric_est(model,dataset,observed_features):


    content_ac=model[0]
    lmap_id=model[1]
    lmap_w=model[2]
    indicator_dict = model[5]
    variable_list=model[6]


    class_num = len(dataset[0].split(','))
    thres=0.5

    NodesEv = observed_features+[class_num]

    obs_var_num = NodesEv
    obs_var_den = observed_features



    classes = [0, 1]

    # Initialize weight vector
    init_weight = ac_inference.init_weight(content_ac, lmap_id, lmap_w)

    operations_index, operation =ac_inference.extract_operations(content_ac)

    #To verify WMC: w should be 1
    # wmc, w = inference_fcns.performWMC(operations_index, operation, init_weight, content_ac)
    # print 'w is ', w

    acc=accuracy_estimation(dataset, indicator_dict, variable_list, obs_var_den, init_weight,
                        operations_index, operation, content_ac, classes, obs_var_num, thres)

    par_num = sum([1 for ac in content_ac if 'L' in ac])
    add_num = sum([1 * len(ac.split(' ')) - 2 - 1 + 1 for ac in content_ac if 'O' in ac])
    mult_num = sum([1 * len(ac.split(' ')) - 3 - 1 + 1 for ac in content_ac if 'A' in ac])

    return [acc,par_num,add_num,mult_num]


def metric_est_mv(model,dataset,observed_features,nclasses):


    content_ac=model[0]
    lmap_id=model[1]
    lmap_w=model[2]
    indicator_dict = model[5]
    variable_list=model[6]


    class_num = len(dataset[0].split(','))
    thres=0.5

    NodesEv = observed_features+[class_num]


    # Initialize weight vector
    init_weight = ac_inference.init_weight(content_ac, lmap_id, lmap_w)

    operations_index, operation =ac_inference.extract_operations(content_ac)

    #To verify WMC: w should be 1
    # wmc, w = inference_fcns.performWMC(operations_index, operation, init_weight, content_ac)
    # print 'w is ', w

    acc=accuracy_estimation_mc(dataset, indicator_dict, variable_list, NodesEv, init_weight,
                        operations_index, operation, content_ac, thres,nclasses)

    par_num = sum([1 for ac in content_ac if 'L' in ac])
    add_num = sum([1 * len(ac.split(' ')) - 2 - 1 + 1 for ac in content_ac if 'O' in ac])
    mult_num = sum([1 * len(ac.split(' ')) - 3 - 1 + 1 for ac in content_ac if 'A' in ac])

    return [acc,par_num,add_num,mult_num]


def metric_est_feature_fail(model,dataset,observed_features,fail_sets):


    content_ac=model[0]
    lmap_id=model[1]
    lmap_w=model[2]
    indicator_dict = model[5]
    variable_list=model[6]


    class_num = len(dataset[0].split(','))
    thres=0.5

    NodesEv = observed_features+[class_num]

    obs_var_num = NodesEv
    obs_var_den = observed_features

    classes = [0, 1]

    init_weight = ac_inference.init_weight(content_ac, lmap_id, lmap_w)

    operations_index, operation =ac_inference.extract_operations(content_ac)

    accs_fail={}

    for fail in fail_sets:

        nfail = round(len(obs_var_den) * fail)
        print(nfail, ' features fail')

        accs=[]

        for trial in range(10):

            fi = random.sample(range(0, len(obs_var_num) - 1), int(nfail))
            print(fi)
            num_reduced = [num for ii, num in enumerate(obs_var_num) if ii not in fi]
            den_reduced = [num for ii, num in enumerate(obs_var_den) if ii not in fi]


            acc=accuracy_estimation(dataset, indicator_dict, variable_list, den_reduced, init_weight,
                            operations_index, operation, content_ac, classes, num_reduced, thres)

            accs.append(acc)
        accs_fail[fail]=accs

    return accs_fail
