
# coding: utf-8

import pandas as pd
import numpy as np
import itertools
from sklearn.model_selection import KFold  
from sklearn import svm
from sklearn.model_selection import train_test_split
import math
#from xgboost import XGBClassifier
from sklearn.neighbors import KNeighborsClassifier
import easy_excel
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import *
import sklearn.ensemble
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import roc_curve, auc
import sys
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB  
import subprocess
from sklearn.utils import shuffle
import itertools
from sklearn.ensemble import GradientBoostingClassifier
import sys
from sklearn.feature_selection import  f_classif
import warnings
import os
import argparse
import ItSVM
warnings.filterwarnings('ignore')


def performance(labelArr, predictArr):
    #labelArr[i] is actual value,predictArr[i] is predict value
    TP = 0.; TN = 0.; FP = 0.; FN = 0.
    for i in range(len(labelArr)):
        if labelArr[i] == 1 and predictArr[i] == 1:
            TP += 1.
        if labelArr[i] == 1 and predictArr[i] == 0:
            FN += 1.
        if labelArr[i] == 0 and predictArr[i] == 1:
            FP += 1.
        if labelArr[i] == 0 and predictArr[i] == 0:
            TN += 1.
    if (TP + FN)==0:
        SN=0
    else:
        SN = TP/(TP + FN) #Sensitivity = TP/P  and P = TP + FN
    if (FP+TN)==0:
        SP=0
    else:
        SP = TN/(FP + TN) #Specificity = TN/N  and N = TN + FP
    if (TP+FP)==0:
        precision=0
    else:
        precision=TP/(TP+FP)
    if (TP+FN)==0:
        recall=0
    else:
        recall=TP/(TP+FN)
    GM=math.sqrt(recall*SP)
    #MCC = (TP*TN-FP*FN)/math.sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
    return precision,recall,SN,SP,GM,TP,TN,FP,FN

def SVM_distance(inputname,outputname,distance,crossvalidation_values,CPU_values,SVM_distance_results):
    datapath =inputname
    classifier="SVM"
    mode="crossvalidation"
    print "start"
    train_data = pd.read_csv(datapath, header=None, index_col=None)
    print len(train_data)
    Y = list(map(lambda x: 1, xrange(len(train_data) // 2)))
    Y2 = list(map(lambda x: 0, xrange(len(train_data) // 2)))
    Y.extend(Y2)
    Y = np.array(Y)
    F, pval = f_classif(train_data, Y)
    idx = np.argsort(F)
    selected_list_=idx[::-1]
    F_sort_value=[F[e] for e in selected_list_]
    with open(SVM_distance_results+outputname+"all_dimension_results.txt",'w') as f:
            f.write(str(F_sort_value)+"\n")
    with open(SVM_distance_results+outputname+"all_dimension_results.txt",'a') as f:
            f.write(str(selected_list_)+"\n")
    
    print "deal with data"
    selected_list_=[a  for a,b in zip(selected_list_,F_sort_value) if not math.isnan(b)]
    with open(SVM_distance_results+outputname+"all_dimension_results.txt",'a') as f:
            f.write(str(selected_list_)+"\n")
    
    bestACC=0
    best_c=0
    best_g=0
    best_dimension=0
    all_dimension_results=[]
    select_list=[]
    best_savedata=""
    select_num1=0;
    for select_num in range(0,len(selected_list_),distance):
        if select_num > 0:
           for select_num1 in range(select_num-distance+1,select_num+1):  
               temp_data=selected_list_[select_num1]
               select_list.append(int(temp_data))
               train_data2=train_data.values
               X_train=pd.DataFrame(train_data2)
               X_train=X_train.iloc[:,select_list]
               X = np.array(X_train)
        else:
            temp_data=selected_list_[select_num]
            select_list.append(int(temp_data))
            train_data2=train_data.values
            X_train=pd.DataFrame(train_data2)
            X_train=X_train.iloc[:,select_list]
            X = np.array(X_train)
        svc = svm.SVC(probability=True)
        parameters = {'kernel': ['rbf'], 'C':map(lambda x:2**x,np.linspace(-2,5,7)), 'gamma':map(lambda x:2**x,np.linspace(-5,2,7))}
        clf = GridSearchCV(svc, parameters, cv=crossvalidation_values, n_jobs=CPU_values, scoring='accuracy')
        clf.fit(X, Y)
        C=clf.best_params_['C']
        gamma=clf.best_params_['gamma']
       
        y_predict=cross_val_predict(svm.SVC(kernel='rbf',C=C,gamma=gamma),X,Y,cv=crossvalidation_values,n_jobs=CPU_values)
        y_predict_prob=cross_val_predict(svm.SVC(kernel='rbf',C=C,gamma=gamma,probability=True),X,Y,cv=crossvalidation_values,n_jobs=CPU_values,method='predict_proba')
        
        joblib.dump(clf,SVM_distance_results+outputname+"_"+classifier+mode+str(select_num+1)+".model")
        predict_save=[Y.astype(int),y_predict.astype(int),y_predict_prob[:,1]]
        predict_save=np.array(predict_save).T
        #pd.DataFrame(predict_save).to_csv('Before_'+path+classifier+mode+outputname+"_"+'_predict_crossvalidation.csv',header=None,index=False)
        ROC_AUC_area=metrics.roc_auc_score(Y,y_predict_prob[:,1])
        ACC=metrics.accuracy_score(Y,y_predict)
        precision, recall, SN, SP, GM, TP, TN, FP, FN = performance(Y, y_predict)
        F1_Score=metrics.f1_score(Y, y_predict)
        F_measure=F1_Score
        MCC=metrics.matthews_corrcoef(Y, y_predict)
        pos=TP+FN
        neg=FP+TN
        savedata=[[['SVM'+"C:"+str(C)+"gamma:"+str(gamma),ACC,precision, recall,SN, SP, GM,F_measure,F1_Score,MCC,ROC_AUC_area,TP,FN,FP,TN,pos,neg]]]
        if ACC>bestACC:
            bestACC=ACC
            best_c=C
            best_g=gamma
            best_savedata=savedata
            best_dimension=X.shape[1]
        print savedata
        print X.shape[1]
        with open(SVM_distance_results+outputname+"all_dimension_results.txt",'a') as f:
            f.write(str(savedata)+"\n")
        all_dimension_results.append(savedata)
    print bestACC
    print best_c
    print best_g
    print best_dimension
    y_predict1=cross_val_predict(svm.SVC(kernel='rbf',C=best_c,gamma=best_g),X,Y,cv=crossvalidation_values,n_jobs=CPU_values)
    y_predict_prob1=cross_val_predict(svm.SVC(kernel='rbf',C=best_c,gamma=best_g,probability=True),X,Y,cv=crossvalidation_values,n_jobs=CPU_values,method='predict_proba')
    predict_save1=[Y.astype(int),y_predict1.astype(int),y_predict_prob1[:,1]]
    predict_save1=np.array(predict_save1).T
    pd.DataFrame(predict_save1).to_csv(SVM_distance_results+outputname+"_"+classifier+mode+'_best_dim_pro_features.csv',header=None,index=False)
    easy_excel.save("SVM_crossvalidation",[str(best_dimension)],best_savedata,SVM_distance_results+outputname+"_"+classifier+mode+'_best_ACC.xls')
    return y_predict_prob1[:,1]
def probability_combine():
    nowpath = os.getcwd()
    SVM_distance_results = nowpath + "\\" + 'SVM_distance_results\\'
    print(SVM_distance_results)
    os.mkdir(SVM_distance_results)

    feature_extraction_files = nowpath + "\\feature_extraction\\"
    print(feature_extraction_files)

    #path_file_number = len(os.listdir(feature_extraction_files))
    prob_combine = []
    args = ItSVM.getopt()

    crossvalidation_values=args.cv_number
    print(crossvalidation_values)
    CPU_values=args.CPU_value

    for name in os.listdir(feature_extraction_files):
        print(name)
        outputname = name.split('.')[0]
        inputname = feature_extraction_files + name###传入路径
        if '2RFH' in name:
            distance = args.two_RFH_dis
        elif 'AthMethPre' in name:
            distance = args.Ath_dis
        elif 'KNN' in name:
            distance = args.knn_dis
        elif 'MMI' in name:
            distance = args.mmi_dis
        elif 'PCP' in name:
            distance = args.pcp_dis
        elif 'PseDNC' in name:
            distance = args.psednc_dis
        elif 'PseEIIP' in name:
            distance = args.pseeiip_dis
        elif 'RFH' in name:
            distance = args.rfh_dis
        print(distance)
        res = SVM_distance(inputname, outputname,distance, crossvalidation_values, CPU_values, SVM_distance_results)
        prob_combine.append(res)
    prob_combine = np.array(prob_combine).T
    pd.DataFrame(prob_combine).to_csv("prob_8D.csv", header=None, index=False)

