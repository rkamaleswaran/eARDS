import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import confusion_matrix
from sklearn import linear_model
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.utils import shuffle
from sklearn.model_selection import cross_validate, GroupShuffleSplit
import scipy.stats


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h


def test_performance(model, data, hours=[6],thresh=0.55):

    gss3 = GroupShuffleSplit(n_splits=10, train_size=0.8, random_state=42)
    all_time_auc_emory = []
    ppv_time = []
    sen_time = []
    spe_time = []
    fp_all = []
    fn_all = []
    tn_all = []
    tp_all = []
    y_all_pred_hf_covid_try = []
    y_all_true_hf_covid_try = []

    for train_idx, test_idx in gss3.split(data, data['Label'], data['subject_id']):

        train_emory = data.iloc[train_idx]

        uniIds_emory = train_emory['subject_id'].unique()
        sep_emory = []

        for p in uniIds_emory:
            temp = train_emory[train_emory['subject_id']==p]
            temp = temp.sort_values(by='time')
            temp = temp.reset_index(drop=True)
            sep_emory.append(temp)

        auc_time_emory = []
        for hour in hours:
            y_true = np.array([])
            y_pred = np.array([])
            le = 0
            for p in sep_emory:
                print(le)
                le = le + 1
                p = p.iloc[-1-hour-8:-1-hour,:]
                temp_pred = p['Label'].values
                y_pred = np.append(y_pred, temp_pred,axis=0)
                dcovid_temp = xgb.DMatrix((p[predictors]), p['Label'])
                temp_true = model.predict(dcovid_temp)
                y_true = np.append(y_true, temp_true,axis=0)

                cm1 = confusion_matrix(temp_pred,(temp_true>0.6)*1)
                if len(cm1)!=1 and len(cm1)!=0 :
                    FP1 = cm1[0][1]
                    FN1 = cm1[1][0]
                    TP1 = cm1[1][1]
                    TN1 = cm1[0][0]
                    fp_all.append(FP1)
                    fn_all.append(FN1)
                    tn_all.append(TN1)
                    tp_all.append(TP1)
                elif len(cm1)==1 and max(temp_pred) == 1:
                    fp_all.append(0)
                    fn_all.append(0)
                    tn_all.append(0)
                    tp_all.append(cm1[0][0])
                elif len(cm1)==1 and max(temp_pred) == 0:
                    fp_all.append(0)
                    fn_all.append(0)
                    tn_all.append(cm1[0][0])
                    tp_all.append(0)           

            auc_time_emory.append((metrics.roc_auc_score(y_pred, y_true),hour*2))
            if hour in hours:
                cm = confusion_matrix(y_pred,(y_true>thresh)*1)
                TP = cm[1][1]
                TN = cm[0][0]
                FP = cm[0][1]
                FN = cm[1][0]

                TPR = TP/(TP+FN)
                sen_time.append(TPR)
                TNR = TN/(TN+FP) 
                spe_time.append(TNR)
                PPV = TP/(TP+FP)
                ppv_time.append(PPV)

            y_all_pred_hf_covid_try.append(y_pred)
            y_all_true_hf_covid_try.append(y_true)       
            
        all_time_auc_emory.append(auc_time_emory)     

    results = pd.DataFrame(all_time_auc_emory, columns=['AUC', 'Time before onset(in Hrs)'])

    return results
















