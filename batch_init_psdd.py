import subprocess


# benchmarks=['australian','breast','chess','cleve','corral','credit','diabetes','flare','german','heart','mofn','pima']
benchmarks=['breast','chess','cleve','corral','credit','diabetes','flare','german','heart','mofn','pima']

for benchmark in benchmarks:

    print('\n\nLearning vtrees from ', benchmark)

    process1=subprocess.Popen(['python', 'VtreeClassCond.py', benchmark])

    stdout1, stderr1 = process1.communicate()

    process=subprocess.Popen(['python', 'InitNBPSDD.py', benchmark])

    stdout, stderr = process.communicate()
