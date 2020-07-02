import argparse, sys
from subprocess import check_call
from util import functions
import math

def info_psdd(invtree):
    # read vtree
    vtree = functions.read_file(invtree)
    nodes=max([int(line.split(' ')[2]) for line in vtree if line.split(' ')[0]=='L'])+1
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
            internal_children[int(sline[1])] = [int(sline[2]), int(sline[3])]  # {vtree node internal:[vtree-node-child1 vtree-node-child2]}
            leaf_parents[int(sline[2])] = int(sline[1])  # {vtree-node:parent}
            leaf_parents[int(sline[3])] = int(sline[1])

    # print('internal children', internal_children)
    # print('leaf parents', leaf_parents)

    return(leaf_nodes,internal_children,leaf_parents)



def prune_psdd(invtree,inpsdd,variables_prune,outpsdd,outvtree):

    psddfile = functions.read_file(inpsdd)
    full_psdd = []
    for line in psddfile:
        full_psdd.append(line)

    largest_id = max([int(id.split(' ')[1]) for id in full_psdd if 'c' not in id and 'psdd' not in id])
    # var_prune=1
    var_prune=[int(v) for v in variables_prune.split(',')]
    # print('variable to prune ',var_prune)
    (leaf_nodes,internal_children,leaf_parents)=info_psdd(invtree)

    # what is the vtree node of the feature to prune

    vtree_nodes=[leaf_nodes[var] for var in var_prune]
    vtree_nodes.sort(reverse=True)
    # print('vtree node',vtree_nodes)

    for var_to_prune,vtree_node in zip(var_prune,vtree_nodes):
        nodes_replacement = {}
        psdd_nodes_T_remove=[]
        psdd_nodes_L_remove = []
        potential_L_lines_remove=[]
        potential_T_lines_remove = []
        positive_L=[]
        negative_L = []
        all_lines_to_remove=[]
        all_lines_to_add = []
        # print('\n\nVT node ', vtree_node)

    #its parent and the other child
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
        modified_tnodes=[]

        L_node_to_true=[]
        replacements={}
        replacements_back = {}
        # print('\n\n')
        for line in full_psdd:

            if line.split(' ')[0] == 'D':
                if int(line.split(' ')[2]) == parent:
                    # print('\nParent line ', line)
                    parent_line=line
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
                    print('From parent ', line)
                    print('children parent decision', children_parent_decision)
                    other_childpsdd = [ch for ch in children_parent_decision if ch in psdd_nodes_T_remove + psdd_nodes_L_remove][0]
                    rep=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove+psdd_nodes_L_remove]
                    to_replace=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove+psdd_nodes_L_remove][0]

                    # print('To replace is ', to_replace)
                    print('Other child is ', other_childpsdd)
                    if other_childpsdd in positive_L and len(line.split(' '))>7:
                        flag_tnode_modify.append([str(to_replace),rep, parent_line])
                        # flag_tnode_modify.append(rep)
                        print('Flagged T node to be modified ', flag_tnode_modify)
                        # This one is only used by those decision nodes that require reparam (flagged t nodes)
                        replacements_back[str(to_replace)] = parent_line
                    # print('OCH ', other_child in positive_L)

                    #when replacing a mult-children decision node with a leaf node, we must modify that leaf node to a true node
                    #with the paraneters from the replaced decision node
                    # print(children_parent_decision)
                    if len(children_parent_decision)>2:
                        # print('From parent ', line, 'momdify new pointer to be true')
                        potential_replace=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove+psdd_nodes_L_remove]
                        # print('Potential replace ', potential_replace)
                        # which of the potential replacements is positive leaf
                        for chline in full_psdd:
                            if chline.split(' ')[0]=='L' and int(chline.split(' ')[1]) in potential_replace:
                                if '-' not in chline.split(' ')[-1]:
                                    tr=chline
                                    replace_flag = 0
                        if replace_flag==0:
                            # print('Will modify l node ', tr)
                            # print(children_parent_decision)
                            #params of the decision node (it would make sense that this decision node only has two children...)
                            if int(tr.split(' ')[1]) in children_parent_decision:  #[0:2]:
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
        # print('Replacements are ')
        # for node in replacements:
        #     print(node,',',replacements[node])

        # print('Replacements back ', replacements_back)
        # for node in replacements_back:
        #     print(node,',',replacements_back[node])

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
        # print(nodes_replacement)

        if flag_tnode_modify:
            tnode_change = None
            tnode_change_parent=None
            dnode_change = None
            for node_mod in flag_tnode_modify:
                print('\n\nModifying node ', node_mod)
                cond_params={}
                for line in full_psdd:
                    if line.split(' ')[0]!='c' and line.split(' ')[0]!='psdd':
                        if line.split(' ')[1] == node_mod[0]:
                            if line.split(' ')[0]=='T':
                                tnode_change=line
                                tnode_change_parent=node_mod[2]
                            if line.split(' ')[0] == 'D':
                                dnode_change = line
                if tnode_change:  # I know this is not smart but I don't have time to modify the rest of the code, change later
                    print('tnode change ', tnode_change)
                    print('Its parent is ', tnode_change_parent)
                    tnodes = [tnode_change]
                    cond_params[tnode_change.split(' ')[1]] = tnode_change.split(' ')[-1]
                    # We first have to find the other tnodes
                    mm = [str(nod) for nod in node_mod[1] if str(nod) not in node_mod[0]]
                    print('mm is', mm)
                    rem_t=1
                    linetoremove=None
                    for other_dec in mm:
                        for line in full_psdd:
                            if line.split(' ')[0] != 'c' and line.split(' ')[0] != 'psdd':
                                if line.split(' ')[0] == 'T' and line.split(' ')[1] == other_dec:
                                    tnodes.append(line)
                                    # should not remove if used elsewhere though
                                    cond_params[line.split(' ')[1]] = line.split(' ')[-1]
                                    linetoremove=line
                                    break
                        print('Linetoremove ', linetoremove)
                        if linetoremove:
                            for row in full_psdd:
                                if row.split(' ')[0] != 'c' and row.split(' ')[0] != 'psdd':
                                    if row.split(' ')[0] == 'D' and linetoremove.split(' ')[1] in row.split(' ')[4:]:
                                        if row!=tnode_change_parent:
                                            print('Cannot remove or modify because it has more than one parent ',row)
                                            rem_t=0
                                            break
                        if rem_t:
                            all_lines_to_remove.append(line)
                            print('Line remove ', line)
                        if not rem_t:
                            #INstead of modifying the Tnode and removing its sibling, we add a new Tnode with new params
                            print('We will instead add a new T node')
                            print('And also modify the grandparent node',tnode_change_parent.split(' ')[1])
                            # all_lines_to_add


                    # print('Cond params is', cond_params)
                    # print('Positive ', positive_L, ', negative ', negative_L)
                    # #
                    # print('Decision node of interest', node_mod[2])
                    # print(int((len(replacements_back[node_mod[0]].split(' '))-4)/3))
                    # print(node_mod[2].split(' ')[3])
                    positive_cond_param = 0.5
                    pos_parent_param = 0.5
                    negative_cond_param = 0.5
                    neg_parent_param = 0.5
                    for ii in range(int(node_mod[2].split(' ')[3])):
                        # dn=replacements_back[node_mod[0]].split(' ')[4+(3*ii):4+(3*ii)+3]
                        dn = node_mod[2].split(' ')[4 + (3 * ii):4 + (3 * ii) + 3]
                        # print('dn',dn,'posL',str(positive_L[0]),str(positive_L[0]) in dn)
                        # print('dn', dn, 'negL', str(negative_L[0]),str(negative_L[0]) in dn)

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
                        if sum([1 for nn in dn if nn in [str(ni) for ni in negative_L]])>0: #this is the positive variable:
                            neg_parent_param=math.exp(float(dn[2]))
                    print('Positive cond param ', positive_cond_param)
                    print('Positive parent param ', pos_parent_param)
                    print('Negative cond param ', negative_cond_param)
                    print('Negative parent param ', neg_parent_param)
                    print('rem t ', rem_t)
                    new_pos_param=(positive_cond_param*pos_parent_param)+(negative_cond_param*neg_parent_param)
                    newnode=tnode_change.split(' ')
                    newnode[-1]=str(math.log(new_pos_param))
                    print('New node is ', newnode)
                    print(modified_tnodes)

                    if not rem_t or (newnode[1] in modified_tnodes):
                        #find out what is the largest
                        print('We will add modified ', newnode)
                        #Look for largest ID

                        print('Largest ID is ', largest_id)
                        newnode[1]=str(largest_id+1)
                        print('New node to append to psdd is ', ' '.join(newnode))
                        # all_lines_to_add.append(' '.join(newnode))
                        print('Looking for ', tnode_change_parent.split(' ')[1])
                        print(nodes_replacement)

                        id_append_new=len(full_psdd)
                        for nr in nodes_replacement:
                            if tnode_change_parent.split(' ')[1] in nr.split(' ')[4:]:
                                if full_psdd.index(nr)< id_append_new:
                                    id_append_new=full_psdd.index(nr)
                                print(nr, 'Position ', nr.split(' ').index(tnode_change_parent.split(' ')[1]))
                                temp=nodes_replacement[nr]
                                temp=temp.split(' ')
                                temp[nr.split(' ').index(tnode_change_parent.split(' ')[1])]=str(largest_id+1)

                                nodes_replacement[nr]=(' ').join(temp)
                        print('New nodes replacement ', nodes_replacement)
                        largest_id += 1
                        full_psdd.insert(id_append_new,' '.join(newnode))
                    elif rem_t:
                        nodes_replacement[tnode_change]=' '.join(newnode)
                        modified_tnodes.append(newnode[1])
                        print(newnode[1] in modified_tnodes)

                if dnode_change:  # I know this is not smart but I don't have time to modify the rest of the code, change later
                    dnodes=[dnode_change]
                    dnodes_params=[[math.exp(float(dnode_change.split(' ')[6+(3*ii)])) for ii in range(int(dnode_change.split(' ')[3]))]]
                    #We first have to find the other dnodes
                    nm=[str(nod) for nod in node_mod[1] if str(nod) not in dnode_change]
                    print('nm is', nm)
                    for other_dec in nm:
                        for line in full_psdd:
                            if line.split(' ')[0] != 'c' and line.split(' ')[0] != 'psdd':
                                if line.split(' ')[0] == 'D' and line.split(' ')[1] == other_dec:
                                    dnodes.append(line)
                                    all_lines_to_remove.append(line)
                                    dnodes_params.append([math.exp(float(line.split(' ')[6+(3*ii)])) for ii in range(int(line.split(' ')[3]))])
                                    break
                    print('Dnodes to merge are ', dnodes)
                    #
                    print(' Their params ', dnodes_params)
                    #we will modify dnode_change to add the other dnodes as extra children and then we need to reparametrize everything
                    # print('Decision node parent', replacements_back[node_mod[0]])
                    if len(dnodes)>1:
                        parent_decision_nodes=[]
                        for ii in range(int(replacements_back[node_mod[0]].split(' ')[3])):
                            parent_decision_nodes.append(replacements_back[node_mod[0]].split(' ')[4+(3*ii):4+(3*ii)+3])
                        # print(parent_decision_nodes)
                        for dnode,dnode_param in zip(dnodes,dnodes_params):
                            for ch in parent_decision_nodes:
                                if dnode.split(' ')[1] in ch:
                                    print('For node ', dnode, ' parent param is ', math.exp(float(ch[-1])))
                                    dnodes_params[dnodes_params.index(dnode_param)]=[math.log(math.exp(float(ch[-1]))*param) for param in dnode_param]
                                    tempd = dnode.split(' ')
                                    for ii in range(int(dnode.split(' ')[3])):
                                        tempd[6 + (3 * ii)]=str(math.log(math.exp(float(ch[-1]))*dnode_param[ii]))
                                    dnodes[dnodes.index(dnode)]=tempd
                        #Now we merge the dnodes, we use the first's number
                        newline=dnodes[0]
                        print('newline ', newline)
                        print('dnode ', dnodes)
                        print(node_mod)


                        # newline=[newline+dnode[4:] for dnode in dnodes[1:]]
                        for dnode in dnodes[1:]:
                            if isinstance(dnode,str):
                                newline=newline+dnode.split(' ')[4:]
                                nl=newline
                                newline=[nl]
                            else:
                                newline=newline+dnode[4:]
                        # newline[0][3]= str(int((len(newline[0])-4)/3))
                        if newline[0]=='D':
                            newline=newline
                            newline[3] = str(int((len(newline[0]) - 4) / 3))
                            newline = (' ').join(newline)
                        else:
                            newline[0][3] = str(int((len(newline[0]) - 4) / 3))
                            newline=(' ').join(newline[0])
                        nodes_replacement[dnode_change] =newline

                        # print('Replace ', dnode_change, ' with ', newline)


        #
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
            print('Check 1 ',node_remove in full_psdd)
            if node_remove in full_psdd:
                print(node_remove)
                full_psdd.pop(full_psdd.index(node_remove))
            # print('Check 2 ', node_remove in full_psdd)

        # for newnode in all_lines_to_add:
        #     full_psdd.append(newnode)
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

        # internal_children[parent_of_parent][internal_children[parent_of_parent].index(parent)]=other_child
        # leaf_parents[other_child]=parent_of_parent

        # print('\n\nleaf nodes ', leaf_nodes)
        # print('internal children ',internal_children)
        # print('leaf parents ', leaf_parents)

    outpsddfile=open(outpsdd,'w')
    for line in full_psdd:
        # print(line)
        outpsddfile.write(line+'\n')

    print('Written pruned to ',outpsdd)


    ####### We also have to prune the vtree
    vtree=functions.read_file(invtree)

    # grandparent-
    children_grandparent_vtree=internal_children[leaf_parents[leaf_parents[vtree_node]]]
    original_vtree_grandparent='I '+ str(leaf_parents[leaf_parents[vtree_node]]) +' ' + (' ').join([str(ch) for ch in children_grandparent_vtree])
    children_grandparent_vtree[children_grandparent_vtree.index(leaf_parents[vtree_node])]=[node for node in internal_children[leaf_parents[vtree_node]] if node!=vtree_node][0]
    new_vtree_grandparent='I '+ str(leaf_parents[leaf_parents[vtree_node]]) +' ' + (' ').join([str(ch) for ch in children_grandparent_vtree])
    #Modify grandparent
    vtree[vtree.index(original_vtree_grandparent)]=new_vtree_grandparent
    #remove leaf
    vtree.pop(vtree.index('L '+str(vtree_node)+' '+str(var_prune[0])))
    #remove parent
    vtree.pop(vtree.index('I '+ str(leaf_parents[vtree_node]) + ' ' + (' ').join([str(ch) for ch in internal_children[leaf_parents[vtree_node]]])))
    #reduce count by two
    psddline=[(loc,vnode) for loc,vnode in enumerate(vtree) if 'vtree' in vnode and 'c' not in vnode]
    newvtreeline= psddline[0][1].split(' ')[0]+' '+str(int(psddline[0][1].split(' ')[1])-2)

    vtree[psddline[0][0]]=newvtreeline

    # print(vtree)

    print('Writing modified vtree to ', outvtree)
    outvtree_file=open(outvtree,'w')
    for line in vtree:
        outvtree_file.write(line+'\n')
    outvtree_file.close()

def run(args):
    prune_psdd(args.invtree, args.inpsdd,args.prunef,args.outpsdd,args.outvtree)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('-invtree', '--invtree', type=str, default=None, help='Input vtree')
    parser.add_argument('-outvtree', '--outvtree', type=str, default=None, help='Output vtree')
    parser.add_argument('-inpsdd', '--inpsdd', type=str, default=None, help='Input psdd')
    parser.add_argument('-outpsdd', '--outpsdd', type=str, default=None, help='Output psdd')
    parser.add_argument('-prunef', '--prunef', type=str, default=None, help='Features to prune (comma separated string)')


    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())