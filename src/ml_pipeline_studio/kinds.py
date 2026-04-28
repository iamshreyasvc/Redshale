"""Pipeline node kind identifiers (stable JSON / executor contract)."""

DATASET = "dataset"
PREPROCESS = "preprocess"
TRAIN_PYTORCH = "train_pytorch"
TRAIN_TENSORFLOW = "train_tensorflow"
EVALUATE = "evaluate"
VALIDATE = "validate"
EXPORT = "export"

ALL_KINDS = (
    DATASET,
    PREPROCESS,
    TRAIN_PYTORCH,
    TRAIN_TENSORFLOW,
    EVALUATE,
    VALIDATE,
    EXPORT,
)
