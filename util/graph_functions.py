import argparse, sys
from subprocess import check_call
from util import functions
#
# ac_to_dot.py

# Based on code by Jonas Vlasselaer,  Joris Renkens and Wannes Meert.
#KU Leuven

def writeToDot_vtree_custom_name(lines, node_labels,out_name):



    with open(out_name, 'w') as f_out:
        f_out.write("digraph test {\n")
        f_out.write("// Edges\n")

        for line in lines:
            f_out.write("{} -> {};\n".format(line[0],line[1]))

        f_out.write("// Labels\n")
        for (key, name) in node_labels.items():

            f_out.write("{} [label=\"{}\"];\n".format(key,node_labels[key]))
            #print colors[key]
        f_out.write("}\n")
    f_out.close()


def readvtree(vtree,var_names):


    node_labels = dict()
    node_counter = 0
    lines = []
    color = dict()
    name =  dict()


    for line in vtree:
        if not line.startswith('c'):
            parts = line.strip().rstrip('\n').split()
            if parts:
                if parts[0] == "L":
                    node_labels[int(parts[1])] = parts[1]+':'+var_names[int(parts[2])] # 'F'+(parts[2])
                    name[node_counter] = int(parts[1])

                elif parts[0] == "I":
                    node_labels[int(parts[1])] = int(parts[1])
                    name[node_counter] = int(parts[1])
                    for i in range(2, len(parts)):
                        lines.append([parts[1], int(parts[i])])

                node_counter += 1
    #
    return lines, node_labels, name






def print_vtree_graph(vtree_name,out_name):


    vtree = functions.read_file(vtree_name)

    #Class variable is last by default
    var_num=[1 for vt in vtree if 'L' in vt]
    # print var_num


    names = ['F' + str(num) for num in range(0, sum(var_num))]
    #names = names + ['CL']

    # print 'names is ', names


    var_names={}
    for nu in range(1,sum(var_num)):
        var_names[nu]=names[nu]


    lines,node_labels,names=readvtree(vtree,var_names)

    # print 'node labels are ', node_labels
    # if args.MI:
    #     fold=1
    #     for ty in ['miBlossom','miMetis']:
    #         main_res_dir = 'PSDD_models/har_folds/'
    #
    #         reader=csv.reader(open('PSDD_models/har_folds/MI_fold1_'+vt_type+'_valid.csv'),delimiter=',')
    #
    #         for row in reader:
    #             node_labels.update({int(float(row[0])):float(row[1])})




    writeToDot_vtree_custom_name(lines, node_labels, out_name)

    check_call(['dot', '-Tpdf', out_name])

def run(args):
    print_vtree_graph(args.inv, args.outv)

def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('inv', help='input vtree file')
    parser.add_argument('outv', help='output pdf')



    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())