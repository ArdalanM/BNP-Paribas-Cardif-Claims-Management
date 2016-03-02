__author__ = 'Ardalan'

CODE_FOLDER = "/home/ardalan/Documents/kaggle/bnp/"
# CODE_FOLDER = "/home/arda/Documents/kaggle/bnp/"

import os, sys, time, re, zipfile, pickle, operator
if os.getcwd() != CODE_FOLDER: os.chdir(CODE_FOLDER)
import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn import cross_validation
from sklearn import linear_model
from sklearn import ensemble
from sklearn import naive_bayes
from sklearn import svm

def reshapePrediction(ypredproba):
    result = None
    if len(ypredproba.shape) > 1:
        if ypredproba.shape[1] == 1: result = ypredproba[:, 0]
        if ypredproba.shape[1] == 2: result = ypredproba[:, 1]
    else:
        result = ypredproba.ravel()
    return result
def eval_func(ytrue, ypredproba):
    return metrics.log_loss(ytrue, reshapePrediction(ypredproba))
def loadFileinZipFile(zip_filename, filename, dtypes=None, parsedate = None, password=None, **kvargs):
    """
    Load file to dataframe.
    """
    with zipfile.ZipFile(zip_filename, 'r') as myzip:
        if password:
            myzip.setpassword(password)

        if parsedate:
            return pd.read_csv(myzip.open(filename), sep=',', parse_dates=parsedate, dtype=dtypes, **kvargs)
        else:
            return pd.read_csv(myzip.open(filename), sep=',', dtype=dtypes, **kvargs)
def printResults(dic_logs):
        l_train_logloss = dic_logs['train_error']
        l_val_logloss = dic_logs['val_error']

        string = ("logTRVAL_{0:.4f}|{1:.4f}".format(np.mean(l_train_logloss), np.mean(l_val_logloss)))
        return string
def KerasClassWeight(Y_vec):
    # Find the weight of each class as present in y.
    # inversely proportional to the number of samples in the class
    recip_freq = 1. / np.bincount(Y_vec)
    weight = recip_freq / np.mean(recip_freq)
    dic_w = {index:weight_value for index, weight_value in enumerate(weight)}
    return dic_w
def saveDicLogs(dic_logs, filename):

    folder2save = CODE_FOLDER + 'diclogs/'
    if os.path.exists(folder2save + filename):
        print('file exist !')
        raise BrokenPipeError
    else:
        # proof_code = open(CODE_FOLDER + 'code/main_CV.py', 'rb').read()
        # open(folder2save + filename + '.py', 'wb').write(proof_code)
        pickle.dump(dic_logs, open(folder2save + filename, 'wb'))
    return


folder = CODE_FOLDER + 'diclogs/'
import glob
l_filenames = glob.glob1(folder, '*.p') ; print(l_filenames)

pd_blend = pd.DataFrame()
for filename in l_filenames:
    dic_log = pickle.load(open(folder + filename,'rb'))
    filename = filename[:-2]

    folds = dic_log['fold']

    for fold in dic_log['fold']:
        pd_blend[filename+'_pred'+str(fold)] = dic_log['ypredproba'][fold]
        pd_blend[filename+'_val'+str(fold)] = dic_log['yval'][fold]


#params
n_folds = len(folds)
test_size = .1
n_models = len(l_filenames)
nthread = 8
seed = 123





# clf = linear_model.SGDClassifier(loss='log', penalty='l2')
clf = linear_model.LogisticRegression(C=10, penalty='l2')
# clf = linear_model.LinearRegression()


skf = cross_validation.ShuffleSplit(len(pd_blend), n_iter=n_folds, test_size=test_size, random_state=seed)

for fold_indice, (tr_idx, te_idx) in enumerate(skf):

    X_cols = [col for col in pd_blend if 'pred{}'.format(fold_indice) in col]
    Y_cols = [col for col in pd_blend if 'val{}'.format(fold_indice) in col]

    X = np.array(pd_blend[X_cols]).astype(float)
    Y = np.array(pd_blend[Y_cols]).mean(1).astype(int)

    xtrain = X[tr_idx]
    xval = X[te_idx]

    ytrain = Y[tr_idx]
    yval = Y[te_idx]

    clf.fit(xtrain, ytrain)

    valpred = reshapePrediction(clf.predict_proba(xval))
    trainpred = reshapePrediction(clf.predict_proba(xtrain))


    train_err = eval_func(ytrain, trainpred)
    val_err = eval_func(yval, valpred)

    print(train_err, val_err)





#
# l_filenames = glob.glob1(folder, '*.csv') ; print(l_filenames)
#
# pd_blend = pd.DataFrame()
# for filename in l_filenames:
#     pd_temp = pd.read_csv(folder + filename)
#     pd_blend[filename] = pd_temp['PredictedProb']
#     test_idx = pd_temp['ID']
#
# X_test = np.array(pd_blend).astype(float)
# testpred = clf.predict_proba(X_test)
# testpred = reshapePrediction(testpred)
#
# pd_submission = pd.DataFrame({'ID':test_idx, 'PredictedProb':testpred})
# pd_submission.to_csv(CODE_FOLDER + 'diclogs/' + 'test' + '.csv', index=False)




    l_filenames = glob.glob1(folder, '*.csv') ; print(l_filenames)

    pd_blend = pd.DataFrame()
    for filename in l_filenames:
        pd_temp = pd.read_csv(folder + filename)
        pd_blend[filename] = pd_temp['PredictedProb']
        test_idx = pd_temp['ID']

    testpred = pd_blend.mean(1).values

    pd_submission = pd.DataFrame({'ID':test_idx, 'PredictedProb':testpred})
    pd_submission.to_csv(CODE_FOLDER + 'diclogs/' + 'test' + '.csv', index=False)


