import subprocess


# benchmarks=['australian','breast','chess','cleve','corral','credit','diabetes','flare','german','heart','mofn','pima']
benchmarks=['breast','chess','cleve','corral','credit','diabetes','flare','german','heart','mofn','pima']

for benchmark in benchmarks:

    print('\n\nLearning vtrees from ', benchmark)

    process=subprocess.Popen(['python', 'LearnPSDDfromVtree.py', benchmark])

    stdout, stderr = process.communicate()
