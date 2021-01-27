import pandas as pd
import numpy as np
import pickle 
import xgboost as xgb
from utils import test_performance, mean_confidence_interval
from preprocess import load_data


model_pred_covid = pickle.load(open("XBG_HF_Covid.pickle.dat", "rb"))

data_path = '/data/jupyter/CVD/SQL_MAX_DATA/added vaso data/HF_final_vaso.csv'
demgraphic_path = '/data/jupyter/CVD/HF/demographics.csv'
age_path = '/data/jupyter/CVD/HF/age.csv'
comorbidity_path = '/data/jupyter/CVD/HF/comorbidity.csv'

data = load_data(data_path, demgraphic_path, age_path, comorbidity_path)


test_acc = test_performance(model_pred_covid, data)




