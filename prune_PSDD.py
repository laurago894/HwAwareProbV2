import argparse, sys
from subprocess import check_call
from util import functions

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
    print('leaf nodes ', leaf_nodes)

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

    print('internal children', internal_children)
    print('leaf parents', leaf_parents)

    return(leaf_nodes,internal_children,leaf_parents)



def prune_psdd(invtree,inpsdd,variables_prune,outpsdd):

    psddfile = functions.read_file(inpsdd)
    full_psdd = []
    for line in psddfile:
        full_psdd.append(line)

    # var_prune=1
    var_prune=[int(v) for v in variables_prune.split(',')]
    print(var_prune)
    (leaf_nodes,internal_children,leaf_parents)=info_psdd(invtree)

    # what is the vtree node of the feature to prune

    vtree_nodes=[leaf_nodes[var] for var in var_prune]
    vtree_nodes.sort(reverse=True)
    print(vtree_nodes)

    for vtree_node in vtree_nodes:
        nodes_replacement = {}
        psdd_nodes_T_remove=[]
        all_lines_to_remove=[]
        print('\n\nVT node ', vtree_node)

    #it's parent and the other child
        parent=leaf_parents[vtree_node]

        parent_of_parent=leaf_parents[parent]

        print('vtree node ', vtree_node)
        print('Parent is  ', parent)
        print('Children of the parents ', internal_children[parent])
        #
        print('The parent of the parent is ', parent_of_parent, ' and its children are', internal_children[parent_of_parent], ' remove ', parent),


        other_child=[ch for ch  in internal_children[parent] if ch!=vtree_node][0]
        print('and replace with other child', other_child)
        print('Also remove T node ', vtree_node)
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
                    all_lines_to_remove.append(line)

        # print('PSDD nodes to remove ', psdd_nodes_T_remove)

        replacements={}
        # print('\n\n')
        for line in full_psdd:

            if line.split(' ')[0] == 'D':
                if int(line.split(' ')[2]) == parent:
                    # print('Parent line ', line)
                    all_lines_to_remove.append(line)
                    children_parent_decision =[int(ch) for ch in line.split(' ')[4:6]]
                    # print(children_parent_decision)
                    to_replace=[ch for ch in children_parent_decision if ch not in psdd_nodes_T_remove][0]
                    other_childpsdd = [ch for ch in children_parent_decision if ch in psdd_nodes_T_remove][0]
                    print('To replace is ', to_replace)
                    print('Other child is ', other_childpsdd)
                    replacements[line.split(' ')[1]]=str(to_replace)
        # print(replacements)





        # print('\n\n')
        for line in full_psdd:
            if line.split(' ')[0]=='D':
                if int(line.split(' ')[2])==parent_of_parent:
                    lines=line.split(' ')
                    # print(line)
                    #children psdd nodes:
                    children_grandparent_decision=lines[4:6]
                    # print(children_grandparent_decision)
                    if children_grandparent_decision[0] in replacements:
                        children_grandparent_decision[0]=replacements[children_grandparent_decision[0]]
                    if children_grandparent_decision[1] in replacements:
                        children_grandparent_decision[1] = replacements[children_grandparent_decision[1]]
                    # print(children_grandparent_decision)
                    lines[4:6]=children_grandparent_decision
                    st=' '.join(lines)
                    nodes_replacement[line]=st

        print('\n')
        print('Nodes to modify ', nodes_replacement)
        print('Nodes to remove', all_lines_to_remove)

        for node_change in nodes_replacement:
            idx=full_psdd.index(node_change)
            print(full_psdd.index(node_change))
            print(node_change)
            print(full_psdd[full_psdd.index(node_change)])
            full_psdd[full_psdd.index(node_change)]=nodes_replacement[node_change]
            print(full_psdd[idx])

        for node_remove in all_lines_to_remove:
            # print('Check 1 ',node_remove in full_psdd)
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

    print(type(full_psdd[0]))
    outpsddfile=open(outpsdd,'w')
    for line in full_psdd:
        print(line)
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