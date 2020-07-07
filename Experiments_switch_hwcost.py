import subprocess
import argparse, sys

def run(args):

    # test_dataset='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/har_mv/har_mv_fold0/har_mv_order_20_30.test.data'
    test_dataset=args.td
    # out_prefix='/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/model_switch_hwcost/intervals_'
    out_prefix=args.op

    # th1s=['0.1','0.2','0.3','0.4','0.5']
    th1s = ['0.1','0.2', '0.3', '0.4', '0.5']
    th2s=['0.8','0.85','0.9','0.95','0.99']

    peris=['1,1','2,2','3,3','5,5','8,8','5-10','1-10','10,10','20,20']
    # peris=['10,30']


    for per in peris:

        for th1 in th1s:

            for th2 in th2s:

                process=subprocess.Popen(['python', 'ModelSwitch_hwcost_pr.py', '-th1',th1,'-th2',th2,'-periods',per,'-t',test_dataset,'-op',out_prefix,'-mm',args.mm,'-pf',args.pf])

                stdout, stderr = process.communicate()




def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the hardware-aware model optimization')
    parser.add_argument('-td', '--td', type=str, default=None,help='test dataset')
    parser.add_argument('-mm', '--mm', type=str, default=None, help='min acc max cost')
    parser.add_argument('-op', '--op', type=str, default=None, help='Out prefix')
    parser.add_argument('-pf', '--pf', type=str, default=None, help='Pareto filename')

    args = parser.parse_args(argv)

    run(args)


if __name__ == "__main__":
    sys.exit(main())