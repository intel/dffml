import os
import sys
import ast
import site
from io import open
from pathlib import Path
from setuptools import find_packages, setup

# See https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

ORG = "intel"
NAME = "dffml-model-scikit"
DESCRIPTION = "DFFML model scikit"
AUTHOR_NAME = "Yash Lamba"
AUTHOR_EMAIL = "yashlamba2000@gmail.com"

IMPORT_NAME = (
    NAME
    if "replace_package_name".upper() != NAME
    else "replace_import_package_name".upper()
).replace("-", "_")

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(SELF_PATH, IMPORT_NAME, "version.py"), "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(SELF_PATH, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="dffml-model-scikit",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Yash Lamba",
    author_email="yashlamba2000@gmail.com",
    maintainer="John Andersen",
    maintainer_email="john.s.andersen@intel.com",
    url="https://github.com/intel/dffml/blob/master/model/scikit/README.md",
    license="MIT",
    keywords=["dffml"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points={
        "dffml.model": [
            f"scikitknn = {IMPORT_NAME}.scikit_models:KNeighborsClassifierModel",
            f"scikitadaboost = {IMPORT_NAME}.scikit_models:AdaBoostClassifierModel",
            f"scikitgpc = {IMPORT_NAME}.scikit_models:GaussianProcessClassifierModel",
            f"scikitdtc = {IMPORT_NAME}.scikit_models:DecisionTreeClassifierModel",
            f"scikitrfc = {IMPORT_NAME}.scikit_models:RandomForestClassifierModel",
            f"scikitmlp = {IMPORT_NAME}.scikit_models:MLPClassifierModel",
            f"scikitgnb = {IMPORT_NAME}.scikit_models:GaussianNBModel",
            f"scikitqda = {IMPORT_NAME}.scikit_models:QuadraticDiscriminantAnalysisModel",
            f"scikitsvc = {IMPORT_NAME}.scikit_models:SVCModel",
            f"scikitlr = {IMPORT_NAME}.scikit_models:LinearRegressionModel",
            f"scikitlor = {IMPORT_NAME}.scikit_models:LogisticRegressionModel",
            f"scikitgbc = {IMPORT_NAME}.scikit_models:GradientBoostingClassifierModel",
            f"scikitetc = {IMPORT_NAME}.scikit_models:ExtraTreesClassifierModel",
            f"scikitbgc = {IMPORT_NAME}.scikit_models:BaggingClassifierModel",
            f"scikiteln = {IMPORT_NAME}.scikit_models:ElasticNetModel",
            f"scikitbyr = {IMPORT_NAME}.scikit_models:BayesianRidgeModel",
            f"scikitlas = {IMPORT_NAME}.scikit_models:LassoModel",
            f"scikitard = {IMPORT_NAME}.scikit_models:ARDRegressionModel",
            f"scikitrsc = {IMPORT_NAME}.scikit_models:RANSACRegressorModel",
            f"scikitbnb = {IMPORT_NAME}.scikit_models:BernoulliNBModel",
            f"scikitmnb = {IMPORT_NAME}.scikit_models:MultinomialNBModel",
            f"scikitlda = {IMPORT_NAME}.scikit_models:LinearDiscriminantAnalysisModel",
            f"scikitdtr = {IMPORT_NAME}.scikit_models:DecisionTreeRegressorModel",
            f"scikitgpr = {IMPORT_NAME}.scikit_models:GaussianProcessRegressorModel",
            f"scikitomp = {IMPORT_NAME}.scikit_models:OrthogonalMatchingPursuitModel",
            f"scikitlars = {IMPORT_NAME}.scikit_models:LarsModel",
            f"scikitridge = {IMPORT_NAME}.scikit_models:RidgeModel",
            f"scikitkmeans = {IMPORT_NAME}.scikit_models:KMeansModel",
            f"scikitbirch = {IMPORT_NAME}.scikit_models:BirchModel",
            f"scikitmbkmeans = {IMPORT_NAME}.scikit_models:MiniBatchKMeansModel",
            f"scikitap = {IMPORT_NAME}.scikit_models:AffinityPropagationModel",
            f"scikitms = {IMPORT_NAME}.scikit_models:MeanShiftModel",
            f"scikitsc = {IMPORT_NAME}.scikit_models:SpectralClusteringModel",
            f"scikitac = {IMPORT_NAME}.scikit_models:AgglomerativeClusteringModel",
            f"scikitoptics = {IMPORT_NAME}.scikit_models:OPTICSModel",
        ],
        "dffml.accuracy": [
            "skmodelscore = dffml_model_scikit.scikit_model_scorer:SklearnModelAccuracy",
            f"acscore = {IMPORT_NAME}.scikit_scorers:AccuracyScoreScorer",
            f"bacscore = {IMPORT_NAME}.scikit_scorers:BalancedAccuracyScoreScorer",
            f"topkscore = {IMPORT_NAME}.scikit_scorers:TopKAccuracyScoreScorer",
            f"avgprescore = {IMPORT_NAME}.scikit_scorers:AveragePrecisionScoreScorer",
            f"brierscore = {IMPORT_NAME}.scikit_scorers:BrierScoreLossScorer",
            f"f1score = {IMPORT_NAME}.scikit_scorers:F1ScoreScorer",
            f"logloss = {IMPORT_NAME}.scikit_scorers:LogLossScorer",
            f"prescore = {IMPORT_NAME}.scikit_scorers:PrecisionScoreScorer",
            f"recallscore = {IMPORT_NAME}.scikit_scorers:RecallScoreScorer",
            f"jacscore = {IMPORT_NAME}.scikit_scorers:JaccardScoreScorer",
            f"rocaucscore = {IMPORT_NAME}.scikit_scorers:RocAucScoreScorer",
            f"adjmutinfoscore = {IMPORT_NAME}.scikit_scorers:AdjustedMutualInfoScoreScorer",
            f"adjrandscore = {IMPORT_NAME}.scikit_scorers:AdjustedRandScoreScorer",
            f"complscore = {IMPORT_NAME}.scikit_scorers:CompletenessScoreScorer",
            f"fowlmalscore = {IMPORT_NAME}.scikit_scorers:FowlkesMallowsScoreScorer",
            f"homoscore = {IMPORT_NAME}.scikit_scorers:HomogeneityScoreScorer",
            f"mutinfoscore = {IMPORT_NAME}.scikit_scorers:MutualInfoScoreScorer",
            f"normmutinfoscore = {IMPORT_NAME}.scikit_scorers:NormalizedMutualInfoScoreScorer",
            f"randscore = {IMPORT_NAME}.scikit_scorers:RandScoreScorer",
            f"vmscore = {IMPORT_NAME}.scikit_scorers:VMeasureScoreScorer",
            f"exvscore = {IMPORT_NAME}.scikit_scorers:ExplainedVarianceScoreScorer",
            f"maxerr = {IMPORT_NAME}.scikit_scorers:MaxErrorScorer",
            f"meanabserr = {IMPORT_NAME}.scikit_scorers:MeanAbsoluteErrorScorer",
            f"meansqrerr = {IMPORT_NAME}.scikit_scorers:MeanSquaredErrorScorer",
            f"meansqrlogerr = {IMPORT_NAME}.scikit_scorers:MeanSquaredLogErrorScorer",
            f"medabserr = {IMPORT_NAME}.scikit_scorers:MedianAbsoluteErrorScorer",
            f"r2score = {IMPORT_NAME}.scikit_scorers:R2ScoreScorer",
            f"meanpoidev = {IMPORT_NAME}.scikit_scorers:MeanPoissonDevianceScorer",
            f"meangammadev = {IMPORT_NAME}.scikit_scorers:MeanGammaDevianceScorer",
            f"meanabspererr = {IMPORT_NAME}.scikit_scorers:MeanAbsolutePercentageErrorScorer",
        ],
    },
)
