class Task:
    """The objective of the experiment."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class Algorithm:
    """The algorithm to train on the dataset."""

    XGBOOST = "xgboost"
    XGBOOST_RANDOM_FOREST = "xgboost_random_forest"
    LIGHTGBM = "lightgbm"
    ADA_BOOST = "ada_boost"
    BAGGING = "bagging"
    EXTRA_TREES = "extra_trees"
    GRADIENT_BOOSTING_TREES = "gradient_boosting_trees"
    RANDOM_FOREST = "random_forest"
    HIST_GRADIENT_BOOSTING = "hist_gradient_boosting"
    SVM = "svm"
    NU_SVM = "nu_svm"
    LINEAR_SVM = "linear_svm"
    LINEAR = "linear"
    RIDGE = "ridge"
    LASSO = "lasso"
    ELASTIC_NET = "elastic_net"
    LEAST_ANGLE = "least_angle"
    LASSO_LEAST_ANGLE = "lasso_least_angle"
    ORTHOGONAL_MATCHING_PURSUIT = "orthogonal_matching_pursuit"
    BAYSIAN_RIDGE = "baysian_ridge"
    AUTOMATIC_RELEVANCE_DETERMINATION = "automatic_relevance_determination"
    STOCHASTIC_GRADIENT_DESCENT = "stochastic_gradient_descent"
    PERCEPTRON = "perceptron"
    PASSIVE_AGGRESSIVE = "passive_aggressive"
    RANSAC = "ransac"
    THEIL_SEN = "theil_sen"
    HUBER = "huber"
    QUANTILE = "quantile"
    KERNEL_RIDGE = "kernel_ridge"
    GAUSSIAN_PROCESS = "gaussian_process"


class Search:
    """If set, PostgresML will perform a hyperparameter search to find the best hyperparameters for the algorithm."""

    GRID = "grid"
    RANDOM = "random"


class Sampling:
    """Search parameters used in the hyperparameter search, using the scikit-learn notation, JSON formatted."""

    RANDOM = "random"
    FIRST = "first"
    LAST = "last"


class CategoricalEncodings:
    """Encoding categorical variables is an O(N log(M)) where N is the number of rows, and M is the number of distinct categories."""

    NONE = "none"
    TARGET = "target"
    ONE_HOT = "one_hot"
    ORDINAL = "ordinal"


class Imputing:
    """NULL and NaN values can be replaced by several statistical measures observed in the training data."""

    ERROR = "error"
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    MIN = "min"
    MAX = "max"
    ZERO = "zero"


class Scaling:
    PRESERVE = "preserve"
    STANDARD = "standard"
    MIN_MAX = "min_max"
    MAX_ABS = "max_abs"
    ROBUST = "robust"


class Strategy:
    MOST_RECENT = "most_recent"
    BEST_SCORE = "best_score"
    ROLLBACK = "rollback"
