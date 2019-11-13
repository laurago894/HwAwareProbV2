import subprocess

#Full pipeline fOr binary class datasets

dataset_location='/users/micas/lgalinde/Documents/code_2019/datasets_classification/'

benchmarks=['chess','cleve','corral','credit','diabetes','flare','german','heart','mofn','pima']

for benchmark in benchmarks:

    print('\n\nProcessing ', benchmark)

    in_dataset=dataset_location+benchmark+'/'+benchmark+'.arff'

    process1=subprocess.Popen(['python', 'BinarizeDataset.py', in_dataset, '-o', benchmark])

    stdout1, stderr1 = process1.communicate()

    print('\n\nLearning vtrees from ', benchmark)

    process2=subprocess.Popen(['python', 'LearnVtrees.py', benchmark])

    stdout2, stderr2 = process2.communicate()

    print('\n\nLearning vtrees from ', benchmark)

    process3=subprocess.Popen(['python', 'VtreeClassCond.py', benchmark])

    stdout3, stderr3 = process3.communicate()

    process4=subprocess.Popen(['python', 'InitNBPSDD.py', benchmark])

    stdout4, stderr4 = process4.communicate()

    process5=subprocess.Popen(['python', 'LearnPSDDfromVtree.py', benchmark])

    stdout5, stderr5 = process5.communicate()

    print('\n\nAccuracy  ', benchmark)

    process6=subprocess.Popen(['python', 'AccuracyCost.py', benchmark])

    stdout6, stderr6 = process6.communicate()

