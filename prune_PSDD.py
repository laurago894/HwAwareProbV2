import argparse, sys
from subprocess import check_call
from util import functions
import math

def info_psdd(invtree):
    # read vtree
    vtree = functions.read_file(invtree)
    for line in vtree:
        if line.split(' ')[0] == 'vtree':
            nodes = int(((int(line.split(' ')[1]) + 1) / 2) + 1)

    # node cprresponding to the leaf
    leaf_nodes = [None] * nodes  # index is number of variable and content is vtree-node
    for line in vtree:
        sline = line.split(' ')
        if sline[0] == 'L':
            leaf_nodes[int(sline[-1])] = int(sline[-2])
    #
    # print('leaf nodes ', leaf_nodes)

    # dict of internal nodes' children
    internal_children = {}
    # dictionary with parent node of each leave
    leaf_parents = {}

    for line in vtree:
        sline = line.split(' ')
        if sline[0] == "I":
            internal_children[int(sline[1])] = [int(sline[2]), int(
                sline[3])]  # {vtree node internal:[vtree-node-child1 vtree-node-child2]}
            leaf_parents[int(sline[2])] = int(sline[1])  # {vtree-node:parent}
            leaf_parents[int(sline[3])] = int(sline[1])

    # print('internal children', internal_children)
    # print('leaf parents', leaf_parents)

    return(leaf_nodes,internal_children,leaf_parents)



def prune_psdd(invtree,inpsdd,variables_prune,outpsdd):

    psddfile = functions.read_file(inpsdd)
    full_psdd = []
    for line in psddfile:
        full_psdd.append(line)

    # var_prune=1
    var_prune=[int(v) for v in variables_prune.split(',')]
    print('variable to prune ',var_prune)
    (leaf_nodes,internal_children,leaf_parents)=info_psdd(invtree)

    # what is the vtree node of the feature to prune

    vtree_nodes=[leaf_nodes[var] for var in var_prune]
    vtree_nodes.sort(reverse=True)
    print('vtree node',vtree_nodes)

    for var_to_prune,vtree_node in zip(var_prune,vtree_nodes):
        nodes_replacement = {}
        psdd_nodes_T_remove=[]
        psdd_nodes_L_remove = []
        potential_L_lines_remove=[]
        potential_T_lines_remove = []
        positive_L=[]
        negative_L = []
        all_lines_to_remove=[]
        # print('\n\nVT node ', vtree_node)

    #it's parent and the other child
        parent=leaf_parents[vtree_node]

        parent_of_parent=leaf_parents[parent]

        # print('vtree node ', vtree_node)
        # print('Parent is  ', parent)
        # print('Children of the parents ', internal_children[parent])
        # #
        # print('The parent of the parent is ', parent_of_parent, ' and its children are', internal_children[parent_of_parent], ' remove ', parent),


        other_child=[ch for ch  in internal_children[parent] if ch!=vtree_node][0]
        # print('and replace with other child', other_child)
        # print('Also remove T node ', vtree_node)
        #
        #######
        parent_locs={}


        #the true nodes to remove


        # print('\n\n')
        for line in full_psdd:
            # print(line)
            if line.split(' ')[0]=='T':
                # print(int(line.split(' ')[2]),vtree_node)
                if int(line.split(' ')[2]) == vtree_node:
                    # print('TO remove line ',line)
                    psdd_nodes_T_remove.append(int(line.split(' ')[1]))
                    potential_T_lines_remove.append(line)
                    all_lines_to_remove.append(line)
            if line.split(' ')[0] == 'L':
                # print(int(line.split(' ')[2]),vtree_node)
                if int(line.split(' ')[2]) == vtree_node:
                    # print('TO remove line ',line)
                    psdd_nodes_L_remove.append(int(line.split(' ')[1]))
                    potential_L_lines_remove.append(line)
                    all_lines_to_remove.append(line) #we remove the line that has the negative number and will modify the params of the positive one


        #true of leaf nodes from the vtree node of interest
        # print('PSDD T nodes to remove ', psdd_nodes_T_remove,'\n')
        # print('PSDD L nodes to remove ', psdd_nodes_L_remove, '\n')

        # save then in aux variable because we need to know whose sibling we keep and we need to modify that sibling's params
        #but this only makes sense if the parents of positiveL and negative L were not deterministic
        # print('Potential L lines remove ', potential_L_lines_remove)
        # print(parent)
        # positive_L=positive_L+ [int(pl.split(' ')[1]) for pl in potential_L_lines_remove if pl.split(' ')[-1]=='1']
        # negative_L = negative_L + [pl.split(' ')[1] for pl in potential_L_lines_remove if pl.split(' ')[-1] == '-1']
        # print('positive L (keep the true node that is sibling to this node but modify params)', positive_L,'\n')



        flag_tnode_modify=[]
        L_node_to_true=[]
        replacements={}
        replacements_back = {}
        # print('\n\n')
        for line in full_psdd:

            if line.split(' ')[0] == 'D':
                if int(line.split(' ')[2]) == parent:
                    # print('\nParent line ', line)
                    replace_flag = 1
                    #Check if we will have to modify the surviving sibling (when decision node parent is not deterministic we have to reparametrize)
                    if len(line.split(' '))>7:
                        # print('Potential L lines remove ', potential_L_lines_remove)
                        positive_L = positive_L + [int(pl.split(' ')[1]) for pl in potential_L_lines_remove if
                                                   pl.split(' ')[-1] == str(var_to_prune)]
                        negative_L = negative_L + [pl.split(' ')[1] for pl in potential_L_lines_remove if
                                                   pl.split(' ')[-1] == '-'+str(var_to_prune)]
                        # print('Positive L is ', positive_L)
                    all_lines_to_remove.append(line)
                    # for ii in range(int((len(lines) - 4) / 3)):
                    #     children_grandparent_decision=children_grandparent_decision+lines[4 + (3 * ii): 4 + (3 * ii) + 3]

                    if len(line.split(' '))>7:
                        children_parent_decision = [int(ch) for ch in line.split(' ')[4:6]+line.split(' ')[7:9]]
                    else:
                        children_parent_decision =[int(ch) for ch in line.split(' ')[4:6]]
                    # print('From parent ', line)
                    # print('children parent decision', children_parent_decision)
                    other_childpsdd = [ch for ch in children_parent_decision if ch in psdd_nodes_T_remove + psdd_nodes_L_remove][0]
                    rep=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove+psdd_nodes_L_remove]
                    to_replace=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove+psdd_nodes_L_remove][0]

                    # print('To replace is ', to_replace)
                    # print('Other child is ', other_childpsdd)
                    if other_childpsdd in positive_L and len(line.split(' '))>7:
                        flag_tnode_modify.append([str(to_replace),rep])
                        # flag_tnode_modify.append(rep)
                        print('Flagged T node to be modified ', flag_tnode_modify)
                        # This one is only used by those decision nodes that require reparam (flagged t nodes)
                        replacements_back[str(to_replace)] = line
                    # print('OCH ', other_child in positive_L)

                    #when replacing a mult-children decision node with a leaf node, we must modify that leaf node to a true node
                    #with the paraneters from the replaced decision node
                    if len(children_parent_decision)>2:
                        # print('From parent ', line, 'momdify new pointer to be true')
                        potential_replace=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove+psdd_nodes_L_remove]
                        # print('Potential replace ', potential_replace)
                        #which of the potential replacements is positive leaf
                        for chline in full_psdd:
                            if chline.split(' ')[0]=='L' and int(chline.split(' ')[1]) in potential_replace:
                                if '-' not in chline.split(' ')[-1]:
                                    tr=chline
                                    replace_flag = 0
                        if replace_flag==0:
                            # print('Will modify l node ', tr)
                            #params of the decision node (it would make sense that this decision node only has two children...)
                            if int(tr.split(' ')[1]) in children_parent_decision[0:2]:
                                new_param=line.split(' ')[6]
                            # elif int(tr.split(' ')[1]) in children_parent_decision[2:]:
                            #     # print(line.split(' ')[9])

                            mod_lnode=tr.split(' ')
                            mod_lnode[0]='T'
                            mod_lnode[1]=line.split(' ')[1]
                            mod_lnode.append(new_param)
                            nodes_replacement[line]=' '.join(mod_lnode)
                            # print('Will now replace ',line, ' with  ', mod_lnode)
                    if replace_flag:
                        replacements[line.split(' ')[1]]=str(to_replace)

        #                 print('We will replace ',line.split(' ')[1], 'with ', str(to_replace))
        print('Replacements are ')
        for node in replacements:
            print(node,',',replacements[node])

        print('Replacements back ', replacements_back)
        for node in replacements_back:
            print(node,',',replacements_back[node])

        # print('pisitive L', positive_L)
        #
        # print('flag tnode modify',flag_tnode_modify)
        # print('L node to modify ', L_node_to_true)




        # print('\n\n')
        for line in full_psdd:
            if line.split(' ')[0]=='D':
                if int(line.split(' ')[2])==parent_of_parent:
                    lines=line.split(' ')
                    # print(line)

                    #1 child or two children
                    #children psdd nodes:
                    children_grandparent_decision=[]
                    # print('Range is ', range(int((len(lines) - 4) / 3)))
                    for ii in range(int((len(lines) - 4) / 3)):
                        # print(lines[4 + (3 * ii): 4 + (3 * ii) + 2])
                        children_grandparent_decision=children_grandparent_decision+lines[4 + (3 * ii): 4 + (3 * ii) + 2]

                    for ich,ch in enumerate(children_grandparent_decision):
                        if ch in replacements:
                            #check if replacement was for t or L node, if it was for t we will need to modify the sibling t node
                            children_grandparent_decision[ich]=replacements[children_grandparent_decision[ich]]

                    # print('children gp decision', children_grandparent_decision)

                    for ii in range(int((len(lines) - 4) / 3)):
                        lines[4 + (3 * ii): 4 + (3 * ii) + 2]=children_grandparent_decision[(2*ii):(2*ii)+2]
                    st=' '.join(lines)
                    nodes_replacement[line]=st

        #modify the flagged true nodes -- this will be needed if after pruning the remaining child is a true node with conditional probability
        # flag_tnode_modify
        print(nodes_replacement)

        if flag_tnode_modify:
            tnode_change = None
            dnode_change = None
            for node_mod in flag_tnode_modify:
                print('\n\nModifying node ', node_mod)
                cond_params={}
                for line in full_psdd:
                    if line.split(' ')[0]!='c' and line.split(' ')[0]!='psdd':
                        if line.split(' ')[1] == node_mod[0]:
                            if line.split(' ')[0]=='T':
                                tnode_change=line
                            if line.split(' ')[0] == 'D':
                                dnode_change = line
                if tnode_change:  # I know this is not smart but I don't have time to modify the rest of the code, change later
                    tnodes = [tnode_change]
                    cond_params[tnode_change.split(' ')[1]] = tnode_change.split(' ')[-1]
                    # We first have to find the other tnodes
                    mm = [str(nod) for nod in node_mod[1] if str(nod) not in tnode_change]
                    print('mm is', mm)

                    for other_dec in mm:
                        for line in full_psdd:
                            if line.split(' ')[0] != 'c' and line.split(' ')[0] != 'psdd':
                                if line.split(' ')[0] == 'T' and line.split(' ')[1] == other_dec:
                                    tnodes.append(line)
                                    all_lines_to_remove.append(line)
                                    cond_params[line.split(' ')[1]] = line.split(' ')[-1]
                                    break
                    print('Cond params is', cond_params)
                    print('Positive ', positive_L, ', negative ', negative_L)
                    #
                    print('Decision node of interest', replacements_back[node_mod[0]])
                    print(int((len(replacements_back[node_mod[0]].split(' '))-4)/3))
                    for ii in range(int((len(replacements_back[node_mod[0]].split(' '))-4)/3)):
                        dn=replacements_back[node_mod[0]].split(' ')[4+(3*ii):4+(3*ii)+3]
                        print('dn,positive L',dn,positive_L)
                        if str(positive_L[0]) in dn:
                            for node in dn[0:2]:
                                if node in cond_params:
                                    positive_cond_param=math.exp(float(cond_params[node]))
                        if str(negative_L[0]) in dn:
                            for node in dn[0:2]:
                                if node in cond_params:
                                    negative_cond_param = math.exp(float(cond_params[node]))
                        if sum([1 for nn in dn if nn in [str(ni) for ni in positive_L]])>0: #this is the positive variable:
                            pos_parent_param=math.exp(float(dn[2]))
                            # print(pos_parent_param)
                        if sum([1 for nn in dn if nn in [str(ni) for ni in negative_L]])>0: #this is the positive variable:
                            neg_parent_param=math.exp(float(dn[2]))
                            # print(neg_parent_param)
                    new_pos_param=(positive_cond_param*pos_parent_param)+(negative_cond_param*neg_parent_param)
                    newnode=tnode_change.split(' ')
                    newnode[-1]=str(math.log(new_pos_param))
                    nodes_replacement[tnode_change]=' '.join(newnode)

                if dnode_change:  # I know this is not smart but I don't have time to modify the rest of the code, change later
                    dnodes=[dnode_change]
                    dnodes_params=[[math.exp(float(dnode_change.split(' ')[6+(3*ii)])) for ii in range(int(dnode_change.split(' ')[3]))]]
                    #We first have to find the other dnodes
                    nm=[str(nod) for nod in node_mod[1] if str(nod) not in dnode_change]
                    # print('nm is', nm)
                    for other_dec in nm:
                        for line in full_psdd:
                            if line.split(' ')[0] != 'c' and line.split(' ')[0] != 'psdd':
                                if line.split(' ')[0] == 'D' and line.split(' ')[1] == other_dec:
                                    dnodes.append(line)
                                    all_lines_to_remove.append(line)
                                    dnodes_params.append([math.exp(float(line.split(' ')[6+(3*ii)])) for ii in range(int(line.split(' ')[3]))])
                                    break
                    # print('Dnodes to merge are ', dnodes)
                    #
                    # print(' Their params ', dnodes_params)
                    #we will modify dnode_change to add the other dnodes as extra children and then we need to reparametrize everything
                    # print('Decision node parent', replacements_back[node_mod[0]])
                    parent_decision_nodes=[]
                    for ii in range(int(replacements_back[node_mod[0]].split(' ')[3])):
                        parent_decision_nodes.append(replacements_back[node_mod[0]].split(' ')[4+(3*ii):4+(3*ii)+3])
                    # print(parent_decision_nodes)

                    for dnode,dnode_param in zip(dnodes,dnodes_params):
                        for ch in parent_decision_nodes:
                            if dnode.split(' ')[1] in ch:
                                # print('For node ', dnode, ' parent param is ', math.exp(float(ch[-1])))
                                # print(dnode_param)
                                dnodes_params[dnodes_params.index(dnode_param)]=[math.log(math.exp(float(ch[-1]))*param) for param in dnode_param]
                                tempd = dnode.split(' ')
                                for ii in range(int(dnode.split(' ')[3])):
                                    tempd[6 + (3 * ii)]=str(math.log(math.exp(float(ch[-1]))*dnode_param[ii]))
                                dnodes[dnodes.index(dnode)]=tempd
                    #Now we merge the dnodes, we use the first's number
                    newline=dnodes[0]
                    newline=[newline+dnode[4:] for dnode in dnodes[1:]]
                    newline[0][3]= str(int((len(newline[0])-4)/3))
                    newline=(' ').join(newline[0])
                    nodes_replacement[dnode_change] =newline
                    # print('Replace ', dnode_change, ' with ', newline)



        print('\n')
        print('Nodes to modify ')
        for node in nodes_replacement:
            print(node,)
            print(' to')
            print(nodes_replacement[node],'\n')



        for node_change in nodes_replacement:
            idx=full_psdd.index(node_change)
            # print(full_psdd.index(node_change))
            # print(full_psdd[full_psdd.index(node_change)])
            full_psdd[full_psdd.index(node_change)]=nodes_replacement[node_change]
            # print(full_psdd[idx])

        print('\nNodes to remove')

        for node_remove in all_lines_to_remove:
            # print('Check 1 ',node_remove in full_psdd)
            if node_remove in full_psdd:
                print(node_remove)
                full_psdd.pop(full_psdd.index(node_remove))
            # print('Check 2 ', node_remove in full_psdd)

        # print('\n\nleaf nodes ', leaf_nodes)
        # print('internal children ',internal_children)
        # print('leaf parents ', leaf_parents)
        #
        # print('vtree node ', vtree_node)
        # print('Parent is  ', parent)
        # print('Children of the parents ', internal_children[parent])
        # #
        # print('The parent of the parent is ', parent_of_parent, ' and its children are',
        #       internal_children[parent_of_parent], ' remove ', parent),

        # print('and replace with other child', other_child)
        # print('Also remove T node ', vtree_node)

        internal_children[parent_of_parent][internal_children[parent_of_parent].index(parent)]=other_child
        leaf_parents[other_child]=parent_of_parent

        # print('\n\nleaf nodes ', leaf_nodes)
        # print('internal children ',internal_children)
        # print('leaf parents ', leaf_parents)

    outpsddfile=open(outpsdd,'w')
    for line in full_psdd:
        # print(line)
        outpsddfile.write(line+'\n')

    print('Written pruned to ',outpsdd)


def run(args):
    prune_psdd(args.invtree, args.inpsdd,args.prunef,args.outpsdd)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('-invtree', '--invtree', type=str, default=None, help='Input vtree')
    parser.add_argument('-inpsdd', '--inpsdd', type=str, default=None, help='Input psdd')
    parser.add_argument('-outpsdd', '--outpsdd', type=str, default=None, help='Output psdd')
    parser.add_argument('-prunef', '--prunef', type=str, default=None, help='Features to prune (comma separated string)')


    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())