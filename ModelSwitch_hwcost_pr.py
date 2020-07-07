from util import Pareto_functions, functions
import numpy as np
from PSDD_functions import PSDD_to_AC_pruned
import argparse, sys
from inference_functions import performance_est, ac_inference
from precision_reduction import FixedPointImplementation
import random, sys

def extract_intervals(minacc,maxcost,pareto_filename):


    # minacc=0.68
    # maxcost=0.45

    maxcosts={'gen':1946000,'gen_cmi':1946000}
    ranges=list(reversed(list(np.linspace(0.1,maxcost,11))))

    print('ranges is ', ranges)

    model_type=['gen','gen_cmi']
    paretos={}
    norm_costs={}
    model_interval=[]

    for ir,range in enumerate(ranges[:-1]):
        model_specs={}
        for ty in model_type:
            files_dir='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/pruning_'+ty+'_hwcost/'

            # outfile=files_dir+'/pareto_final.csv'
            outfile = files_dir + '/' + pareto_filename

            off=functions.read_file(outfile)

            paretos[ty]=off

            nc=[]
            ac=[]
            list_pareto=[]


            for par in off:
                list_pareto.append(par.split(','))
                nc.append(float(par.split(',')[2])/maxcosts[ty])
                ac.append(float(par.split(',')[1]))


            # print(ranges[ir])
            belong_range=[ii for ii,co in enumerate(nc) if co<ranges[ir] and co>=ranges[ir+1]]
            # print([ac[ii] for ii in belong_range])
            if belong_range:
                print('ii is ',belong_range[0])
                li_range=list_pareto[belong_range[0]]
                mod_spec=li_range[0].split('-')
                print('mod spec is ', mod_spec)
                print('li range ', li_range)
                model=mod_spec[0].strip('model')
                feats=[int(num) for num in mod_spec[1:-1]]
                bits=int(mod_spec[-1].strip('bits'))
                print('Bits ', bits)
                li_range[1]=float(li_range[1])
                li_range[2] =float(li_range[2])/maxcosts[ty]

                print('model ',model)
                print('feats ', feats)
                print('li range ', li_range)
                print('acc',ac[belong_range[0]])
                full_model_spec=[(model,feats,bits)]+li_range[1:]
                print('Full spec ', full_model_spec)

                model_specs[ty]=full_model_spec

        model_interval.append(model_specs)

    print('Model interval ')
    for mod in model_interval:
        print(mod,'\n')

    final_inters=[]
    valid_accs_gen=[]
    valid_accs_gen_cmi = []
    costs_gen=[]
    costs_gen_cmi=[]

    for inter,interval in enumerate(model_interval):
        if interval:
            # print('\n')
            # print('interval ', interval)
            # print('acc ', interval['gen'][1], interval['gen_cmi'][1])
            # print('cost ', interval['gen'][2], interval['gen_cmi'][2])
            if 'gen' in interval and 'gen_cmi' in interval:
                valid_accs_gen.append(interval['gen'][1])
                valid_accs_gen_cmi.append(interval['gen_cmi'][1])
                costs_gen.append(interval['gen'][2])
                costs_gen_cmi.append(interval['gen_cmi'][2])


                if not(interval['gen'][1]<minacc or interval['gen_cmi'][1]<minacc or interval['gen'][2]>maxcost or interval['gen_cmi'][2]>maxcost):
                    final_inters.append(interval)

    print(len(final_inters),len(model_interval))



    intervals_fn_perf='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/model_switch_hwcost/intervals'+ str(len(final_inters)) +'_acc_cost_'+ str(minacc) +'_' + str(maxcost) +'.csv'
    # intervals_fn_models = '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/model_switch_hwcost/interval_models.csv'

    intervals_w=open(intervals_fn_perf,'w')
    intervals_w.write((',').join([str(num) for num in valid_accs_gen])+'\n')
    intervals_w.write((',').join([str(num) for num in valid_accs_gen_cmi]) + '\n')
    intervals_w.write((',').join([str(num) for num in costs_gen])+'\n')
    intervals_w.write((',').join([str(num) for num in costs_gen_cmi]) + '\n')

    intervals_w.close()
    print('Interval info written to ', intervals_fn_perf)

    print('\n\nFinal inters')
    for fi in final_inters:
        print('gen',fi['gen'])
        print('gen cmi ', fi['gen_cmi'])
        print('\n')


    print('valid accs gen',valid_accs_gen)
    print('valid accs gen cmi',valid_accs_gen_cmi)
    print('costs gen',costs_gen)
    print('costs gen cmi',costs_gen_cmi)

    return final_inters

########
def single_prediction(class_mv,NodesEv,observation, variable_list,init_weight,operations_index, operation,content_ac,indicator_dict):

    ratios=[]

    for class_num in class_mv:

        # chnage observation value of class variable
        observation[class_num - 1] = 1

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


        rati = w_num

        ratios.append(rati)


    return ratios


    ##########################################################

########
def single_prediction_flp(class_mv,NodesEv,observation, variable_list,init_weight,operations_index, operation,content_ac,indicator_dict,EXP_L,MANT_L):

    ratios=[]

    for class_num in class_mv:

        # chnage observation value of class variable
        observation[class_num - 1] = 1

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

        wmc_num, w_num = ac_inference.performWMC_red_prec(operations_index, operation, init_weight_num,
                                                 content_ac,EXP_L,MANT_L,0)


        rati = FixedPointImplementation.custom_flt_to_flt(w_num, EXP_L, MANT_L, 0)

        ratios.append(rati)


    return ratios


    ##########################################################



def run(args):
    # out_dir='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/model_switch_periodic/'

    minacc=float(args.min_max.split(',')[0])
    maxcost=float(args.min_max.split(',')[1])

    inters=extract_intervals(minacc,maxcost,args.pf)
    print(inters)


    type_data='test'


    # dataset=functions.read_file('/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/har_mv/har_mv_fold0/har_mv_fold0.'+type_data+'.data')
    # test_dataset='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/har_mv/har_mv_fold0/har_mv_order_20_30.test.data'
    test_dataset=args.test_dataset

    dataset=functions.read_file(test_dataset)

    valid=dataset

    tys=['gen','gen_cmi']
    #[exp,mant]
    bit_sets={32:[8,24],16:[5,11],8:[4,4]}


    ###### Save all models in data struct for fetching when needed
    ##List of dicts

    all_obs_feats=[]
    all_ac_models=[]
    all_model_num=[]
    all_bits=[]
    all_weights=[]
    all_costs=[]


    for inter in inters:

        obs_feats={}
        ac_models={}
        models={}
        bits={}
        ws=[]
        cos=[]

        for ty in tys:
            mod = inter[ty][0][0]
            obf = inter[ty][0][1]
            bt = inter[ty][0][2]
            acm = PSDD_to_AC_pruned.convert_psdd(
                '/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/har_mv/har_mv_fold0_' + ty + '/models/' + '/0-' + mod + '.psdd')

            obs_feats[ty]=obf
            ac_models[ty]=acm
            models[ty]=mod
            bits[ty]=bt

            ws.append(inter[ty][1])
            cos.append(inter[ty][2])

        ws = [w / sum(ws) for w in ws]
        #
        all_obs_feats.append(obs_feats)
        all_ac_models.append(ac_models)
        all_model_num.append(models)
        all_bits.append(bits)
        all_weights.append(ws)
        all_costs.append(cos)



    ##################################

    used_intervals=[]
    used_classifier_type=[]
    used_costs=[]
    used_cfs=[]
    corrects_gen=[]
    corrects_gen_cmi=[]

    #considers also iterations needed for selection
    total_iters_costs=[]
    total_iters_intervals=[]
    total_iters_accepts=[]

    probs_gen=[]
    probs_gen_cmi=[]

    correct_count=0
    all_preds=[[],[]]


    cf_buffer=[]
    counter_corrects=[]

    initial_interval=0
    current_interval=initial_interval
    check=0

    # th1=0.2
    # th2=0.99
    th1=float(args.th1)
    th2 =float(args.th2)

    # periods=[1,1]
    periods=[int(num) for num in args.periods.split(',')]
    #
    check_period = random.randint(periods[0], periods[1])
    for it,test in enumerate(dataset):
        check+=1
        accept_flag=0
        # check+=1
        while not accept_flag:

            print('\ncurrent interval is ', current_interval)
            print('Current count is ', check)
            print('Current check is ', check_period)
            # used_intervals.append(current_interval)

            accept_flag=0
            print('Sample ', it, ' of ', len(dataset))

            # ty='gen'

            ratios_pair=[]
            win_classes=[]
            correct_pred=[0,0]

            weights = all_weights[current_interval]
            costs = all_costs[current_interval]

            total_iters_costs.append(sum(costs))
            total_iters_intervals.append(current_interval)

            for ity,ty in enumerate(tys):
                # model=models[ty]
                observed_features=all_obs_feats[current_interval][ty]
                ac_model=all_ac_models[current_interval][ty]
                nbits=all_bits[current_interval][ty]


                model=ac_model

                content_ac = model[0]
                lmap_id = model[1]
                lmap_w = model[2]
                indicator_dict = model[5]
                variable_list = model[6]
                classv=6
                class_num = len(dataset[0].split(','))

                NodesEv = observed_features + [class_num]

                # Initialize weight vector
                init_weight = ac_inference.init_weight(content_ac, lmap_id, lmap_w)

                operations_index, operation = ac_inference.extract_operations(content_ac)

                class_mv = NodesEv[-classv:]


                if test:
                    observation = [int(t) for t in test.split(',')]
                    gt = observation[-classv:]

                    if nbits==64:
                        ratios=single_prediction(class_mv, NodesEv, observation, variable_list, init_weight, operations_index, operation,
                                          content_ac, indicator_dict)

                    else:
                        print('Bits: ', nbits)
                        EXP_L=bit_sets[nbits][0]
                        MANT_L = bit_sets[nbits][1]
                        init_weight_fl = [FixedPointImplementation.flt_to_custom_flt(w, EXP_L, MANT_L, 0, 0) for w in init_weight]
                        ratios = single_prediction_flp(class_mv, NodesEv, observation, variable_list, init_weight_fl,
                                               operations_index, operation,
                                               content_ac, indicator_dict,EXP_L,MANT_L)


                    ratios=[rat+sys.float_info.min for rat in ratios]
                    ratios = [rat / sum(ratios) for rat in ratios]

                    ratios_pair.append(ratios)

                    if ity==0:
                        probs_gen.append(ratios[ratios.index(max(ratios))])

                    if ity==1:
                        probs_gen_cmi.append(ratios[ratios.index(max(ratios))])

                    win_classes.append(ratios.index(max(ratios)))

                    if gt.index(1) == ratios.index(max(ratios)):
                        correct_pred[ity]=1
                        all_preds[ity].append(1)
                    else:
                        all_preds[ity].append(0)


            gamma = [-1 * (win_classes.index(cl) + (win_classes.index(cl) - 1)) for icl, cl in enumerate(win_classes)]


            print('Predictions ', correct_pred)
            print('Win classes ', win_classes)
            print('ratios',ratios_pair)
            print('weights',weights)
            print('gamma',gamma)
            cf = abs(sum([pp * w * g for pp, w, g in zip([max(rp) for rp in ratios_pair], weights, gamma)]))
            P_weight = [pp * w  for pp, w in zip([max(rp) for rp in ratios_pair], weights)]
            print('CF ', cf)
            used_cfs.append(cf)

####################################################
            if check == check_period:
                print('CHECK')

                if cf<th1:
                    if current_interval==0:
                        accept_flag=1
                        check=0
                        check_period = random.randint(periods[0], periods[1])
                    elif current_interval > 0:
                        print('Warning!!!')
                        current_interval-=1
                        print('Interval now changes to ', current_interval)
                else:
                    accept_flag=1
                    check = 0
                    check_period = random.randint(periods[0], periods[1])
                    pred_classifier=P_weight.index(max(P_weight))
                    if cf>th2:
                        if current_interval<len(inters)-1:
                            current_interval+=1
            else:
                accept_flag = 1
                pred_classifier = P_weight.index(max(P_weight))
########################################################
            # accept_flag=1
            # pred_classifier = P_weight.index(max(P_weight))
            # pred_classifier = 0

            total_iters_accepts.append(accept_flag)



        ratios_used=ratios_pair[pred_classifier]

        used_intervals.append(current_interval)
        used_classifier_type.append(tys[pred_classifier])
        used_costs.append(costs[pred_classifier])
        print('Used cost ', costs[pred_classifier])

        if gt.index(1) == ratios_used.index(max(ratios_used)):
            correct_count += 1
            counter_corrects.append(1)
            corrects_gen_cmi.append(1)
        else:
            corrects_gen_cmi.append(0)
            counter_corrects.append(0)


        if gt.index(1) == ratios_pair[0].index(max(ratios_pair[0])):
            corrects_gen.append(1)
        else:
            corrects_gen.append(0)





    accuracy = float(correct_count) / float(len(dataset))
    #
    print(type_data,'Test acc ', accuracy, len(counter_corrects), len(dataset))
    print(correct_count,sum(counter_corrects))


    print('Average cost ', sum(used_costs)/float(len(used_costs)))
    print('Average cost with overhead ', sum(total_iters_costs)/float(len(used_costs)))
    print('Used intervals ', used_intervals)

    print('Len of total iters costs ', len(total_iters_costs))
    print('Len of total iters accepts ', len(total_iters_accepts), ', sum ', sum(total_iters_accepts))
    print(total_iters_accepts)
    print(total_iters_intervals)


    if args.out_prefix:
        fname =args.out_prefix+ str(len(inters))+ '_th_'+ str(th1) + '-' + str(th2) +'_init_'+str(initial_interval)+'_period_'+ str(periods[0])+'-' + str(periods[1]) +'.csv'
        fname_w=open(fname,'w')
        fname_w.write((',').join([str(co) for co in counter_corrects])+'\n')
        fname_w.write((',').join([str(co) for co in used_costs])+'\n')
        fname_w.write((',').join([str(co) for co in used_intervals])+'\n')
        fname_w.write((',').join(used_classifier_type)+'\n')
        fname_w.close()

        print('Writing results to ', fname)

        fname_overhead =args.out_prefix+'_overhead_'+ str(len(inters))+ '_th_'+ str(th1) + '-' + str(th2) +'_init_'+str(initial_interval)+'_period_'+ str(periods[0])+'-' + str(periods[1]) +'.csv'
        fname_o = open(fname_overhead, 'w')
        fname_o.write((',').join([str(co) for co in total_iters_costs]) + '\n')
        fname_o.write((',').join([str(co) for co in total_iters_intervals]) + '\n')
        fname_o.write((',').join([str(co) for co in total_iters_accepts]) + '\n')
        fname_o.close()
        print('Writing overhead results to ', fname_overhead)






def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('-th1', '--th1', type=str, default=None,help='theta1')
    parser.add_argument('-th2', '--th2', type=str, default=None,help='theta2')
    parser.add_argument('-periods', '--periods', type=str, default=None, help='start and end periods')
    parser.add_argument('-t', '--test_dataset', type=str, default=None, help='Test dataset')
    parser.add_argument('-op', '--out_prefix', type=str, default=None, help='Output file prefix')
    parser.add_argument('-mm', '--min_max', type=str, default=None, help='Min acc max cost')
    parser.add_argument('-pf', '--pf', type=str, default=None, help='Pareto filename')
    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())