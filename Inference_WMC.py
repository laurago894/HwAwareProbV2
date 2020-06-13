from PSDD_functions import PSDD_to_AC_pruned, PSDD_to_AC
from inference_functions import ac_inference

observation=[0,0,1,0,0,0,1]

observations=[observation[2:],observation]
# observations=[observation,observation]

obds=[[3,4,5,6,7],[3,4,5,6,7]]
inputs=['/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/corral/corral_fold0_gen_cmi/models/0-0-prune1-2.psdd','/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/psdds/corral/corral_fold0_gen_cmi/models/0-0.psdd']

ii=0
for input_psdd,obd,obs in zip(inputs,obds,observations):


    print('\n')

    model = PSDD_to_AC_pruned.convert_psdd(input_psdd)

    content_ac = model[0]
    lmap_id = model[1]
    lmap_w = model[2]
    indicator_dict = model[5]
    variable_list = model[6]

    print(indicator_dict)
    print(variable_list)

    obs_var_den=obd

    # Initialize weight vector
    init_weight = ac_inference.init_weight(content_ac, lmap_id, lmap_w)

    observation=obs

    position_neg_den = [indicator_dict[variable_list[var] + '_' + str(value)] for value, var in
                                    zip(observation, variable_list) if var in obs_var_den ]

    psn_den = [pos for position in position_neg_den for pos in position]

    init_weight_den = [w for w in init_weight]

    for psden in psn_den:
        init_weight_den[psden] = 0


    operations_index, operation = ac_inference.extract_operations(content_ac)

    wmc_den, w_den = ac_inference.performWMC(operations_index, operation, init_weight_den, content_ac)

    print(w_den)
    ii+=1


