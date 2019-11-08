import subprocess

dataset_location='/users/micas/lgalinde/Documents/code_2019/datasets_classification/'

benchmarks=['australian','breast','chess','cleve','corral','credit','diabetes','flare','german','heart','mofn','pima']

for benchmark in benchmarks:

    print('\n\nProcessing ', benchmark)

    in_dataset=dataset_location+benchmark+'/'+benchmark+'.arff'

    process=subprocess.Popen(['python', 'BinarizeDataset.py', in_dataset, '-o', benchmark])

    stdout, stderr = process.communicate()
