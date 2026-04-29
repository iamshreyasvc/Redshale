"""Pipeline node kind identifiers (stable JSON / executor contract)."""

DATASET = "dataset"
PREPROCESS = "preprocess"
TRAIN = "train"
TRAIN_PYTORCH = "train_pytorch"
TRAIN_TENSORFLOW = "train_tensorflow"
EVALUATE = "evaluate"
VALIDATE = "validate"
EXPORT = "export"
PRINT_RESULTS = "print_results"

ALL_KINDS = (
    DATASET,
    PREPROCESS,
    TRAIN,
    TRAIN_PYTORCH,
    TRAIN_TENSORFLOW,
    EVALUATE,
    VALIDATE,
    EXPORT,
    PRINT_RESULTS,
)
