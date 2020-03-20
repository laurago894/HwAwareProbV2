import argparse
import sys
from util import functions




def modify_vtree(vtree,vtree_new_name,classes):
    header=[vt for vt in vtree if  'c' in vt]
    vtree_content=[vt for vt in vtree if 'c' not in vt and 'vtree' not in vt]
    vtl=[vt for vt in vtree if 'vtree' in vt and 'c' not in vt]
    ids_internal_vtree_node=[vt.split(' ')[1] for vt in vtree_content]
    ids_variables=[vt.split(' ')[2] for vt in vtree_content if 'L' in vt]

    max_id_variable = str(max([int(id) for id in ids_variables]))
    # print('Ids of vtree nodes', ids_internal_vtree_node)

    new_leaf_id = int(max_id_variable) + 1
    last_internal_node=int(ids_internal_vtree_node[-1])


    new_leaves=[]
    new_inodes=[]

    for cl in reversed(range(classes)):


        if cl==classes-1:
            right_child=last_internal_node+(2*classes)
        else:
            right_child=idI

        idL=((cl+1)*2)-2
        idI=((cl+1)*2)-1

        new_leaf_line='L '+ str(idL) +' '+ str(new_leaf_id)
        new_inode_line='I '+ str(idI) +' '+ str(idL) +' '+ str(right_child)

        new_leaves.append(new_leaf_line)
        new_inodes.append(new_inode_line)

        new_leaf_id+=1
        # last_internal_node+=2




    ids_internal_vtree_node_new=[int(num)+(2*classes) for num in ids_internal_vtree_node]


    new_vtree=[]
    for ivt,vt in enumerate(vtree_content):
        vts=vt.split(' ')
        vts[1]=str(ids_internal_vtree_node_new[ivt])
        if vts[0]=='I':
            vts[2]=str(int(vts[2])+(2*classes))
            vts[3] = str(int(vts[3]) + (2*classes))
        new_vtree.append((' ').join(vts))


    new_vtree_line = 'vtree ' + str(int(vtl[0].split(' ')[1]) + (2*classes))

    with open(vtree_new_name,'w') as vtnew:
        for vt in header:
            vtnew.write(vt+'\n')
        vtnew.write(new_vtree_line+'\n')
        for vt in new_vtree:
            vtnew.write(vt + '\n')
        for cl in range(classes):
            vtnew.write(new_leaves[cl]+'\n')
            vtnew.write(new_inodes[cl]+'\n')

    vtnew.close()

    print('Writing vtree to ', vtree_new_name)


def run(args):
    #################Vtree learning

    out_location='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/learned_models/vtrees/' + args.dataset + '/'

    for fold in range(int(args.folds)):

        vtree_discr = out_location + args.dataset + '_fold' + str(fold) + '_gen_mi_noclass.vtree'
        vtree_discr_cmi = out_location + args.dataset + '_fold' + str(fold) + '_gen_cmi_noclass.vtree'

        vtree_discr_final = out_location + args.dataset + '_fold' + str(fold) + '_gen_mi.vtree'
        vtree_discr_cmi_final = out_location + args.dataset + '_fold' + str(fold) + '_gen_cmi.vtree'

        #Modify the vtree that was learned without the class variable
        vtree=functions.read_file(vtree_discr)
        modify_vtree(vtree, vtree_discr_final,int(args.class_num))


        vtree2=functions.read_file(vtree_discr_cmi)
        modify_vtree(vtree2, vtree_discr_cmi_final,int(args.class_num))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Re-write PSDD to AC and test WMC without evidence')
    parser.add_argument('dataset', help='Dataset name')
    parser.add_argument('-class_num', '--class_num', type=str, default='1', help='How many class variables are  there')
    parser.add_argument('-f', '--folds', type=str, default=None, help='How many folds')
    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())





