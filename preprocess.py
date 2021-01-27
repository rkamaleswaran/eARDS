import random
import pandas as pd
import numpy as np
from multiprocessing import Pool
from tqdm import tqdm

def f_map(data):
    chunks=[data[i::5] for i in range(5)]
    pool = Pool(processes=5)
    result = pool.map(xgboost_data_creation,chunks)

    return result

def xgboost_data_creation(data):
    for i in range(len(data)):
      data[i] = data[i].drop(['ratio'],axis=1)
    var_to_impute = [x for x in data[0].columns if x not in ['mech_ventilation','height','oxygen_therapy','subject_id','time_index']]
      
    print(1) 
    df_median = data[0][var_to_impute].median().add_suffix('_median').to_frame().transpose()
    for i in range(len(data)-1):
      df_median = df_median.append(data[i+1][var_to_impute].median().add_suffix('_median').to_frame().transpose(),ignore_index=True)
    print(2)
    df_max = data[0].max().add_suffix('_max').to_frame().transpose()
    for i in range(len(data)-1):
      df_max = df_max.append(data[i+1].max().add_suffix('_max').to_frame().transpose(),ignore_index=True)
    print(3)
    df_min = data[0][var_to_impute].min().add_suffix('_min').to_frame().transpose()
    for i in range(len(data)-1):
      df_min = df_min.append(data[i+1][var_to_impute].min().add_suffix('_min').to_frame().transpose(),ignore_index=True)
    print(4)
    df_std = data[0][var_to_impute].std().add_suffix('_std').to_frame().transpose()
    for i in range(len(data)-1):
      df_std = df_std.append(data[i+1][var_to_impute].std().add_suffix('_std').to_frame().transpose(),ignore_index=True)
    print(5)
    df_skew = data[0][var_to_impute].skew().add_suffix('_skew').to_frame().transpose()
    for i in range(len(data)-1):
      df_skew = df_skew.append(data[i+1][var_to_impute].skew().add_suffix('_skew').to_frame().transpose(),ignore_index=True)
    print(6)

    
    df_data = df_median
    df_data = df_data.join(df_max)
    df_data = df_data.join(df_min)
    df_data = df_data.join(df_std)
    df_data = df_data.join(df_skew)

    return df_data



def load_data(data_path, demgraphic_path, age_path, comorbidity_path, dataset='HF', time_before_onset=24, o_window=24, p_window=4, onset_after=1):

  def timedelta_to_hour(time):
      d = 24*(time.days)
      h = (time.seconds)/3600
      total_hours = d + h 
      return total_hours

  def seperate_patients(p1):
      subHadmID = []
      uniH = p1['hadm_id'].unique()
      p1['time'] = pd.to_datetime(p1['time'])
      for id in uniH:
          subHadmID.append(p1[p1['hadm_id'] == id])    
      finalHadms = []
      temp = subHadmID[0]
      if(len(subHadmID) == 1):
          finalHadms.append(temp)
      i=0    
      while i < len(subHadmID)-1:
          k = 0
          if((min(subHadmID[i+1]['time']) - max(subHadmID[i]['time'])).days < 30 ):   
              temp = temp.append(subHadmID[i+1])
              i=i+1
              
          else:
              finalHadms.append(temp)
              temp = subHadmID[i+1]
              i=i+1
          if(i==len(subHadmID)-1):
              finalHadms.append(temp)
              
      return finalHadms

  def ards_criterion(p,criterion,time_before_onset):
      if(criterion == 'berlin'):
          p['ratio'] = p['pao2']/(p['fio2']/100)
          i=0
          while(i < len(p)):
              kemp = p['ratio'][p.index[i]]     
              if(kemp < 300 and p['peep'][p.index[i]]>=5):
                  break
              i=i+1 
              
          if(i==len(p)):
              return -1        
          return p.index[i]

  def prepocessed_patients(p, o_window, p_window,onset_after,time_before_onset):
      onset_index = int(timedelta_to_hour(ards_criterion(p,'berlin',time_before_onset) - p.index[0])/2)
      part1 = p.iloc[0:onset_index-p_window-o_window,:]
      part1['label'] = 0
      part2 = p.iloc[onset_index-p_window-o_window:onset_index,:]
      part2['label'] = 1
      part3 = p.iloc[onset_index:onset_index + onset_after,:]
      part3['label'] = 1
      part1 = part1.append(part2)
      part1 = part1.append(part3)
      return part1




  def preprocessing(dataset, per_to_num_dic, num_to_per_dic, uniIDS, criterion, time_before_onset, o_window, p_window, onset_after):
      
      dataset = dataset.rename(columns={'personid':'subject_id'})
      dataset['mech_ventilation'] = dataset['mech_ventilation'].notnull().astype(int)
      dataset['oxygen_therapy'] = dataset['oxygen_therapy'].notnull().astype(int)

      uniSubIDs = uniIDS
      uniSubIDs.sort()
      dataSubID = [] 
   
      for id in tqdm(range(len(uniSubIDs))):
          dataSubID.append(dataset[dataset['subject_id'] == uniSubIDs[id]])
          if id>50:
            break
     
      print('Data Segregation Done')
        
      for i in range(len(dataSubID)):    
          dataSubID[i]=dataSubID[i].sort_values(by=['time'])    
      
      var_to_impute = [x for x in dataset.columns if x not in ['mech_ventilation','height','weight','oxygen_therapy','subject_id', 'time']]
      global_median = dataset[var_to_impute].median()
      print("1 Done")

      # Median of the all the patients in the MIMIC III Dataset   
      global_median['pao2'] = 109
      global_median['fio2'] = 32
      global_median['albumin'] = 3.1
      global_median['bicarbonate'] = 25
      global_median['bilirubin'] = 0.9
      global_median['creatinine'] = 1
      global_median['glucose'] = 125
      global_median['hematocrit'] = 30.5
      global_median['peep'] = 5
      global_median['sodium'] = 138
      global_median['wbc'] = 9.1
      global_median['heart_rate'] = 92 
      global_median['map'] = 77
      global_median['pco2'] = 41
      global_median['pp'] = 21
      global_median['plat_cnt'] = 215
      global_median['sbp'] = 119
      global_median['temperature'] = 36
      global_median['tidal_v'] = 499
      global_median['lactate'] = 1.8
      global_median['calcium'] = 1.13 
      global_median['respiratory_rate'] = 20
      global_median['potassium'] = 4.1
      global_median['anion_gap'] = 13
      global_median['o2_flow'] = 4
      global_median['chloride'] = 104
      global_median['spo2'] = 97
      global_median['ionotrope'] = 0
      global_median['vasocount'] = 0
      global_median['ionocount'] = 0
      global_median['vasopressor'] = 0


      final_patients = dataSubID    

      final_patients_per_hour = []

      for id in final_patients:
          id['time'] = pd.to_datetime(id['time'])
          id['subject_id'] = per_to_num_dic[max(id['subject_id'])] 
          temp = id.resample('120min', on='time').median()        
          temp = temp.ffill(axis=0)
          temp = temp.fillna(global_median)
          final_patients_per_hour.append(temp)
      
      final_ards_patients = []
      training_ards_patients = []
      training_nonards_patients = []

      print("Resampling and Imputation Done")
      
      if(criterion=='berlin'):
          for p in final_patients_per_hour:
              ards_onset_time = ards_criterion(p,criterion,time_before_onset)
              if(ards_onset_time==0):
                  continue
              if(ards_onset_time==-1):
                  p['label']=0
  #                 p['ratio'] = p['pao2']/p['fio2']
                  training_nonards_patients.append(p)
                  continue
                  
              admission_time = p.index[0]
              time_diff =  timedelta_to_hour(ards_onset_time - admission_time)
              if(time_diff >= time_before_onset):
                  print(p['subject_id'][0])
                  final_ards_patients.append(p)        
                  
          
          for p in final_ards_patients:
              temp = prepocessed_patients(p, o_window, p_window, onset_after,time_before_onset)        
              training_ards_patients.append(temp)
      
      print('Step 1 Done')

      return training_ards_patients, training_nonards_patients


  data_try = pd.read_csv(data_path)

  if dataset=='HF':
    col_new=['albumin', 'bicarbonate', 'bilirubin',
           'creatinine', 'glucose', 'hematocrit', 'peep', 'sodium', 'wbc',
           'heart_rate', 'map', 'pco2', 'pao2', 'fio2', 'pp', 'plat_cnt', 'sbp',
           'temperature', 'tidal_v', 'o2_flow', 'chloride', 'lactate', 'calcium',
           'respiratory_rate', 'potassium', 'anion_gap', 'spo2'] 


    perc = pd.DataFrame(columns = ['feature','95th','99th'])
    for col in col_new:
        temp = pd.DataFrame(columns = ['feature','95th','99th'], data = np.array([col,np.nanpercentile(data_try[col].values,95),np.nanpercentile(data_try[col].values,99)]).reshape(1,3))
        perc = perc.append(temp)
    perc = perc.reset_index(drop=True)

    perc['99th'] = pd.to_numeric(perc['99th'])    

    median_hf = data_try[col_new].median()

    i=0
    for col in col_new:
        data_try.loc[data_try[col] > perc['99th'][i], col] = median_hf[col]
        i=i+1
  

  def data_creation(training_ards, training_nonards, stride, hours):
    
    ards_patients = []
    nonards_patients = []
    num = 0
      
    for p in training_ards:
      print(num)
      num = num + 1

      for k in range(int((len(p)-hours)/stride)+1):
        temp = p.iloc[len(p) - stride*k - hours : len(p) - (stride*k),:]
        temp['id'] = num
        temp['time_index'] = int((len(p)-hours)/stride) - k 
        ards_patients.append(temp)      
    
    for p in training_nonards:
      print(num)
      num = num + 1

      for k in range(int((len(p)-hours)/stride)+1):
        temp = p.iloc[len(p) - stride*k - hours : len(p) - (stride*k),:]
        temp['id'] = num
        temp['time_index'] = int((len(p)-hours)/stride) - k 
        nonards_patients.append(temp)   

    
    return ards_patients, nonards_patients


  def preproces_ards_data(data):
      time_index = data['time_index_max'].astype(int) 
      subject_id = data['subject_id_max'].astype(int)
      mech_ven = data['mech_ventilation_max'].astype(int)
      oxy_ther = data['oxygen_therapy_max'].astype(int)
      label = data['label_max'].astype(int)
      ids  = data['id_max'].astype(int)
      data = data.drop(['label_min','label_max','label_median','label_std','label_skew','subject_id_max','oxygen_therapy_max'],axis=1)
      data = data.drop(['id_min','id_max','id_median','id_std','id_skew','mech_ventilation_max','time_index_max'],axis=1)
      data['mech_ventilation'] = mech_ven
      data['oxygen_therapy_max'] = oxy_ther
      data['subject_id'] = subject_id
      data['time'] = time_index
      data['id'] = ids
      data['Label'] = label 
      data = data.sort_values(by='id')
      
      return data

  def preproces_non_ards_data(data):
      time_index = data['time_index_max'].astype(int) 
      subject_id = data['subject_id_max'].astype(int)
      mech_ven = data['mech_ventilation_max'].astype(int)
      oxy_ther = data['oxygen_therapy_max'].astype(int)
      label = data['label_max'].astype(int)
      ids  = data['id_max'].astype(int)
      data = data.drop(['label_max','subject_id_max','oxygen_therapy_max'],axis=1)
      data = data.drop(['id_max','mech_ventilation_max','time_index_max'],axis=1)
      data['mech_ventilation'] = mech_ven
      data['oxygen_therapy_max'] = oxy_ther
      data['subject_id'] = subject_id
      data['time'] = time_index
      data['id'] = ids
      data['Label'] = label 
      data = data.sort_values(by='id')
      
      return data

  drop_cols = ['vasopressor_skew','vasopressor_median','vasopressor_std','vasopressor_min',
               'vasocount_skew','vasocount_median','vasocount_std','vasocount_min',
               'ionotrope_skew','ionotrope_median','ionotrope_std','ionotrope_min',
               'ionocount_skew','ionocount_median','ionocount_std','ionocount_min'
              ]

  per_to_num_dic = {}
  uniperIDs = data_try['personid'].unique()
  i = 0
  for ids in uniperIDs:
      per_to_num_dic[ids] = i
      i = i + 1


  num_to_per_dic = {}
  for ids in uniperIDs:
      num_to_per_dic[per_to_num_dic[ids]] = ids
    
  training_ards, training_nonards = preprocessing(data_try, per_to_num_dic, num_to_per_dic, uniperIDs, 'berlin', time_before_onset, o_window, p_window, onset_after)
  ards_data, nonards_data = data_creation(training_ards,  training_nonards, 1, 8)

  df1 = f_map(ards_data)
  df2 = f_map(nonards_data)

  dff_ards = df1[0]
  for i in range(len(df1)-1):
      dff_ards = dff_ards.append(df1[i+1])

  dff_nonards = df2[0]
  for i in range(len(df2)-1):
      dff_nonards = dff_nonards.append(df2[i+1])

  ards = preproces_ards_data(dff_ards)
  nonards = preproces_ards_data(dff_nonards)

  covid_final_data = ards.append(nonards)
  data = covid_final_data.reset_index(drop=True)

  data = data.drop(drop_cols,axis=1)
  data = data.rename(columns={'vasopressor_max':'vasopressor', 'vasocount_max':'vasocount','ionotrope_max':'ionotrope','ionocount_max':'ionocount'})

  demo = pd.read_csv(demgraphic_path)
  age = pd.read_csv(age_path)

  ageDic = age[['age_at_encounter','personid']].set_index('personid').T.to_dict('list')
  tempDic1 = demo[['gender','personid']].set_index('personid').T.to_dict('list')

  data['age_18-40'] = 0
  data['age_40-60'] = 0
  data['age_60-80'] = 0
  data['age_80+'] = 0



  indexAgeDrop = []
  subID = []
  for i in range(len(data)):
      print(i)
      tempSub = num_to_per_dic[data['subject_id'][i]]
      if tempSub not in ageDic:
          subID.append(tempSub)
          continue
      tempAge = ageDic[tempSub][0]
      if(tempAge >= 18 and tempAge < 40):
          data['age_18-40'][i] = 1
      elif(tempAge >= 40 and tempAge < 60):
          data['age_40-60'][i] = 1
      elif(tempAge >= 60 and tempAge < 80):
          data['age_60-80'][i] = 1
      elif(tempAge >= 80):
          data['age_80+'][i] = 1
      else:
          indexAgeDrop.append(i)

  data = data.drop(indexAgeDrop)
  data = data.reset_index(drop=True)


  data['gender'] = 0
  for i in range(len(data)):
      tempSub1 = num_to_per_dic[data['subject_id'][i]]
      if tempSub1 not in tempDic1:
          continue
      tempAge1 = tempDic1[tempSub1][0]
      if(tempAge1=='Male'):
          data['gender'][i] = 1
      elif(tempAge1=='Female'):
          data['gender'][i] = 0


  corm = pd.read_csv(comorbidity_path)

  tempCom = corm[['congestive_heart_failure', 'cardiac_arrhythmias', 'valvular_disease', 'hypertension', 'chronic_pulmonary', 'diabetes_uncomplicated', 'diabetes_complicated', 'renal_failure', 'liver_disease', 'metastatic_cancer', 'rheumatoid_arthritis', 'obesity','personid']].set_index('personid').T.to_dict('list')
  cols = [x for x in corm.columns if x not in ['personid','encounterid']]
  for j in cols:
      data[j] = 0

  cormToDrop = []
  for ids in range(len(data)):
      print(ids)
      for j in range(len(cols)):
          tempC = num_to_per_dic[data['subject_id'][ids]]
          if tempC not in tempCom:
              cormToDrop.append(ids)
              continue
          data[cols[j]][ids] = tempCom[tempC][j]

  droplist = list(set(cormToDrop))
  data = data.drop(droplist)

  data_file_name = str(dataset) + '-P-8-S-1-O' + str(time_before_onset*2) + '-AFO-' + str(onset_after) + '.csv'
  data.to_csv(data_file_name)

  return data