
def pareto_acc_cost(model_list): #list of tuples with model specs [(model0,accuracy0,cost0)]

    cost_list=[li[2] for li in model_list]
    accuracy_list=[li[1] for li in model_list]

    #Sorting order of costs
    sort_order = sorted(range(len(cost_list)), key=lambda k: cost_list[k], reverse=True)
    sorted_list=[model_list[num] for num in sort_order]

    ic=0
    pareto_list=[]

    while ic<len(sort_order):
        max_acc=sorted_list[ic][1]
        max_acc_id=ic
        icp=ic
        #Is there a higher accuracy point for the same or less cost?
        for model in sorted_list[ic+1:]:
            icp+=1
            if max_acc<model[1] or max_acc==model[1]:
                max_acc=model[1]
                max_acc_id=icp
        pareto_list.append(sorted_list[max_acc_id])
        ic=max_acc_id+1
    return pareto_list
    # plt.plot([cost_list[num] for num in sort_ordeb

