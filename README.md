# HwAwareProbV2

## Dependencies and parameters



### 1. Dataset pre-processing

Weka's supervised discretization and a one-hot encoding. Removes features that area always equal to 0. Generates 5 folds, each with 70% train, 10% validation and 20% test.

```
python BinarizeDataset.py path/dataset_name -o out_dataset_name
```
To process all the datasets:

```
python batch_binarize_script.py
```

### 2. Vtree learning

Uses the vtree learning algorithm from learnPSDD <sup>[1](#myfootnote1)</sup>. We have added a Conditional Mutual Information vtree learning function. The following script learns three different vtree types (for now limited to bottom-up learning):

* genMI: Mutual Information based vtree learning (original algorithm)
* discMI: Mutual Information based vtree learning (original algorithm) on all "feature" variables.
* discCMI: Conditional Mutual Information based vtree learning on all "feature" variables.


```
python LearnVtrees.py out_dataset_name
```

To process all datasets:

```
python batch_vtree_script.py
```

### 3. Setting up the initial PSDD

Uses the vtree learning algorithm from learnPSDD <sup>[1](#myfootnote1)</sup> to incrementally learn a model. First, force the class variable to be the prime of the vtree's PSDD:

```
python VtreeClassCond.py out_dataset_name
```

For discMI and discCMI, generate an initial PSDD, where feature variables are conditioned on the class variable (i.e. a naive Bayes like structure):

```
python InitNBPSDD.py out_dataset_name
```

Both steps for all datasets:

```
python batch_init_psdd.py
```

### 4. Accuracy and node count


Accuracy per fold and learning type:

```
python AccuracyCost.py out_dataset_name
```
For all datasets:

```
python batch_accuracy_script.py
```

### 5. Comparison with Bayesian Network classifiers

TO DO

<a name="myfootnote1">1</a>: Liang, Yitao, Jessa Bekker, and Guy Van den Broeck. "Learning the structure of probabilistic sentential decision diagrams." Proceedings of the 33rd Conference on Uncertainty in Artificial Intelligence (UAI). 2017.
