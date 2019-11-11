# HwAwareProbV2

### 1. Dataset pre-processing

Weka's supervised discretization and a one-hot encoding. Removes features that area always equal to 0. Generates 5 folds, each with 70% train, 10% validation and 20% test.

Example:
```
python BinarizeDataset.py path/dataset_name -o out_dataset_name
```
To process all the datasets:

```
python batch_binarize_script.py
```

### 2. 

