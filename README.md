# eARDS
eARDS Model Code Base


## How to run the code

Run model.py file to test the eARDS model performance.

 > python model.py

This script takes following input file paths:

|File|Type|
----|-----|
Data|CSV|
Demographics|CSV|
Age|CSV|
Comorbidites|CSV|

The Data file contains following variables with the name mentioned in the table below:

Patient Info/Vital/Labs|Variable|Variable Type|Unit|
-----------------------|--------|-------------|----|
Patient ID|patient_id|Unique Number|None|
Time|time|Time stamp|datatime|
Albumin|albumin|Continous||
Bicarbonate|bicarbonate|Continous||
Bilirubin|bilirubin|Continous||
Creatinine|creatinine|Continous|
Glucose|glucose|Continous|
Hematocrit|hematocrit|Continous|
PEEP|peep|Continous|
Sodium|sodium|Continous|
WBC|wbc|Continous|
Heart Rate|heart_rate|Continous|
Mean Arterial Pressure|map|Continous|
PaCo2|pco2|Continous|
PaO2|pao2|Continous|
FiO2|fio2|Continous|
Plateau Pressure|pp|Continous|
Platalet Count|plat_cnt|Continous|
Systolic Blood Pressure|sbp|Continous|
Temperature|temperature|Continous|
Tidal Volume|tidal_v|Continous|
O2 Flow|o2_flow|Continous|
Chloride|chloride|Continous|
Lactate|lactate|Continous|
Calcium|calcium|Continous|
Respiratory Rate|respiratory_rate|Continous|
Pattasium|potassium|Continous|
Anion Gap|anion_gap|Continous|
SpO2|spo2|Continous|
Oxgen Therapy|oxygen_therapy|Binary Indicator|None|
Mechanical Ventilation|mech_ventilation|Binary Indicator|None|
Vasopressor|vasopresso|Binary Indicator|None|
Vasocount|vasocount|Binary Indicator|None|
Ionotrope|ionotrope|Binary Indicator|None|
Ionocount|ionocount|Binary Indicator|None|

The Demographics file contains following variables with the name mentioned in the table below:

Demographic|Variable|
-----------|--------|
Person ID|personid|
Gender|gender|


The Age file contains following variables with the name mentioned in the table below:

Age|Variable|
---|--------|
Person ID|personid|
Age|age|


The Comorbidity file contains following variables with the name mentioned in the table below:

Comorbidity|Variable|Variable Type|
-----------|--------|-------------|
Person ID|personid|Unique Number|
Congestive Heart Failure|congestive_heart_failure|Binary Indicator|
Cardiac Arrhythmias|cardiac_arrhythmias|Binary Indicator|
Valvular Disease|valvular_disease|Binary Indicator|
Hypertension|hypertension|Binary Indicator|
Chronic Pulmonary|chronic_pulmonary|Binary Indicator|
Diabetes Uncomplicated|diabetes_uncomplicated|Binary Indicator|
Diabetes Complicated|diabetes_complicated|Binary Indicator|
Renal Failure|renal_failure|Binary Indicator|
Liver Disease|liver_disease|Binary Indicator|
Metastatic Cancer|metastatic_cancer|Binary Indicator|
Rheumatoid Arthritis|rheumatoid_arthritis|Binary Indicator|
Obesity|obesity|Binary Indicator|
