#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from pytz import timezone


# # SPRING 2021

# # APT Data

# In[2]:


#APT Additional Info import
apt_info = pd.read_excel("CS APT Problem.xlsx")
print(len(apt_info))


apt_info = apt_info[apt_info.index < apt_info[apt_info["apt_set"] == "CS201"].index[0]] # omit all info on CS201
apt_info = apt_info[apt_info["semester"]== "sp21"] # only get Spring 2021 semester

#cleaning time zones
apt_info["assign_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info["assign_date"]]
apt_info["due_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info["due_date"]]
apt_info["late_due"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info["late_due"]]
apt_info["late_due"] = apt_info["late_due"].fillna(apt_info["due_date"])


print(len(apt_info))

#apt_info.head()


# In[3]:


#student formative APT log import
formative = pd.read_csv("cs101sp21-apt-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(formative))
formative.head()


# In[4]:


#student summative APT log import
summative = pd.read_csv("cs101sp21-aptquiz-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(summative))
summative.head()


# In[5]:


#read in apt extra info data and clean
apt = {}
apt_quiz = {}

formative["timestamp"] = pd.to_datetime(formative.timestamp,unit='s').dt.tz_localize('utc')

formative = formative[formative["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)


summative["timestamp"] = pd.to_datetime(summative.timestamp,unit='s').dt.tz_localize('utc')

summative = summative[summative["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)
formative.head()


# In[6]:


# separate the submissions that were submitted during an apt set's assigned time range vs. extra practice 
extra = {} 
extra_quiz = {} 
for sem in ["sp21"]: 
    if sem not in extra: 
        extra[sem] = pd.DataFrame(columns = formative.columns)
    if sem not in extra_quiz:  
        extra_quiz[sem] = pd.DataFrame(columns = summative.columns)
    
    extra[sem] = formative[~formative["apt_name"].isin(set(apt_info[(apt_info["semester"]== sem) &
                                             (apt_info["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    
    formative = formative[formative["apt_name"].isin(set(apt_info[(apt_info["semester"]== sem) &
                                             (apt_info["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)

    extra_quiz[sem] = summative[~summative["apt_name"].isin(set(apt_info[(apt_info["semester"]== sem) &
                                             (apt_info["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    summative = summative[summative["apt_name"].isin(set(apt_info[(apt_info["semester"]== sem) &
                                             (apt_info["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)


# In[7]:


#combine sumamtive and formative dataframes
frames=[summative, formative]
sp21=pd.concat(frames)
print(len(sp21))
sp21.head()


# In[8]:


#df = pd.merge(apt_info, sp21, how = "left", on = "apt_name")
df = sp21.merge(apt_info[(apt_info["semester"]== 'sp21') &
                                             (apt_info["type"].isin(["formative",
                                              "summative_practice", "summative"]))].copy(deep = True).reset_index(drop = True),
                                              how = "left", on = "apt_name")
print(len(df))
df.head()


# In[9]:


df.dtypes


# In[10]:


#find student/apt combinations
grouped=df.groupby(['anonid', 'apt_name', 'apt_set'])['score'].max()
grouped.head()
display(grouped)


# In[11]:


#find max score per submission per student
new_df=df.groupby( [ "anonid", "apt_name", "apt_set"])['score'].max().to_frame(name = 'max_score').reset_index()
new_df.head()


# In[12]:


#clean column entry
new_df.replace('wrongclass', 0.0)
new_df.replace('nocompile', 0.0)
new_df['max_score'] = pd.to_numeric(new_df['max_score'], errors='coerce')


# In[13]:


#check column types
new_df.dtypes


# In[14]:


#add struggling column, where max apt score is less than 100%
new_df['struggling'] = new_df['max_score']<1.00000
print(len(new_df))
new_df.head()


# In[15]:


#sort for only struggling students
struggling_students = new_df[new_df['struggling'] == True] 
print(len(struggling_students))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_students)


# In[16]:


#count number of struggling students
new_df.groupby(['struggling']).count()


# In[17]:


struggling_students.groupby(['apt_set']).count()


# In[18]:


#number of struggles per student
struggling_count=struggling_students.groupby(['anonid']).count()
struggling_count.sort_values(by='apt_name', ascending=False)
print(len(struggling_count))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_count)


# In[19]:


#view number of struggles per student
sns.histplot(data = struggling_count, x = "apt_name")


# In[20]:


only_fail=df

only_fail=df
only_fail.replace('wrongclass', 0.0)
only_fail.replace('nocompile', 0.0)
only_fail['score'] = pd.to_numeric(only_fail['score'], errors='coerce')

only_fail = only_fail[only_fail['score'] < 1.000]




#only_fail = only_fail[only_fail['score'] == True] 
only_fail.head()


# In[21]:


only_fail.dtypes


# In[22]:


redefine=df.groupby( [ "anonid", "apt_name", "apt_set"]).count()
redefine = redefine[redefine.columns[~redefine.columns.isin(['score', 'semester', 'concept', 'type', 'mapping', 'assign_date', 'due_date', 'late_due', 'required', 'notes', 'other'])]]
redefine = redefine.rename(columns={'timestamp': 'num_submissions'})
redefine['struggling']=redefine['num_submissions']>=3
redefine.head()


# In[23]:


redefine=redefine.sort_values(by=['num_submissions'])
sns.histplot(data = redefine, x = "anonid")
median_submissions=redefine["num_submissions"].median()
max_submissions=redefine['num_submissions'].max()
mean_submissions=redefine['num_submissions'].mean()
print(median_submissions)
print(max_submissions)
print(mean_submissions)


# In[24]:


struggles = redefine[redefine['struggling'] == True] 
print(len(struggles))
struggles.head()


# In[25]:


struggles.groupby(['apt_set']).count()


# In[26]:


#number per anonid
struggles.groupby(['anonid']).count()


# In[27]:


by_apt_set=struggles.groupby( [ "anonid", "apt_set"]).count()
by_apt_set = by_apt_set[by_apt_set.columns[~by_apt_set.columns.isin(['struggling'])]]
by_apt_set = by_apt_set.rename(columns={'num_submissions': 'num_struggles'})
by_apt_set.head()


# In[28]:


num_students=struggles.groupby('anonid').count()
num_students = num_students[num_students.columns[~num_students.columns.isin(['struggling'])]]
num_students = num_students.rename(columns={'num_submissions': 'num_struggles'})
num_students = num_students.reset_index()
print(len(num_students))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(num_students)


# In[29]:


#total_struggling=pd.merge(struggling_students, num_students, on="anonid")
struggling_count = struggling_count.reset_index()
struggling_count_anon=struggling_count.iloc[: , :1]
num_students_anon=num_students.iloc[: , :1]

#struggling_count_anon.head()
#num_students_anon.head()

total_struggling = pd.concat([struggling_count_anon, num_students_anon], ignore_index=True)

total_strugglers=total_struggling.drop_duplicates()


#total_struggling=pd.merge(struggling_count, num_students, on="anonid")


# In[30]:


print(len(total_struggling))
print(len(total_strugglers))


# # Office Hours Data

# In[31]:


#import dataset
oh=pd.read_csv('cs101sp21-no-teacher-data-processed.csv')
print(len(oh))
oh.head()


# In[32]:


display(oh.iloc[1])


# In[33]:


office_hours=oh.rename(columns=oh.iloc[1]).drop([0, 1])


# In[34]:


office_hours.head()


# In[35]:


office_hours.dtypes


# In[ ]:





# In[36]:


office_hours['apt_question'] = pd.np.where(office_hours[['APT1', 'APT2', 'APT3', 'APT4', 'APT5', 'APT6', 'APT7', 'APT8', 'OTHER', 'Understanding a past assignment/APT']].eq('True').any(1, skipna=True), True, 
             pd.np.where(office_hours[['APT1', 'APT2', 'APT3', 'APT4', 'APT5', 'APT6', 'APT7', 'APT8', 'OTHER', 'Understanding a past assignment/APT']].eq('False').all(1), None, False))

office_hours.head()
                                           
                                           


# In[37]:


office_hour = office_hours[office_hours['apt_question'] == True] 
office_hour.head()


# In[38]:


apt_oh = office_hour[['anonStudent', 'requestedAt', 'startedAt','completedAt','APT1', 'APT2', 'APT3', 'APT4', 'APT5', 'APT6', 'APT7', 'APT8', 'OTHER', 'Understanding a past assignment/APT', 'I will need more help', 'I did not make progress']]
print(len(apt_oh))
apt_oh.head()


# In[39]:


apt_oh.loc[apt_oh.anonStudent == '8e8d8c04bd2e4559245eb4c640591447996c5ec8', 'set'] = 'x'

for ind in apt_oh.index:
    if apt_oh['APT1'][ind]=="True":
        apt_oh['set'][ind]="1"
    if apt_oh['APT2'][ind]=="True":
        apt_oh['set'][ind]="2"
    if apt_oh['APT3'][ind]=="True":
        apt_oh['set'][ind]="3"
    if apt_oh['APT4'][ind]=="True":
        apt_oh['set'][ind]="4"
    if apt_oh['APT5'][ind]=="True":
        apt_oh['set'][ind]="5"
    if apt_oh['APT6'][ind]=="True":
        apt_oh['set'][ind]="6"
    if apt_oh['APT7'][ind]=="True":
        apt_oh['set'][ind]="7"
    if apt_oh['APT8'][ind]=="True":
        apt_oh['set'][ind]="8"
    else:
        apt_oh['set'][ind]="0"
  
apt_oh = apt_oh.rename(columns={'set': 'apt_set'})    
apt_oh.head()


# In[40]:


num_oh_students = apt_oh.groupby(['anonStudent']).count()
num_oh_students = num_oh_students.sort_values(by='requestedAt', ascending=False)
mean_visits=num_oh_students["requestedAt"].median()
num_oh_students = num_oh_students['requestedAt']
print(len(num_oh_students))
print(mean_visits)
num_oh_students


# In[41]:


sns.histplot(data = num_oh_students)


# In[42]:


apt1 = apt_oh.groupby(['APT1']).count()
apt2 = apt_oh.groupby(['APT2']).count()
apt3 = apt_oh.groupby(['APT3']).count()
apt4 = apt_oh.groupby(['APT4']).count()
apt5 = apt_oh.groupby(['APT5']).count()
apt6 = apt_oh.groupby(['APT6']).count()
apt7 = apt_oh.groupby(['APT7']).count()
apt8 = apt_oh.groupby(['APT8']).count()
other = apt_oh.groupby(['OTHER']).count()

print('APT 1 has '+ apt1.iloc[1][True].astype(str)+ ' students')
print('APT 2 has '+ apt2.iloc[1][True].astype(str)+ ' students')
print('APT 3 has '+ apt3.iloc[1][True].astype(str)+ ' students')
print('APT 4 has '+ apt4.iloc[1][True].astype(str)+ ' students')
print('APT 5 has '+ apt5.iloc[1][True].astype(str)+ ' students')
print('APT 6 has '+ apt6.iloc[1][True].astype(str)+ ' students')
print('APT 7 has '+ apt7.iloc[1][True].astype(str)+ ' students')
print('APT 8 has '+ apt8.iloc[1][True].astype(str)+ ' students')
print('OTHER has '+ other.iloc[1][True].astype(str)+ ' students')


# In[43]:


oh_students = pd.DataFrame()
oh_students['oh_students']=apt_oh['anonStudent']
apt_students = pd.DataFrame()
apt_students['apt_students']=struggling_students['anonid']
apt_students.head()
print(len(apt_students))


# # Combining OH and APT

# In[44]:


nos=num_oh_students.to_frame(name = 'count').reset_index()
ns=num_students.rename(columns = {"anonid":"anonStudent"})
ns.head()

frames = [nos, ns]

result3 = pd.concat(frames).reset_index()
result3.head()
print(len(result3))
print('52 total OH Students, 157 struggling students, 209 combined')
print(len(result3['anonStudent'])-len(result3['anonStudent'].drop_duplicates()))
#result3.dtypes


# In[45]:


overlap=0
for student in ns['anonStudent']:
    for s in nos['anonStudent']:
        if student==s:
            overlap+=1
print(overlap)
print('of struggling students visited OH')
print(' ')
print('Every student who visited office hours for an APT was struggling. Of the struggling students, ~33% of them visited Office Hours.')
print(' ')
print('This shows that number of APT submissions is a good indicator of OH attendance for students')


# #### Next steps: keep only struggling students and APT OH students from larger datasets. Do this using for loops perhaps to make sure student = student who struggles and apt set=struggling apt set. Then, loop through both of these new datasets to see if there was an APT submission of ==1.000 during an OH session time (could consider extending by 30 mins or so) 

# In[46]:


#for s in df['anonid']:
#    for student in num_students['anonid']:
   #     if s==student:
  #          df['struggling']=True
#print(len(df))
#df.head()


# In[47]:


#df2 = df[df['struggling'] == True]
#print(len(df2))


# In[48]:


#count=0
#for ind in df.index:
#    for i in apt_oh.index:
#        if df['anonid'][ind]==apt_oh['anonStudent'][i] and df['apt_set'][ind]==apt_oh['apt_set'][i]:
   #         count+=1
#
#print(count)
        


# In[49]:


df = df.assign(result=df['anonid'].isin(num_students['anonid']).astype(bool))
df.head()


# In[50]:


df.groupby(['result']).count()


# In[51]:


anonids=df.groupby(['anonid']).count()
print(len(anonids))


# In[52]:


apt_oh=apt_oh.rename(columns={'anonStudent': 'anonid'})
apt_oh.dtypes


# In[53]:


mergedf=pd.merge(df, apt_oh, on=['anonid'])
print(len(mergedf))
mergedf.head()


# In[54]:


mergedf=mergedf.loc[mergedf['score'] == 1]
print(len(mergedf))
mergedf.head()


# In[55]:


mergedf['startedAt'] = pd.to_datetime(mergedf.startedAt).dt.tz_convert('utc')


# In[56]:


mergedf['requestedAt'] = pd.to_datetime(mergedf.requestedAt).dt.tz_convert('utc')


# In[57]:


mergedf['completedAt'] = pd.to_datetime(mergedf.completedAt).dt.tz_convert('utc')


# In[58]:


mergedf.dtypes


# In[59]:


duringoh=mergedf[(mergedf['timestamp'] >= mergedf['startedAt'])& (mergedf['timestamp'] <= mergedf['completedAt'])]
print(len(duringoh))


# In[60]:


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(duringoh)


# In[61]:


duringoh.groupby(['anonid']).count().sort_values(by='apt_name', ascending=False)


# In[62]:


strugglemerge=pd.merge(struggles, df, on=['anonid', 'apt_name'])
strugglemerge.head()


# In[63]:


struggleoh=pd.merge(strugglemerge, apt_oh, on=['anonid'])
struggleoh.head()


# In[64]:


struggleoh['startedAt'] = pd.to_datetime(struggleoh.startedAt).dt.tz_convert('utc')
struggleoh['requestedAt'] = pd.to_datetime(struggleoh.requestedAt).dt.tz_convert('utc')
struggleoh['completedAt'] = pd.to_datetime(struggleoh.completedAt).dt.tz_convert('utc')


# In[65]:


struggleduringoh=struggleoh[(struggleoh['timestamp'] >= struggleoh['startedAt'])& (struggleoh['timestamp'] <= struggleoh['completedAt'])]
print(len(struggleduringoh))


# In[66]:


#median score of submissions in total
struggleoh['score'].median()


# In[67]:


#median score of submissions that occur during OH
struggleduringoh['score'].median()


# In[68]:


#mean score of submissions that occur during OH
struggleduringoh['score'].mean()


# In[69]:


#median number of submissions of someone who goes to office hours and submits an APT during the OH time frame
struggleduringoh['num_submissions'].median()


# In[70]:


#median number of submissions for someone that goes to office hours
struggleoh['num_submissions'].median()


# In[71]:


#only include submissions with a perfect score
strugglepass=struggleduringoh.loc[struggleduringoh['score'] == 1]
print(len(strugglepass))


# In[72]:


#all rows for APT submissions of 1 that occurre during an OH session
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(strugglepass)


# In[73]:


#number of pass submissions during OH per student
strugglepass.groupby(['anonid']).count().sort_values(by='apt_name', ascending=False)


# In[74]:


#number of submissions of individual APTs during OH (median=1)
strugglepass.groupby(['anonid', 'apt_name']).count()


# In[75]:


#number successful APT submissions during OH per APT
strugglepass.groupby(['apt_name']).count().sort_values(by='anonid', ascending=False)


# In[76]:


#number successful APT submissions during OH per set
strugglepass.groupby(['apt_set_x']).count().sort_values(by='anonid', ascending=False)


# In[77]:


#total struggles per APT
struggles.groupby(['apt_name']).count().sort_values(by='struggling', ascending=False)


# In[78]:


#total apt set struggles
struggles.groupby(['apt_set']).count().sort_values(by='struggling', ascending=False)


# ###### Also, count number of submissions during an OH time that were not of score 1 and were never of score 1. Find max score for each (apt, student) combo during an OH timeslot and filter for those <1.

# In[79]:


nopass=struggleduringoh.groupby( [ "anonid", "apt_name", "apt_set_x", "completedAt"])['score'].max().to_frame(name = 'max_score').reset_index()
nopass.head()
print(len(nopass))


# In[80]:


nopass['not_pass'] = nopass['max_score']<1.00000


# In[81]:


nopass=nopass.loc[nopass['not_pass'] == True]
print(len(nopass))


# In[82]:


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(nopass)


# In[83]:


ohfail=pd.merge(nopass, df, on=['anonid', 'apt_name'])
ohfail.head()
print(len(ohfail))


# In[84]:


ohfail=ohfail[(ohfail['timestamp'] >= ohfail['completedAt'])]
print(len(ohfail))


# In[85]:


ohfail['difference']=ohfail['timestamp']-ohfail['completedAt']
ohfail.head()


# In[86]:


ohfail['difference']=ohfail['difference'].astype('timedelta64[m]').astype(int)

ohfail.head()


# In[87]:


conditions = [
    (ohfail['difference'] == 0),
    (ohfail['difference'] > 0) & (ohfail['difference'] <= 30),
    (ohfail['difference'] > 30) & (ohfail['difference'] <= 60),
    (ohfail['difference'] > 60) & (ohfail['difference'] <= 90),
    (ohfail['difference'] > 90) & (ohfail['difference'] <= 120),
    (ohfail['difference'] > 120) & (ohfail['difference'] <= 150),
    (ohfail['difference'] > 150) & (ohfail['difference'] <= 180),
    (ohfail['difference'] > 180) & (ohfail['difference'] <= 1440),
    (ohfail['difference'] > 1440)
    ]

# create a list of the values we want to assign for each condition
values = ['0', '1-30', '31-60', '61-90', '91-120', '121-150', '151-180', '180-1 day', '>1 day']

# create a new column and use np.select to assign values to it using our lists as arguments
ohfail['time_since_oh'] = np.select(conditions, values)

# display updated DataFrame
ohfail.head()


# In[88]:


ohfail.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()


# In[89]:


clean_ohfail=ohfail[(ohfail['time_since_oh'] != '0')]


# In[310]:


sns.boxplot(data=clean_ohfail, x="time_since_oh", y="score")


# In[91]:


sns.lineplot(data=clean_ohfail, x="time_since_oh", y="score")


# In[92]:


sns.lineplot(data=ohfail, x="difference", y="score")


# In[93]:


graph = sns.FacetGrid(ohfail, col ="anonid")
# map the above form facetgrid with some attributes
graph.map(plt.scatter, "difference", "score")
# show the object
plt.show()


# In[94]:


adapted1_ohfail=ohfail[(ohfail['time_since_oh'] != '180-1 day') & (ohfail['time_since_oh'] != '>1 day')]
adapted2_ohfail=ohfail[(ohfail['time_since_oh'] != '180-1 day')]
adapted3_ohfail=ohfail[(ohfail['time_since_oh'] != '180-1 day') & (ohfail['time_since_oh'] != '>1 day') & (ohfail['time_since_oh'] != '151-180') & (ohfail['time_since_oh'] != '121-150') & (ohfail['time_since_oh'] != '91-120')]
adapted4_ohfail=ohfail[(ohfail['time_since_oh'] != '180-1 day') & (ohfail['time_since_oh'] != '>1 day') & (ohfail['time_since_oh'] != '151-180') & (ohfail['time_since_oh'] != '121-150') & (ohfail['time_since_oh'] != '91-120') & (ohfail['time_since_oh'] != '61-90')]
adapted5_ohfail=ohfail[(ohfail['time_since_oh'] != '180-1 day') & (ohfail['time_since_oh'] != '>1 day') & (ohfail['time_since_oh'] != '151-180') & (ohfail['time_since_oh'] != '121-150') & (ohfail['time_since_oh'] != '91-120') & (ohfail['time_since_oh'] != '61-90') & (ohfail['time_since_oh'] != '31-60')]
adapted6_ohfail=ohfail[(ohfail['time_since_oh'] != '180-1 day') & (ohfail['time_since_oh'] != '>1 day') & (ohfail['time_since_oh'] != '151-180') & (ohfail['time_since_oh'] != '121-150') & (ohfail['time_since_oh'] != '91-120') & (ohfail['time_since_oh'] != '61-90') & (ohfail['time_since_oh'] != '31-60') & (ohfail['time_since_oh'] != '1-30')]


# In[95]:


adapted1_ohfail.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 180 mins after OH


# In[96]:


adapted2_ohfail.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 1 day after OH


# In[97]:


adapted3_ohfail.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 90 minutes from OH


# In[98]:


adapted4_ohfail.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 60 minutes from OH


# In[99]:


adapted5_ohfail.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 30 minutes from OH


# # FALL 2020

# In[100]:


#APT Additional Info import
apt_info_fa20 = pd.read_excel("CS APT Problem.xlsx")
print(len(apt_info))


apt_info_fa20 = apt_info_fa20[apt_info_fa20.index < apt_info_fa20[apt_info_fa20["apt_set"] == "CS201"].index[0]] # omit all info on CS201
apt_info_fa20 = apt_info_fa20[apt_info_fa20["semester"]== "fa20"] # only get Fall 2020 semester

#cleaning time zones
apt_info_fa20["assign_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_fa20["assign_date"]]
apt_info_fa20["due_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_fa20["due_date"]]
apt_info_fa20["late_due"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_fa20["late_due"]]
apt_info_fa20["late_due"] = apt_info_fa20["late_due"].fillna(apt_info_fa20["due_date"])


print(len(apt_info_fa20))

#apt_info.head()


# In[101]:


#student formative APT log import
formative_fa20 = pd.read_csv("cs101fa20-apt-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(formative_fa20))
formative_fa20.head()


# In[102]:


#student summative APT log import
summative_fa20 = pd.read_csv("cs101fa20-aptquiz-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(summative_fa20))
summative_fa20.head()


# In[103]:


#read in apt extra info data and clean
apt = {}
apt_quiz = {}

formative_fa20["timestamp"] = pd.to_datetime(formative_fa20.timestamp,unit='s').dt.tz_localize('utc')

formative_fa20 = formative_fa20[formative_fa20["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)


summative_fa20["timestamp"] = pd.to_datetime(summative_fa20.timestamp,unit='s').dt.tz_localize('utc')

summative_fa20 = summative_fa20[summative_fa20["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)
formative_fa20.head()


# In[104]:


# separate the submissions that were submitted during an apt set's assigned time range vs. extra practice 
extra = {} 
extra_quiz = {} 
for sem in ["fa20"]: 
    if sem not in extra: 
        extra[sem] = pd.DataFrame(columns = formative_fa20.columns)
    if sem not in extra_quiz:  
        extra_quiz[sem] = pd.DataFrame(columns = summative_fa20.columns)
    
    extra[sem] = formative_fa20[~formative_fa20["apt_name"].isin(set(apt_info_fa20[(apt_info_fa20["semester"]== sem) &
                                             (apt_info_fa20["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    
    formative_fa20 = formative_fa20[formative_fa20["apt_name"].isin(set(apt_info_fa20[(apt_info_fa20["semester"]== sem) &
                                             (apt_info_fa20["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)

    extra_quiz[sem] = summative_fa20[~summative_fa20["apt_name"].isin(set(apt_info_fa20[(apt_info_fa20["semester"]== sem) &
                                             (apt_info_fa20["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    summative_fa20 = summative_fa20[summative_fa20["apt_name"].isin(set(apt_info_fa20[(apt_info_fa20["semester"]== sem) &
                                             (apt_info_fa20["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    


# In[105]:


#combine sumamtive and formative dataframes
f=[summative_fa20, formative_fa20]
fa20=pd.concat(f)
print(len(fa20))
fa20.head()


# In[106]:


#df = pd.merge(apt_info, sp21, how = "left", on = "apt_name")
df_fa20 = fa20.merge(apt_info_fa20[(apt_info_fa20["semester"]== 'fa20') &
                                             (apt_info_fa20["type"].isin(["formative",
                                              "summative_practice", "summative"]))].copy(deep = True).reset_index(drop = True),
                                              how = "left", on = "apt_name")
print(len(df_fa20))
df_fa20.head()


# In[107]:


grouped_fa20=df_fa20.groupby(['anonid', 'apt_name', 'apt_set'])['score'].max()
grouped_fa20.head()
display(grouped_fa20)


# In[108]:


#find max score per submission per student
new_df_fa20=df_fa20.groupby( [ "anonid", "apt_name", "apt_set"])['score'].max().to_frame(name = 'max_score').reset_index()
new_df_fa20.head()


# In[109]:


#clean column entry
new_df_fa20.replace('wrongclass', 0.0)
new_df_fa20.replace('nocompile', 0.0)
new_df_fa20['max_score'] = pd.to_numeric(new_df_fa20['max_score'], errors='coerce')


# In[110]:


#check column types
new_df_fa20.dtypes


# In[111]:


#add struggling column, where max apt score is less than 100%
new_df_fa20['struggling'] = new_df_fa20['max_score']<1.00000
print(len(new_df_fa20))
new_df_fa20.head()


# In[112]:


#sort for only struggling students
struggling_students_fa20 = new_df_fa20[new_df_fa20['struggling'] == True] 
print(len(struggling_students_fa20))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_students_fa20)


# In[113]:


#count number of struggling students
new_df_fa20.groupby(['struggling']).count()


# In[114]:


struggling_students_fa20.groupby(['apt_set']).count()


# In[115]:


#number of struggles per student
struggling_count_fa20=struggling_students_fa20.groupby(['anonid']).count()
struggling_count_fa20.sort_values(by='apt_name', ascending=False)
print(len(struggling_count_fa20))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_count_fa20)


# In[116]:


#view number of struggles per student
sns.histplot(data = struggling_count_fa20, x = "apt_name")


# In[117]:


only_fail_fa20=df_fa20

only_fail_fa20=df_fa20
only_fail_fa20.replace('wrongclass', 0.0)
only_fail_fa20.replace('nocompile', 0.0)
only_fail_fa20['score'] = pd.to_numeric(only_fail_fa20['score'], errors='coerce')

only_fail_fa20 = only_fail_fa20[only_fail_fa20['score'] < 1.000]




#only_fail = only_fail[only_fail['score'] == True] 
only_fail_fa20.head()


# In[118]:


only_fail_fa20.dtypes


# In[119]:


redefine_fa20=df_fa20.groupby( [ "anonid", "apt_name", "apt_set"]).count()
redefine_fa20 = redefine_fa20[redefine_fa20.columns[~redefine_fa20.columns.isin(['score', 'semester', 'concept', 'type', 'mapping', 'assign_date', 'due_date', 'late_due', 'required', 'notes', 'other'])]]
redefine_fa20 = redefine_fa20.rename(columns={'timestamp': 'num_submissions'})
redefine_fa20['struggling']=redefine_fa20['num_submissions']>=3
redefine_fa20.head()


# In[120]:


redefine_fa20=redefine_fa20.sort_values(by=['num_submissions'])
sns.histplot(data = redefine_fa20, x = "anonid")
median_submissions_fa20=redefine_fa20["num_submissions"].median()
max_submissions_fa20=redefine_fa20['num_submissions'].max()
mean_submissions_fa20=redefine_fa20['num_submissions'].mean()
print(median_submissions_fa20)
print(max_submissions_fa20)
print(mean_submissions_fa20)


# In[121]:


struggles_fa20 = redefine_fa20[redefine_fa20['struggling'] == True] 
print(len(struggles_fa20))
struggles_fa20.head()


# In[122]:


#number total struggles per set
struggles_fa20.groupby(['apt_set']).count()


# In[123]:


#number unique struggling students
struggles_fa20.groupby(['anonid']).count()


# In[124]:


by_apt_set_fa20=struggles_fa20.groupby( [ "anonid", "apt_set"]).count()
by_apt_set_fa20 = by_apt_set_fa20[by_apt_set_fa20.columns[~by_apt_set_fa20.columns.isin(['struggling'])]]
by_apt_set_fa20 = by_apt_set_fa20.rename(columns={'num_submissions': 'num_struggles'})
by_apt_set_fa20.head()


# In[125]:


num_students_fa20=struggles_fa20.groupby('anonid').count()
num_students_fa20 = num_students_fa20[num_students_fa20.columns[~num_students_fa20.columns.isin(['struggling'])]]
num_students_fa20 = num_students_fa20.rename(columns={'num_submissions': 'num_struggles'})
num_students_fa20 = num_students_fa20.reset_index()
print(len(num_students_fa20))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(num_students_fa20)


# In[126]:


#total_struggling=pd.merge(struggling_students, num_students, on="anonid")
struggling_count_fa20 = struggling_count_fa20.reset_index()
struggling_count_anon_fa20=struggling_count_fa20.iloc[: , :1]
num_students_anon_fa20=num_students_fa20.iloc[: , :1]

#struggling_count_anon.head()
#num_students_anon.head()

total_struggling_fa20 = pd.concat([struggling_count_anon_fa20, num_students_anon_fa20], ignore_index=True)

total_strugglers_fa20=total_struggling_fa20.drop_duplicates()


#total_struggling=pd.merge(struggling_count, num_students, on="anonid")


# In[127]:


print(len(total_struggling_fa20))
print(len(total_strugglers_fa20))


# ## Fa20 Office Hours

# In[128]:


#import dataset
oh_fa20=pd.read_csv('cs101fa20-no-teacher-data-processed.csv')
print(len(oh_fa20))
oh_fa20.head()


# In[129]:


display(oh_fa20.iloc[1])


# In[130]:


office_hours_fa20=oh_fa20.rename(columns=oh_fa20.iloc[1]).drop([0, 1])


# In[131]:


office_hours_fa20.head()


# In[132]:


office_hours_fa20.dtypes


# In[133]:


office_hours_fa20['apt_question'] = pd.np.where(office_hours_fa20[['APT 1', 'APT 2', 'APT 3', 'APT 4', 'APT 5', 'APT 6', 'APT7', 'APT8', 'OTHER', 'Understanding a past assignment/APT']].eq('True').any(1, skipna=True), True, 
             pd.np.where(office_hours_fa20[['APT 1', 'APT 2', 'APT 3', 'APT 4', 'APT 5', 'APT 6', 'APT7', 'APT8', 'OTHER', 'Understanding a past assignment/APT']].eq('False').all(1), None, False))

office_hours_fa20.head()
                                           
                                           


# In[134]:


office_hour_fa20 = office_hours_fa20[office_hours_fa20['apt_question'] == True] 
office_hour_fa20.head()


# In[135]:


apt_oh_fa20 = office_hour_fa20[['anonStudent', 'requestedAt', 'startedAt','completedAt','APT 1', 'APT 2', 'APT 3', 'APT 4', 'APT 5', 'APT 6', 'APT7', 'APT8', 'OTHER', 'Understanding a past assignment/APT', 'I will need more help', 'I did not make progress']]
print(len(apt_oh_fa20))
apt_oh_fa20.head()


# In[136]:


apt_oh_fa20.loc[apt_oh_fa20.anonStudent == 'a2bfbec72dadbbeb09898f70adc6f50ec8c49060', 'set'] = 'x'

for ind in apt_oh_fa20.index:
    if apt_oh_fa20['APT 1'][ind]=="True":
        apt_oh_fa20['set'][ind]="1"
    if apt_oh_fa20['APT 2'][ind]=="True":
        apt_oh_fa20['set'][ind]="2"
    if apt_oh_fa20['APT 3'][ind]=="True":
        apt_oh_fa20['set'][ind]="3"
    if apt_oh_fa20['APT 4'][ind]=="True":
        apt_oh_fa20['set'][ind]="4"
    if apt_oh_fa20['APT 5'][ind]=="True":
        apt_oh_fa20['set'][ind]="5"
    if apt_oh_fa20['APT 6'][ind]=="True":
        apt_oh_fa20['set'][ind]="6"
    if apt_oh_fa20['APT7'][ind]=="True":
        apt_oh_fa20['set'][ind]="7"
    if apt_oh_fa20['APT8'][ind]=="True":
        apt_oh_fa20['set'][ind]="8"
    else:
        apt_oh_fa20['set'][ind]="0"
  
apt_oh_fa20 = apt_oh_fa20.rename(columns={'set': 'apt_set'})    
apt_oh_fa20.head()


# In[137]:


num_oh_students_fa20 = apt_oh_fa20.groupby(['anonStudent']).count()
num_oh_students_fa20 = num_oh_students_fa20.sort_values(by='requestedAt', ascending=False)
med_visits_fa20=num_oh_students_fa20["requestedAt"].median()
mean_visits_fa20=num_oh_students_fa20["requestedAt"].mean()
num_oh_students_fa20 = num_oh_students_fa20['requestedAt']
print(len(num_oh_students_fa20))
print(mean_visits_fa20)
num_oh_students_fa20


# In[138]:


sns.histplot(data = num_oh_students_fa20)


# In[139]:


apt1_fa20 = apt_oh_fa20.groupby(['APT 1']).count()
apt2_fa20 = apt_oh_fa20.groupby(['APT 2']).count()
apt3_fa20 = apt_oh_fa20.groupby(['APT 3']).count()
apt4_fa20 = apt_oh_fa20.groupby(['APT 4']).count()
apt5_fa20 = apt_oh_fa20.groupby(['APT 5']).count()
apt6_fa20 = apt_oh_fa20.groupby(['APT 6']).count()
apt7_fa20 = apt_oh_fa20.groupby(['APT7']).count()
apt8_fa20 = apt_oh_fa20.groupby(['APT8']).count()

print('APT 1 has '+ apt1_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 2 has '+ apt2_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 3 has '+ apt3_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 4 has '+ apt4_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 5 has '+ apt5_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 6 has '+ apt6_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 7 has '+ apt7_fa20.iloc[1][True].astype(str)+ ' students')
print('APT 8 has '+ apt8_fa20.iloc[1][True].astype(str)+ ' students')


# In[140]:


oh_students_fa20 = pd.DataFrame()
oh_students_fa20['oh_students']=apt_oh_fa20['anonStudent']
apt_students_fa20 = pd.DataFrame()
apt_students_fa20['apt_students']=struggling_students_fa20['anonid']
apt_students_fa20.head()
print(len(apt_students_fa20))


# ## Fa20 Combining OH and APT

# In[141]:


nos_fa20=num_oh_students_fa20.to_frame(name = 'count').reset_index()
ns_fa20=num_students_fa20.rename(columns = {"anonid":"anonStudent"})
ns_fa20.head()

frames_fa20 = [nos_fa20, ns_fa20]

result3_fa20 = pd.concat(frames_fa20).reset_index()
result3_fa20.head()
print(len(result3_fa20))
print('36 total OH Students, 150 struggling students, 186 combined')
print(len(result3_fa20['anonStudent'])-len(result3_fa20['anonStudent'].drop_duplicates()))
#result3.dtypes


# In[142]:


overlap_fa20=0
for student in ns_fa20['anonStudent']:
    for s in nos_fa20['anonStudent']:
        if student==s:
            overlap_fa20+=1
print(overlap_fa20)
print('of struggling students visited OH')
print(' ')
print('Every student who visited office hours for an APT was struggling. Of the struggling students, ~33% of them visited Office Hours.')
print(' ')
print('This shows that number of APT submissions is a good indicator of OH attendance for students')


# In[143]:


df_fa20 = df_fa20.assign(result=df_fa20['anonid'].isin(num_students_fa20['anonid']).astype(bool))
df_fa20.head()


# In[144]:


df_fa20.groupby(['result']).count()


# In[145]:


anonids_fa20=df_fa20.groupby(['anonid']).count()
print(len(anonids_fa20))


# In[146]:


apt_oh_fa20=apt_oh_fa20.rename(columns={'anonStudent': 'anonid'})
apt_oh_fa20.dtypes


# In[147]:


mergedf_fa20=pd.merge(df_fa20, apt_oh_fa20, on=['anonid'])
print(len(mergedf_fa20))
mergedf_fa20.head()


# In[148]:


mergedf_fa20=mergedf_fa20.loc[mergedf_fa20['score'] == 1]
print(len(mergedf_fa20))
mergedf_fa20.head()


# In[149]:


mergedf_fa20['startedAt'] = pd.to_datetime(mergedf_fa20.startedAt).dt.tz_convert('utc')


# In[150]:


mergedf_fa20['requestedAt'] = pd.to_datetime(mergedf_fa20.requestedAt).dt.tz_convert('utc')


# In[151]:


mergedf_fa20['completedAt'] = pd.to_datetime(mergedf_fa20.completedAt).dt.tz_convert('utc')


# In[152]:


mergedf_fa20.dtypes


# In[153]:


duringoh_fa20=mergedf_fa20[(mergedf_fa20['timestamp'] >= mergedf_fa20['startedAt'])& (mergedf_fa20['timestamp'] <= mergedf_fa20['completedAt'])]
print(len(duringoh_fa20))


# In[154]:


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(duringoh_fa20)


# In[155]:


duringoh_fa20.groupby(['anonid']).count().sort_values(by='apt_name', ascending=False)


# In[156]:


strugglemerge_fa20=pd.merge(struggles_fa20, df_fa20, on=['anonid', 'apt_name'])
strugglemerge_fa20.head()


# In[157]:


struggleoh_fa20=pd.merge(strugglemerge_fa20, apt_oh_fa20, on=['anonid'])
struggleoh_fa20.head()


# In[158]:


struggleoh_fa20['startedAt'] = pd.to_datetime(struggleoh_fa20.startedAt).dt.tz_convert('utc')
struggleoh_fa20['requestedAt'] = pd.to_datetime(struggleoh_fa20.requestedAt).dt.tz_convert('utc')
struggleoh_fa20['completedAt'] = pd.to_datetime(struggleoh_fa20.completedAt).dt.tz_convert('utc')


# In[159]:


struggleduringoh_fa20=struggleoh_fa20[(struggleoh_fa20['timestamp'] >= struggleoh_fa20['startedAt'])& (struggleoh_fa20['timestamp'] <= struggleoh_fa20['completedAt'])]
print(len(struggleduringoh_fa20))


# In[160]:


#median score of submissions in total
struggleoh_fa20['score'].median()


# In[161]:


#median score of submissions that occur during OH
struggleduringoh_fa20['score'].median()


# In[162]:


#mean score of submissions that occur during OH
struggleduringoh_fa20['score'].mean()


# In[163]:


#median number of submissions of someone who goes to office hours and submits an APT during the OH time frame
struggleduringoh_fa20['num_submissions'].median()


# In[164]:


#median number of submissions for someone that goes to office hours
struggleoh_fa20['num_submissions'].median()


# In[165]:


#only include submissions with a perfect score
strugglepass_fa20=struggleduringoh_fa20.loc[struggleduringoh_fa20['score'] == 1]
print(len(strugglepass_fa20))


# In[166]:


#all rows for APT submissions of 1 that occurre during an OH session
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(strugglepass_fa20)


# In[167]:


#number of pass submissions during OH per student
strugglepass_fa20.groupby(['anonid']).count().sort_values(by='apt_name', ascending=False)


# In[168]:


#number of submissions of individual APTs during OH (median=1)
strugglepass_fa20.groupby(['anonid', 'apt_name']).count()


# In[169]:


#number successful APT submissions during OH per APT
strugglepass_fa20.groupby(['apt_name']).count().sort_values(by='anonid', ascending=False)


# In[170]:


#number successful APT submissions during OH per set
strugglepass_fa20.groupby(['apt_set_x']).count().sort_values(by='anonid', ascending=False)


# In[171]:


#total struggles per APT
struggles_fa20.groupby(['apt_name']).count().sort_values(by='struggling', ascending=False)


# In[172]:


#total apt set struggles
struggles_fa20.groupby(['apt_set']).count().sort_values(by='struggling', ascending=False)


# ###### Also, count number of submissions during an OH time that were not of score 1 and were never of score 1. Find max score for each (apt, student) combo during an OH timeslot and filter for those <1.

# In[173]:


nopass_fa20=struggleduringoh_fa20.groupby( [ "anonid", "apt_name", "apt_set_x", "completedAt"])['score'].max().to_frame(name = 'max_score').reset_index()
nopass_fa20.head()
print(len(nopass_fa20))


# In[174]:


nopass_fa20['not_pass'] = nopass_fa20['max_score']<1.00000


# In[175]:


nopass_fa20=nopass_fa20.loc[nopass_fa20['not_pass'] == True]
print(len(nopass_fa20))


# In[176]:


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(nopass_fa20)


# In[177]:


ohfail_fa20=pd.merge(nopass_fa20, df_fa20, on=['anonid', 'apt_name'])
ohfail_fa20.head()
print(len(ohfail_fa20))


# In[178]:


ohfail_fa20=ohfail_fa20[(ohfail_fa20['timestamp'] >= ohfail_fa20['completedAt'])]
print(len(ohfail_fa20))


# In[179]:


ohfail_fa20['difference']=ohfail_fa20['timestamp']-ohfail_fa20['completedAt']
ohfail_fa20.head()


# In[180]:


ohfail_fa20['difference']=ohfail_fa20['difference'].astype('timedelta64[m]').astype(int)

ohfail_fa20.head()


# In[181]:


conditions_fa20 = [
    (ohfail_fa20['difference'] == 0),
    (ohfail_fa20['difference'] > 0) & (ohfail_fa20['difference'] <= 30),
    (ohfail_fa20['difference'] > 30) & (ohfail_fa20['difference'] <= 60),
    (ohfail_fa20['difference'] > 60) & (ohfail_fa20['difference'] <= 90),
    (ohfail_fa20['difference'] > 90) & (ohfail_fa20['difference'] <= 120),
    (ohfail_fa20['difference'] > 120) & (ohfail_fa20['difference'] <= 150),
    (ohfail_fa20['difference'] > 150) & (ohfail_fa20['difference'] <= 180),
    (ohfail_fa20['difference'] > 180) & (ohfail_fa20['difference'] <= 1440),
    (ohfail_fa20['difference'] > 1440)
    ]

# create a list of the values we want to assign for each condition
values_fa20 = ['0', '1-30', '31-60', '61-90', '91-120', '121-150', '151-180', '180-1 day', '>1 day']

# create a new column and use np.select to assign values to it using our lists as arguments
ohfail_fa20['time_since_oh'] = np.select(conditions_fa20, values_fa20)

# display updated DataFrame
ohfail_fa20.head()


# In[182]:


ohfail_fa20.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()


# In[183]:


clean_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '0')]


# In[308]:


sns.boxplot(data=clean_ohfail_fa20, x="time_since_oh", y="score", order=['1-30', '31-60', '61-90', '91-120', '121-150', '151-180', '180-1 day', '>1 day'])


# In[185]:


sns.lineplot(data=clean_ohfail_fa20, x="time_since_oh", y="score")


# In[186]:


sns.lineplot(data=ohfail_fa20, x="difference", y="score")


# In[187]:


graph = sns.FacetGrid(ohfail_fa20, col ="anonid")
# map the above form facetgrid with some attributes
graph.map(plt.scatter, "difference", "score")
# show the object
plt.show()


# In[188]:


adapted1_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '180-1 day') & (ohfail_fa20['time_since_oh'] != '>1 day')]
adapted2_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '180-1 day')]
adapted3_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '180-1 day') & (ohfail_fa20['time_since_oh'] != '>1 day') & (ohfail_fa20['time_since_oh'] != '151-180') & (ohfail_fa20['time_since_oh'] != '121-150') & (ohfail_fa20['time_since_oh'] != '91-120')]
adapted4_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '180-1 day') & (ohfail_fa20['time_since_oh'] != '>1 day') & (ohfail_fa20['time_since_oh'] != '151-180') & (ohfail_fa20['time_since_oh'] != '121-150') & (ohfail_fa20['time_since_oh'] != '91-120') & (ohfail_fa20['time_since_oh'] != '61-90')]
adapted5_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '180-1 day') & (ohfail_fa20['time_since_oh'] != '>1 day') & (ohfail_fa20['time_since_oh'] != '151-180') & (ohfail_fa20['time_since_oh'] != '121-150') & (ohfail_fa20['time_since_oh'] != '91-120') & (ohfail_fa20['time_since_oh'] != '61-90') & (ohfail_fa20['time_since_oh'] != '31-60')]
adapted6_ohfail_fa20=ohfail_fa20[(ohfail_fa20['time_since_oh'] != '180-1 day') & (ohfail_fa20['time_since_oh'] != '>1 day') & (ohfail_fa20['time_since_oh'] != '151-180') & (ohfail_fa20['time_since_oh'] != '121-150') & (ohfail_fa20['time_since_oh'] != '91-120') & (ohfail_fa20['time_since_oh'] != '61-90') & (ohfail_fa20['time_since_oh'] != '31-60') & (ohfail_fa20['time_since_oh'] != '1-30')]


# In[189]:


adapted1_ohfail_fa20.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 180 mins after OH


# In[190]:


adapted2_ohfail_fa20.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 1 day after OH


# In[191]:


adapted3_ohfail_fa20.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 90 minutes from OH


# In[192]:


adapted4_ohfail_fa20.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 60 minutes from OH


# In[193]:


adapted5_ohfail_fa20.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 30 minutes from OH


# # Spring 2022

# In[194]:


#APT Additional Info import
apt_info_sp22 = pd.read_excel("CS APT Problem.xlsx")
print(len(apt_info_sp22))


apt_info_sp22 = apt_info_sp22[apt_info_sp22.index < apt_info_sp22[apt_info_sp22["apt_set"] == "CS201"].index[0]] # omit all info on CS201
apt_info_sp22 = apt_info_sp22[apt_info_sp22["semester"]== "sp22"] # only get Spring 2022 semester

#cleaning time zones
apt_info_sp22["assign_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_sp22["assign_date"]]
apt_info_sp22["due_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_sp22["due_date"]]
apt_info_sp22["late_due"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_sp22["late_due"]]
apt_info_sp22["late_due"] = apt_info_sp22["late_due"].fillna(apt_info_sp22["due_date"])


print(len(apt_info_sp22))

#apt_info.head()


# In[195]:


#student formative APT log import
formative_sp22 = pd.read_csv("cs101sp22-apt-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(formative_sp22))
formative_sp22.head()


# In[196]:


#student summative APT log import
summative_sp22 = pd.read_csv("cs101sp22-aptquiz-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(summative_sp22))
summative_sp22.head()


# In[197]:


#read in apt extra info data and clean
apt = {}
apt_quiz = {}

formative_sp22["timestamp"] = pd.to_datetime(formative_sp22.timestamp,unit='s').dt.tz_localize('utc')

formative_sp22 = formative_sp22[formative_sp22["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)


summative_sp22["timestamp"] = pd.to_datetime(summative_sp22.timestamp,unit='s').dt.tz_localize('utc')

summative_sp22 = summative_sp22[summative_sp22["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)
formative_sp22.head()


# In[198]:


# separate the submissions that were submitted during an apt set's assigned time range vs. extra practice 
extra = {} 
extra_quiz = {} 
for sem in ["sp22"]: 
    if sem not in extra: 
        extra[sem] = pd.DataFrame(columns = formative_sp22.columns)
    if sem not in extra_quiz:  
        extra_quiz[sem] = pd.DataFrame(columns = summative_sp22.columns)
    
    extra[sem] = formative_sp22[~formative_sp22["apt_name"].isin(set(apt_info_sp22[(apt_info_sp22["semester"]== sem) &
                                             (apt_info_sp22["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    
    formative_sp22 = formative_sp22[formative_sp22["apt_name"].isin(set(apt_info_sp22[(apt_info_sp22["semester"]== sem) &
                                             (apt_info_sp22["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)

    extra_quiz[sem] = summative_sp22[~summative_sp22["apt_name"].isin(set(apt_info_sp22[(apt_info_sp22["semester"]== sem) &
                                             (apt_info_sp22["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    summative_sp22 = summative_sp22[summative_sp22["apt_name"].isin(set(apt_info_sp22[(apt_info_sp22["semester"]== sem) &
                                             (apt_info_sp22["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    


# In[199]:


#combine sumamtive and formative dataframes
fr=[summative_sp22, formative_sp22]
sp22=pd.concat(fr)
print(len(sp22))
sp22.head()


# In[200]:


#df = pd.merge(apt_info, sp21, how = "left", on = "apt_name")
df_sp22 = sp22.merge(apt_info_sp22[(apt_info_sp22["semester"]== 'sp22') &
                                             (apt_info_sp22["type"].isin(["formative",
                                              "summative_practice", "summative"]))].copy(deep = True).reset_index(drop = True),
                                              how = "left", on = "apt_name")
print(len(df_sp22))
df_sp22.head()


# In[201]:


grouped_sp22=df_sp22.groupby(['anonid', 'apt_name', 'apt_set'])['score'].max()
grouped_sp22.head()
display(grouped_sp22)


# In[202]:


#find max score per submission per student
new_df_sp22=df_sp22.groupby( [ "anonid", "apt_name", "apt_set"])['score'].max().to_frame(name = 'max_score').reset_index()
new_df_sp22.head()


# In[203]:


#clean column entry
new_df_sp22.replace('wrongclass', 0.0)
new_df_sp22.replace('nocompile', 0.0)
new_df_sp22['max_score'] = pd.to_numeric(new_df_sp22['max_score'], errors='coerce')


# In[204]:


#check column types
new_df_sp22.dtypes


# In[205]:


#add struggling column, where max apt score is less than 100%
new_df_sp22['struggling'] = new_df_sp22['max_score']<1.00000
print(len(new_df_sp22))
new_df_sp22.head()


# In[206]:


#sort for only struggling students
struggling_students_sp22 = new_df_sp22[new_df_sp22['struggling'] == True] 
print(len(struggling_students_sp22))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_students_sp22)


# In[207]:


#count number of struggling students
new_df_sp22.groupby(['struggling']).count()


# In[208]:


struggling_students_sp22.groupby(['apt_set']).count()


# In[209]:


#number of struggles per student
struggling_count_sp22=struggling_students_sp22.groupby(['anonid']).count()
struggling_count_sp22.sort_values(by='apt_name', ascending=False)
print(len(struggling_count_sp22))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_count_sp22)


# In[210]:


#view number of struggles per student
sns.histplot(data = struggling_count_sp22, x = "apt_name")


# In[211]:


only_fail_sp22=df_sp22

only_fail_sp22=df_sp22
only_fail_sp22.replace('wrongclass', 0.0)
only_fail_sp22.replace('nocompile', 0.0)
only_fail_sp22['score'] = pd.to_numeric(only_fail_sp22['score'], errors='coerce')

only_fail_sp22 = only_fail_sp22[only_fail_sp22['score'] < 1.000]




#only_fail = only_fail[only_fail['score'] == True] 
only_fail_sp22.head()


# In[212]:


only_fail_sp22.dtypes


# In[213]:


redefine_sp22=df_sp22.groupby( [ "anonid", "apt_name", "apt_set"]).count()
redefine_sp22 = redefine_sp22[redefine_sp22.columns[~redefine_sp22.columns.isin(['score', 'semester', 'concept', 'type', 'mapping', 'assign_date', 'due_date', 'late_due', 'required', 'notes', 'other'])]]
redefine_sp22 = redefine_sp22.rename(columns={'timestamp': 'num_submissions'})
redefine_sp22['struggling']=redefine_sp22['num_submissions']>=3
redefine_sp22.head()


# In[214]:


redefine_sp22=redefine_sp22.sort_values(by=['num_submissions'])
sns.histplot(data = redefine_sp22, x = "anonid")
median_submissions_sp22=redefine_sp22["num_submissions"].median()
max_submissions_sp22=redefine_sp22['num_submissions'].max()
mean_submissions_sp22=redefine_sp22['num_submissions'].mean()
print(median_submissions_sp22)
print(max_submissions_sp22)
print(mean_submissions_sp22)


# In[215]:


struggles_sp22 = redefine_sp22[redefine_sp22['struggling'] == True] 
print(len(struggles_sp22))
struggles_sp22.head()


# In[216]:


#number total struggles per set
struggles_sp22.groupby(['apt_set']).count()


# In[217]:


#number unique struggling students
struggles_sp22.groupby(['anonid']).count()


# In[218]:


by_apt_set_sp22=struggles_sp22.groupby( [ "anonid", "apt_set"]).count()
by_apt_set_sp22 = by_apt_set_sp22[by_apt_set_sp22.columns[~by_apt_set_sp22.columns.isin(['struggling'])]]
by_apt_set_sp22 = by_apt_set_sp22.rename(columns={'num_submissions': 'num_struggles'})
by_apt_set_sp22.head()


# In[219]:


num_students_sp22=struggles_sp22.groupby('anonid').count()
num_students_sp22 = num_students_sp22[num_students_sp22.columns[~num_students_sp22.columns.isin(['struggling'])]]
num_students_sp22 = num_students_sp22.rename(columns={'num_submissions': 'num_struggles'})
num_students_sp22 = num_students_sp22.reset_index()
print(len(num_students_sp22))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(num_students_sp22)


# In[220]:


#total_struggling=pd.merge(struggling_students, num_students, on="anonid")
struggling_count_sp22 = struggling_count_sp22.reset_index()
struggling_count_anon_sp22=struggling_count_sp22.iloc[: , :1]
num_students_anon_sp22=num_students_sp22.iloc[: , :1]

#struggling_count_anon.head()
#num_students_anon.head()

total_struggling_sp22 = pd.concat([struggling_count_anon_sp22, num_students_anon_sp22], ignore_index=True)

total_strugglers_sp22=total_struggling_sp22.drop_duplicates()


#total_struggling=pd.merge(struggling_count, num_students, on="anonid")


# In[221]:


print(len(total_struggling_sp22))
print(len(total_strugglers_sp22))


# ## Sp22 Office Hours

# In[222]:


#import dataset
oh_sp22=pd.read_csv('cs101sp22-no-teacher-data-processed.csv')
print(len(oh_sp22))
oh_sp22.head()


# In[223]:


display(oh_sp22.iloc[1])


# In[224]:


office_hours_sp22=oh_sp22.rename(columns=oh_sp22.iloc[1]).drop([0, 1])


# In[225]:


office_hours_sp22.head()


# In[226]:


office_hours_sp22.dtypes


# In[227]:


office_hours_sp22['apt_question'] = pd.np.where(office_hours_sp22[['APT 1', 'APT 2', 'APT 3', 'APT 4', 'APT 5', 'APT 6', 'APT 7', 'APT 8', 'Understanding a past assignment/APT']].eq('True').any(1, skipna=True), True, 
             pd.np.where(office_hours_sp22[['APT 1', 'APT 2', 'APT 3', 'APT 4', 'APT 5', 'APT 6', 'APT 7', 'APT 8', 'Understanding a past assignment/APT']].eq('False').all(1), None, False))

office_hours_sp22.head()
                                           
                                           


# In[228]:


office_hour_sp22 = office_hours_sp22[office_hours_sp22['apt_question'] == True] 
office_hour_sp22.head()


# In[229]:


apt_oh_sp22 = office_hour_sp22[['anonStudent', 'requestedAt', 'startedAt','completedAt','APT 1', 'APT 2', 'APT 3', 'APT 4', 'APT 5', 'APT 6', 'APT 7', 'APT 8', 'Understanding a past assignment/APT', 'I will need more help']]
print(len(apt_oh_sp22))
apt_oh_sp22.head()


# In[230]:


apt_oh_sp22.loc[apt_oh_sp22.anonStudent == '898bded048b6076fa9f7800267f553b9c1fe7e39', 'set'] = 'x'

for ind in apt_oh_sp22.index:
    if apt_oh_sp22['APT 1'][ind]=="True":
        apt_oh_sp22['set'][ind]="1"
    if apt_oh_sp22['APT 2'][ind]=="True":
        apt_oh_sp22['set'][ind]="2"
    if apt_oh_sp22['APT 3'][ind]=="True":
        apt_oh_sp22['set'][ind]="3"
    if apt_oh_sp22['APT 4'][ind]=="True":
        apt_oh_sp22['set'][ind]="4"
    if apt_oh_sp22['APT 5'][ind]=="True":
        apt_oh_sp22['set'][ind]="5"
    if apt_oh_sp22['APT 6'][ind]=="True":
        apt_oh_sp22['set'][ind]="6"
    if apt_oh_sp22['APT 7'][ind]=="True":
        apt_oh_sp22['set'][ind]="7"
    if apt_oh_sp22['APT 8'][ind]=="True":
        apt_oh_sp22['set'][ind]="8"
    else:
        apt_oh_sp22['set'][ind]="0"
  
apt_oh_sp22 = apt_oh_sp22.rename(columns={'set': 'apt_set'})    
apt_oh_sp22.head()


# In[231]:


num_oh_students_sp22 = apt_oh_sp22.groupby(['anonStudent']).count()
num_oh_students_sp22 = num_oh_students_sp22.sort_values(by='requestedAt', ascending=False)
med_visits_sp22=num_oh_students_sp22["requestedAt"].median()
mean_visits_sp22=num_oh_students_sp22["requestedAt"].mean()
num_oh_students_sp22 = num_oh_students_sp22['requestedAt']
print(len(num_oh_students_sp22))
print(med_visits_sp22)
print(mean_visits_sp22)
num_oh_students_sp22


# In[232]:


sns.histplot(data = num_oh_students_sp22)


# In[233]:


apt1_sp22 = apt_oh_sp22.groupby(['APT 1']).count()
apt2_sp22 = apt_oh_sp22.groupby(['APT 2']).count()
apt3_sp22 = apt_oh_sp22.groupby(['APT 3']).count()
apt4_sp22 = apt_oh_sp22.groupby(['APT 4']).count()
apt5_sp22 = apt_oh_sp22.groupby(['APT 5']).count()
apt6_sp22 = apt_oh_sp22.groupby(['APT 6']).count()
apt7_sp22 = apt_oh_sp22.groupby(['APT 7']).count()
apt8_sp22 = apt_oh_sp22.groupby(['APT 8']).count()

print('APT 1 has '+ apt1_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 2 has '+ apt2_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 3 has '+ apt3_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 4 has '+ apt4_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 5 has '+ apt5_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 6 has '+ apt6_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 7 has '+ apt7_sp22.iloc[1][True].astype(str)+ ' students')
print('APT 8 has '+ apt8_sp22.iloc[1][True].astype(str)+ ' students')


# In[234]:


oh_students_sp22 = pd.DataFrame()
oh_students_sp22['oh_students']=apt_oh_sp22['anonStudent']
apt_students_sp22 = pd.DataFrame()
apt_students_sp22['apt_students']=struggling_students_sp22['anonid']
apt_students_sp22.head()
print(len(apt_students_sp22))


# ## Sp20 Combining OH and APT

# In[235]:


nos_sp22=num_oh_students_sp22.to_frame(name = 'count').reset_index()
ns_sp22=num_students_sp22.rename(columns = {"anonid":"anonStudent"})
ns_sp22.head()

frames_sp22 = [nos_sp22, ns_sp22]

result3_sp22 = pd.concat(frames_sp22).reset_index()
result3_sp22.head()
print(len(result3_sp22))
print('41 total OH Students, 152 struggling students, 193 combined')
print(len(result3_sp22['anonStudent'])-len(result3_sp22['anonStudent'].drop_duplicates()))
#result3.dtypes


# In[236]:


overlap_sp22=0
for student in ns_sp22['anonStudent']:
    for s in nos_sp22['anonStudent']:
        if student==s:
            overlap_sp22+=1
print(overlap_sp22)
print('of struggling students visited OH')
print(' ')
print('Every student who visited office hours for an APT was struggling. Of the struggling students, ~33% of them visited Office Hours.')
print(' ')
print('This shows that number of APT submissions is a good indicator of OH attendance for students')


# In[237]:


df_sp22 = df_sp22.assign(result=df_sp22['anonid'].isin(num_students_sp22['anonid']).astype(bool))
df_sp22.head()


# In[238]:


df_sp22.groupby(['result']).count()


# In[239]:


anonids_sp22=df_sp22.groupby(['anonid']).count()
print(len(anonids_sp22))


# In[240]:


apt_oh_sp22=apt_oh_sp22.rename(columns={'anonStudent': 'anonid'})
apt_oh_sp22.dtypes


# In[241]:


mergedf_sp22=pd.merge(df_sp22, apt_oh_sp22, on=['anonid'])
print(len(mergedf_sp22))
mergedf_sp22.head()


# In[242]:


mergedf_sp22=mergedf_sp22.loc[mergedf_sp22['score'] == 1]
print(len(mergedf_sp22))
mergedf_sp22.head()


# In[243]:


mergedf_sp22['startedAt'] = pd.to_datetime(mergedf_sp22.startedAt).dt.tz_convert('utc')


# In[244]:


mergedf_sp22['requestedAt'] = pd.to_datetime(mergedf_sp22.requestedAt).dt.tz_convert('utc')


# In[245]:


mergedf_sp22['completedAt'] = pd.to_datetime(mergedf_sp22.completedAt).dt.tz_convert('utc')


# In[246]:


mergedf_sp22.dtypes


# In[247]:


duringoh_sp22=mergedf_sp22[(mergedf_sp22['timestamp'] >= mergedf_sp22['startedAt'])& (mergedf_sp22['timestamp'] <= mergedf_sp22['completedAt'])]
print(len(duringoh_sp22))


# In[248]:


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(duringoh_sp22)


# In[249]:


duringoh_sp22.groupby(['anonid']).count().sort_values(by='apt_name', ascending=False)


# In[250]:


strugglemerge_sp22=pd.merge(struggles_sp22, df_sp22, on=['anonid', 'apt_name'])
strugglemerge_sp22.head()


# In[251]:


struggleoh_sp22=pd.merge(strugglemerge_sp22, apt_oh_sp22, on=['anonid'])
struggleoh_sp22.head()


# In[252]:


struggleoh_sp22['startedAt'] = pd.to_datetime(struggleoh_sp22.startedAt).dt.tz_convert('utc')
struggleoh_sp22['requestedAt'] = pd.to_datetime(struggleoh_sp22.requestedAt).dt.tz_convert('utc')
struggleoh_sp22['completedAt'] = pd.to_datetime(struggleoh_sp22.completedAt).dt.tz_convert('utc')


# In[253]:


struggleduringoh_sp22=struggleoh_sp22[(struggleoh_sp22['timestamp'] >= struggleoh_sp22['startedAt'])& (struggleoh_sp22['timestamp'] <= struggleoh_sp22['completedAt'])]
print(len(struggleduringoh_sp22))


# In[254]:


#median score of submissions in total
struggleoh_sp22['score'].median()


# In[255]:


#median score of submissions that occur during OH
struggleduringoh_sp22['score'].median()


# In[256]:


#mean score of submissions that occur during OH
struggleduringoh_sp22['score'].mean()


# In[257]:


#median number of submissions of someone who goes to office hours and submits an APT during the OH time frame
struggleduringoh_sp22['num_submissions'].median()


# In[258]:


#median number of submissions for someone that goes to office hours
struggleoh_sp22['num_submissions'].median()


# In[259]:


#only include submissions with a perfect score
strugglepass_sp22=struggleduringoh_sp22.loc[struggleduringoh_sp22['score'] == 1]
print(len(strugglepass_sp22))


# In[260]:


#all rows for APT submissions of 1 that occurre during an OH session
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(strugglepass_sp22)


# In[261]:


#number of pass submissions during OH per student
strugglepass_sp22.groupby(['anonid']).count().sort_values(by='apt_name', ascending=False)


# In[262]:


#number of submissions of individual APTs during OH (median=1)
strugglepass_sp22.groupby(['anonid', 'apt_name']).count()


# In[263]:


#number successful APT submissions during OH per APT
strugglepass_sp22.groupby(['apt_name']).count().sort_values(by='anonid', ascending=False)


# In[264]:


#number successful APT submissions during OH per set
strugglepass_sp22.groupby(['apt_set_x']).count().sort_values(by='anonid', ascending=False)


# In[265]:


#total struggles per APT
struggles_sp22.groupby(['apt_name']).count().sort_values(by='struggling', ascending=False)


# In[266]:


#total apt set struggles
struggles_sp22.groupby(['apt_set']).count().sort_values(by='struggling', ascending=False)


# In[267]:


nopass_sp22=struggleduringoh_sp22.groupby( [ "anonid", "apt_name", "apt_set_x", "completedAt"])['score'].max().to_frame(name = 'max_score').reset_index()
nopass_sp22.head()
print(len(nopass_sp22))


# In[268]:


nopass_sp22['not_pass'] = nopass_sp22['max_score']<1.00000


# In[269]:


nopass_sp22=nopass_sp22.loc[nopass_sp22['not_pass'] == True]
print(len(nopass_sp22))


# In[270]:


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(nopass_sp22)


# In[271]:


ohfail_sp22=pd.merge(nopass_sp22, df_sp22, on=['anonid', 'apt_name'])
ohfail_sp22.head()
print(len(ohfail_sp22))


# In[272]:


ohfail_sp22['difference']=ohfail_sp22['timestamp']-ohfail_sp22['completedAt']
ohfail_sp22.head()


# In[273]:


ohfail_sp22['difference']=ohfail_sp22['difference'].astype('timedelta64[m]').astype(int)

ohfail_sp22.head()


# In[274]:


conditions_sp22 = [
    (ohfail_sp22['difference'] == 0),
    (ohfail_sp22['difference'] > 0) & (ohfail_sp22['difference'] <= 30),
    (ohfail_sp22['difference'] > 30) & (ohfail_sp22['difference'] <= 60),
    (ohfail_sp22['difference'] > 60) & (ohfail_sp22['difference'] <= 90),
    (ohfail_sp22['difference'] > 90) & (ohfail_sp22['difference'] <= 120),
    (ohfail_sp22['difference'] > 120) & (ohfail_sp22['difference'] <= 150),
    (ohfail_sp22['difference'] > 150) & (ohfail_sp22['difference'] <= 180),
    (ohfail_sp22['difference'] > 180) & (ohfail_sp22['difference'] <= 1440),
    (ohfail_sp22['difference'] > 1440)
    ]

# create a list of the values we want to assign for each condition
values_sp22 = ['0', '1-30', '31-60', '61-90', '91-120', '121-150', '151-180', '180-1 day', '>1 day']

# create a new column and use np.select to assign values to it using our lists as arguments
ohfail_sp22['time_since_oh'] = np.select(conditions_sp22, values_sp22)

# display updated DataFrame
ohfail_sp22.head()


# In[275]:


ohfail_sp22.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()


# In[276]:


clean_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '0')]


# In[303]:


sns.boxplot(data=clean_ohfail_sp22, x="time_since_oh", y="score", order=['1-30', '31-60', '61-90', '91-120', '121-150', '151-180', '180-1 day', '>1 day'])


# In[306]:


sns.lineplot(data=clean_ohfail_sp22, x="time_since_oh", y="score", sort= False)


# In[279]:


sns.lineplot(data=ohfail_sp22, x="difference", y="score")


# In[280]:


graph = sns.FacetGrid(ohfail_sp22, col ="anonid")
# map the above form facetgrid with some attributes
graph.map(plt.scatter, "difference", "score")
# show the object
plt.show()


# In[281]:


adapted1_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '180-1 day') & (ohfail_sp22['time_since_oh'] != '>1 day')]
adapted2_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '180-1 day')]
adapted3_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '180-1 day') & (ohfail_sp22['time_since_oh'] != '>1 day') & (ohfail_sp22['time_since_oh'] != '151-180') & (ohfail_sp22['time_since_oh'] != '121-150') & (ohfail_sp22['time_since_oh'] != '91-120')]
adapted4_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '180-1 day') & (ohfail_sp22['time_since_oh'] != '>1 day') & (ohfail_sp22['time_since_oh'] != '151-180') & (ohfail_sp22['time_since_oh'] != '121-150') & (ohfail_sp22['time_since_oh'] != '91-120') & (ohfail_sp22['time_since_oh'] != '61-90')]
adapted5_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '180-1 day') & (ohfail_sp22['time_since_oh'] != '>1 day') & (ohfail_sp22['time_since_oh'] != '151-180') & (ohfail_sp22['time_since_oh'] != '121-150') & (ohfail_sp22['time_since_oh'] != '91-120') & (ohfail_sp22['time_since_oh'] != '61-90') & (ohfail_sp22['time_since_oh'] != '31-60')]
adapted6_ohfail_sp22=ohfail_sp22[(ohfail_sp22['time_since_oh'] != '180-1 day') & (ohfail_sp22['time_since_oh'] != '>1 day') & (ohfail_sp22['time_since_oh'] != '151-180') & (ohfail_sp22['time_since_oh'] != '121-150') & (ohfail_sp22['time_since_oh'] != '91-120') & (ohfail_sp22['time_since_oh'] != '61-90') & (ohfail_sp22['time_since_oh'] != '31-60') & (ohfail_sp22['time_since_oh'] != '1-30')]


# In[282]:


adapted1_ohfail_sp22.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 180 mins after OH


# In[283]:


adapted2_ohfail_sp22.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 1 day after OH


# In[284]:


adapted3_ohfail_sp22.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 90 minutes from OH


# In[285]:


adapted4_ohfail_sp22.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 60 minutes from OH


# In[286]:


adapted5_ohfail_sp22.groupby( [ "anonid", "apt_name"])['score'].max().to_frame(name = 'maximum_score').reset_index()
#max scores after 30 minutes from OH


# # FALL 2021

# ## Fall 2021 APT Data

# In[311]:


#APT Additional Info import
apt_info_fa21 = pd.read_excel("CS APT Problem.xlsx")
print(len(apt_info))


apt_info_fa21 = apt_info_fa21[apt_info_fa21.index < apt_info_fa21[apt_info_fa21["apt_set"] == "CS201"].index[0]] # omit all info on CS201
apt_info_fa21 = apt_info_fa21[apt_info_fa21["semester"]== "fa21"] # only get Fall 2020 semester

#cleaning time zones
apt_info_fa21["assign_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_fa21["assign_date"]]
apt_info_fa21["due_date"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_fa21["due_date"]]
apt_info_fa21["late_due"] = [d.replace(tzinfo=timezone('US/Eastern')) for d in apt_info_fa21["late_due"]]
apt_info_fa21["late_due"] = apt_info_fa21["late_due"].fillna(apt_info_fa21["due_date"])


print(len(apt_info_fa21))

#apt_info.head()


# In[316]:


#student formative APT log import
formative_fa21 = pd.read_csv("cs101fa21-apt-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(formative_fa21))
formative_fa21.head()


# In[317]:


#student summative APT log import
summative_fa21 = pd.read_csv("cs101fa21-aptquiz-anon.csv").rename(columns = {"apt":"apt_name"})
print(len(summative_fa21))
summative_fa21.head()


# In[318]:


#read in apt extra info data and clean
apt = {}
apt_quiz = {}

formative_fa21["timestamp"] = pd.to_datetime(formative_fa21.timestamp,unit='s').dt.tz_localize('utc')

formative_fa21 = formative_fa21[formative_fa21["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)


summative_fa21["timestamp"] = pd.to_datetime(summative_fa21.timestamp,unit='s').dt.tz_localize('utc')

summative_fa21 = summative_fa21[summative_fa21["apt_name"].notnull()].copy(deep = True).reset_index(drop = True)
formative_fa21.head()


# In[319]:


# separate the submissions that were submitted during an apt set's assigned time range vs. extra practice 
extra = {} 
extra_quiz = {} 
for sem in ["fa21"]: 
    if sem not in extra: 
        extra[sem] = pd.DataFrame(columns = formative_fa21.columns)
    if sem not in extra_quiz:  
        extra_quiz[sem] = pd.DataFrame(columns = summative_fa21.columns)
    
    extra[sem] = formative_fa21[~formative_fa21["apt_name"].isin(set(apt_info_fa21[(apt_info_fa21["semester"]== sem) &
                                             (apt_info_fa21["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    
    formative_fa21 = formative_fa21[formative_fa21["apt_name"].isin(set(apt_info_fa21[(apt_info_fa21["semester"]== sem) &
                                             (apt_info_fa21["type"].isin(["formative",
                                              "summative_practice"]))]["apt_name"]))].copy(deep = True).reset_index(drop = True)

    extra_quiz[sem] = summative_fa21[~summative_fa21["apt_name"].isin(set(apt_info_fa21[(apt_info_fa21["semester"]== sem) &
                                             (apt_info_fa21["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    summative_fa21 = summative_fa21[summative_fa21["apt_name"].isin(set(apt_info_fa21[(apt_info_fa21["semester"]== sem) &
                                             (apt_info_fa21["type"] == "summative")]["apt_name"]))].copy(deep = True).reset_index(drop = True)
    


# In[320]:


#combine sumamtive and formative dataframes
f1=[summative_fa21, formative_fa21]
fa21=pd.concat(f1)
print(len(fa21))
fa21.head()


# In[321]:


#df = pd.merge(apt_info, sp21, how = "left", on = "apt_name")
df_fa21 = fa21.merge(apt_info_fa21[(apt_info_fa21["semester"]== 'fa21') &
                                             (apt_info_fa21["type"].isin(["formative",
                                              "summative_practice", "summative"]))].copy(deep = True).reset_index(drop = True),
                                              how = "left", on = "apt_name")
print(len(df_fa21))
df_fa21.head()


# In[322]:


grouped_fa21=df_fa21.groupby(['anonid', 'apt_name', 'apt_set'])['score'].max()
grouped_fa21.head()
display(grouped_fa21)


# In[323]:


#find max score per submission per student
new_df_fa21=df_fa21.groupby( [ "anonid", "apt_name", "apt_set"])['score'].max().to_frame(name = 'max_score').reset_index()
new_df_fa21.head()


# In[324]:


#clean column entry
new_df_fa21.replace('wrongclass', 0.0)
new_df_fa21.replace('nocompile', 0.0)
new_df_fa21['max_score'] = pd.to_numeric(new_df_fa21['max_score'], errors='coerce')


# In[325]:


#check column types
new_df_fa21.dtypes


# In[326]:


#add struggling column, where max apt score is less than 100%
new_df_fa21['struggling'] = new_df_fa21['max_score']<1.00000
print(len(new_df_fa21))
new_df_fa21.head()


# In[327]:


#sort for only struggling students
struggling_students_fa21 = new_df_fa21[new_df_fa21['struggling'] == True] 
print(len(struggling_students_fa21))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_students_fa21)


# In[328]:


#count number of struggling students
new_df_fa21.groupby(['struggling']).count()


# In[329]:


struggling_students_fa21.groupby(['apt_set']).count()


# In[330]:


#number of struggles per student
struggling_count_fa21=struggling_students_fa21.groupby(['anonid']).count()
struggling_count_fa21.sort_values(by='apt_name', ascending=False)
print(len(struggling_count_fa21))
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(struggling_count_fa21)


# In[331]:


#view number of struggles per student
sns.histplot(data = struggling_count_fa21, x = "apt_name")


# In[332]:


only_fail_fa21=df_fa21

only_fail_fa21=df_fa21
only_fail_fa21.replace('wrongclass', 0.0)
only_fail_fa21.replace('nocompile', 0.0)
only_fail_fa21['score'] = pd.to_numeric(only_fail_fa21['score'], errors='coerce')

only_fail_fa21 = only_fail_fa21[only_fail_fa21['score'] < 1.000]




#only_fail = only_fail[only_fail['score'] == True] 
only_fail_fa21.head()


# In[333]:


only_fail_fa21.dtypes


# In[334]:


redefine_fa21=df_fa21.groupby( [ "anonid", "apt_name", "apt_set"]).count()
redefine_fa21 = redefine_fa21[redefine_fa21.columns[~redefine_fa21.columns.isin(['score', 'semester', 'concept', 'type', 'mapping', 'assign_date', 'due_date', 'late_due', 'required', 'notes', 'other'])]]
redefine_fa21 = redefine_fa21.rename(columns={'timestamp': 'num_submissions'})
redefine_fa21['struggling']=redefine_fa21['num_submissions']>=3
redefine_fa21.head()


# In[335]:


redefine_fa21=redefine_fa21.sort_values(by=['num_submissions'])
sns.histplot(data = redefine_fa21, x = "anonid")
median_submissions_fa21=redefine_fa21["num_submissions"].median()
max_submissions_fa21=redefine_fa21['num_submissions'].max()
mean_submissions_fa21=redefine_fa21['num_submissions'].mean()
print(median_submissions_fa21)
print(max_submissions_fa21)
print(mean_submissions_fa21)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# # GRADESCOPE Fall 2020

# ### Parsing Gradescope data Fa20

# In[287]:


#import data for fall 2020
fa20_hw1 = pd.read_csv("cs101fa20-hw1.csv")
fa20_hw2 = pd.read_csv("cs101fa20-hw2.csv")
fa20_hw3 = pd.read_csv("cs101fa20-hw3.csv")
fa20_hw4 = pd.read_csv("cs101fa20-hw4.csv")
fa20_hw5 = pd.read_csv("cs101fa20-hw5.csv")
fa20_hw6 = pd.read_csv("cs101fa20-hw6.csv")


# In[288]:


#clean columns for fall 2020
fa20_hw1 = fa20_hw1[[':anonid', 'autograder_score', 'autograder_max', ":created_at"]].rename(columns = {':anonid':'anonid', ':created_at':'timestamp'})
fa20_hw2 = fa20_hw2[[':anonid', 'autograder_score', 'autograder_max', ":created_at"]].rename(columns = {':anonid':'anonid', ':created_at':'timestamp'})
fa20_hw3 = fa20_hw3[[':anonid', 'autograder_score', 'autograder_max', ":created_at"]].rename(columns = {':anonid':'anonid', ':created_at':'timestamp'})
fa20_hw4 = fa20_hw4[[':anonid', 'autograder_score', 'autograder_max', ":created_at"]].rename(columns = {':anonid':'anonid', ':created_at':'timestamp'})
fa20_hw5 = fa20_hw5[[':anonid', 'autograder_score', 'autograder_max', ":created_at"]].rename(columns = {':anonid':'anonid', ':created_at':'timestamp'})
fa20_hw6 = fa20_hw6[[':anonid', 'autograder_score', 'autograder_max', ":created_at"]].rename(columns = {':anonid':'anonid', ':created_at':'timestamp'})

fa20_hw5.head()


# In[289]:


#find median number of submissions per student for each homework
fa20_hw1_num_submissions=fa20_hw1.groupby( [ "anonid"]).count()
fa20_hw1_med_submissions=fa20_hw1_num_submissions["autograder_score"].median()

fa20_hw2_num_submissions=fa20_hw2.groupby( [ "anonid"]).count()
fa20_hw2_med_submissions=fa20_hw2_num_submissions["autograder_score"].median()

fa20_hw3_num_submissions=fa20_hw3.groupby( [ "anonid"]).count()
fa20_hw3_med_submissions=fa20_hw3_num_submissions["autograder_score"].median()

fa20_hw4_num_submissions=fa20_hw4.groupby( [ "anonid"]).count()
fa20_hw4_med_submissions=fa20_hw4_num_submissions["autograder_score"].median()

fa20_hw5_num_submissions=fa20_hw5.groupby( [ "anonid"]).count()
fa20_hw5_med_submissions=fa20_hw5_num_submissions["autograder_score"].median()

fa20_hw6_num_submissions=fa20_hw6.groupby( [ "anonid"]).count()
fa20_hw6_med_submissions=fa20_hw6_num_submissions["autograder_score"].median()


print(fa20_hw1_num_submissions.head())

print('Fa20 HW1 Median Submissions:')
print(fa20_hw1_med_submissions)

print('Fa20 HW2 Median Submissions:')
print(fa20_hw2_med_submissions)

print('Fa20 HW3 Median Submissions:')
print(fa20_hw3_med_submissions)

print('Fa20 HW4 Median Submissions:')
print(fa20_hw4_med_submissions)

print('Fa20 HW5 Median Submissions:')
print(fa20_hw5_med_submissions)

print('Fa20 HW6 Median Submissions:')
print(fa20_hw6_med_submissions)


# In[290]:


#getting only struggling students for each homework using respective medians
#top number in output is total students that submitted and bottom number is only the strugglers

print('hw1 Fa20')
fa20_hw1_num_submissions['struggling']=fa20_hw1_num_submissions['autograder_score']>=4
print(len(fa20_hw1_num_submissions)) #total students
fa20_hw1_strugglers=fa20_hw1_num_submissions[fa20_hw1_num_submissions['struggling'] == True] 
print(len(fa20_hw1_strugglers)) #struggling students

print('hw2 Fa20')
fa20_hw2_num_submissions['struggling']=fa20_hw2_num_submissions['autograder_score']>=3
print(len(fa20_hw2_num_submissions)) #total students
fa20_hw2_strugglers=fa20_hw2_num_submissions[fa20_hw2_num_submissions['struggling'] == True] 
print(len(fa20_hw2_strugglers)) #struggling students

print('hw3 Fa20')
fa20_hw3_num_submissions['struggling']=fa20_hw3_num_submissions['autograder_score']>=4
print(len(fa20_hw3_num_submissions)) #total students
fa20_hw3_strugglers=fa20_hw3_num_submissions[fa20_hw3_num_submissions['struggling'] == True] 
print(len(fa20_hw3_strugglers)) #struggling students

print('hw4 Fa20')
fa20_hw4_num_submissions['struggling']=fa20_hw4_num_submissions['autograder_score']>=4
print(len(fa20_hw4_num_submissions)) #total students
fa20_hw4_strugglers=fa20_hw4_num_submissions[fa20_hw4_num_submissions['struggling'] == True] 
print(len(fa20_hw4_strugglers)) #struggling students

print('hw5 Fa20')
fa20_hw5_num_submissions['struggling']=fa20_hw5_num_submissions['autograder_score']>=5
print(len(fa20_hw5_num_submissions)) #total students
fa20_hw5_strugglers=fa20_hw5_num_submissions[fa20_hw5_num_submissions['struggling'] == True] 
print(len(fa20_hw5_strugglers)) #struggling students

print('hw6 Fa20')
fa20_hw6_num_submissions['struggling']=fa20_hw6_num_submissions['autograder_score']>=10
print(len(fa20_hw6_num_submissions)) #total students
fa20_hw6_strugglers=fa20_hw6_num_submissions[fa20_hw6_num_submissions['struggling'] == True] 
print(len(fa20_hw6_strugglers)) #struggling students


# In[291]:


#get complete dataset with ony struggling students for each hw
print('fa20 hw1')
print(len(fa20_hw1))
fa20_hw1_strugglers=fa20_hw1_strugglers.reset_index()
fa20_hw1_strugglers.head()
fa20_hw1_struggling_students=fa20_hw1[fa20_hw1["anonid"].isin(fa20_hw1_strugglers["anonid"])]
print(len(fa20_hw1_struggling_students))

print('fa20 hw2')
print(len(fa20_hw2))
fa20_hw2_strugglers=fa20_hw2_strugglers.reset_index()
fa20_hw2_strugglers.head()
fa20_hw2_struggling_students=fa20_hw2[fa20_hw2["anonid"].isin(fa20_hw2_strugglers["anonid"])]
print(len(fa20_hw2_struggling_students))

print('fa20 hw3')
print(len(fa20_hw3))
fa20_hw3_strugglers=fa20_hw3_strugglers.reset_index()
fa20_hw3_strugglers.head()
fa20_hw3_struggling_students=fa20_hw3[fa20_hw3["anonid"].isin(fa20_hw3_strugglers["anonid"])]
print(len(fa20_hw3_struggling_students))

print('fa20 hw4')
print(len(fa20_hw4))
fa20_hw4_strugglers=fa20_hw4_strugglers.reset_index()
fa20_hw4_strugglers.head()
fa20_hw4_struggling_students=fa20_hw4[fa20_hw4["anonid"].isin(fa20_hw4_strugglers["anonid"])]
print(len(fa20_hw4_struggling_students))

print('fa20 hw5')
print(len(fa20_hw5))
fa20_hw5_strugglers=fa20_hw5_strugglers.reset_index()
fa20_hw5_strugglers.head()
fa20_hw5_struggling_students=fa20_hw5[fa20_hw5["anonid"].isin(fa20_hw5_strugglers["anonid"])]
print(len(fa20_hw5_struggling_students))

print('fa20 hw6')
print(len(fa20_hw6))
fa20_hw6_strugglers=fa20_hw6_strugglers.reset_index()
fa20_hw6_strugglers.head()
fa20_hw6_struggling_students=fa20_hw6[fa20_hw6["anonid"].isin(fa20_hw6_strugglers["anonid"])]
print(len(fa20_hw6_struggling_students))


# In[292]:


#check to make sure correct number of students are included in struggling dataset (should match # of struggling students)
print(len(fa20_hw1_struggling_students.groupby("anonid")))
print(len(fa20_hw2_struggling_students.groupby("anonid")))
print(len(fa20_hw3_struggling_students.groupby("anonid")))
print(len(fa20_hw4_struggling_students.groupby("anonid")))
print(len(fa20_hw5_struggling_students.groupby("anonid")))
print(len(fa20_hw6_struggling_students.groupby("anonid")))


# ### Office Hours data for Fa20 (in terms of gradescope)

# In[293]:


#create dataset of OH visits for each particular 
#find number of visits per homework

oh_hw1_fa20 = office_hours_fa20[office_hours_fa20['Assignment 1: Totem'] == "True"] 
oh_hw2_fa20 = office_hours_fa20[office_hours_fa20['Assignment 2: Turtles'] == "True"] 
oh_hw3_fa20 = office_hours_fa20[office_hours_fa20['Assignment 3: Transform'] == "True"] 
oh_hw4_fa20 = office_hours_fa20[office_hours_fa20['Assignment 4: Hangman'] == "True"] 
oh_hw5_fa20 = office_hours_fa20[office_hours_fa20['Assignment 5: Clever Hangman'] == "True"] 
oh_hw6_fa20 = office_hours_fa20[office_hours_fa20['Assignment 6: Recommender'] == "True"] 


print(len(oh_hw1_fa20))
print(len(oh_hw2_fa20))
print(len(oh_hw3_fa20))
print(len(oh_hw4_fa20))
print(len(oh_hw5_fa20))
print(len(oh_hw6_fa20))


# In[294]:


oh_hw1_fa20.dtypes


# In[295]:


#convert time values to UTC timestamps
oh_hw1_fa20['startedAt'] = pd.to_datetime(oh_hw1_fa20.startedAt).dt.tz_convert('utc')
oh_hw1_fa20['requestedAt'] = pd.to_datetime(oh_hw1_fa20.startedAt).dt.tz_convert('utc')
oh_hw1_fa20['completedAt'] = pd.to_datetime(oh_hw1_fa20.startedAt).dt.tz_convert('utc')


# In[296]:


#convert time values to UTC timestamps

oh_hw2_fa20['startedAt'] = pd.to_datetime(oh_hw2_fa20.startedAt).dt.tz_convert('utc')
oh_hw2_fa20['requestedAt'] = pd.to_datetime(oh_hw2_fa20.startedAt).dt.tz_convert('utc')
oh_hw2_fa20['completedAt'] = pd.to_datetime(oh_hw2_fa20.startedAt).dt.tz_convert('utc')

oh_hw3_fa20['startedAt'] = pd.to_datetime(oh_hw3_fa20.startedAt).dt.tz_convert('utc')
oh_hw3_fa20['requestedAt'] = pd.to_datetime(oh_hw3_fa20.startedAt).dt.tz_convert('utc')
oh_hw3_fa20['completedAt'] = pd.to_datetime(oh_hw3_fa20.startedAt).dt.tz_convert('utc')

oh_hw4_fa20['startedAt'] = pd.to_datetime(oh_hw4_fa20.startedAt).dt.tz_convert('utc')
oh_hw4_fa20['requestedAt'] = pd.to_datetime(oh_hw4_fa20.startedAt).dt.tz_convert('utc')
oh_hw4_fa20['completedAt'] = pd.to_datetime(oh_hw4_fa20.startedAt).dt.tz_convert('utc')

oh_hw5_fa20['startedAt'] = pd.to_datetime(oh_hw5_fa20.startedAt).dt.tz_convert('utc')
oh_hw5_fa20['requestedAt'] = pd.to_datetime(oh_hw5_fa20.startedAt).dt.tz_convert('utc')
oh_hw5_fa20['completedAt'] = pd.to_datetime(oh_hw5_fa20.startedAt).dt.tz_convert('utc')

oh_hw6_fa20['startedAt'] = pd.to_datetime(oh_hw6_fa20.startedAt).dt.tz_convert('utc')
oh_hw6_fa20['requestedAt'] = pd.to_datetime(oh_hw6_fa20.startedAt).dt.tz_convert('utc')
oh_hw6_fa20['completedAt'] = pd.to_datetime(oh_hw6_fa20.startedAt).dt.tz_convert('utc')


# In[297]:


#include only students struggling on that particular homework in the OH dataset
fa20_hw1_oh_only_struggling=oh_hw1_fa20[oh_hw1_fa20["anonStudent"].isin(fa20_hw1_struggling_students["anonid"])]
print(len(fa20_hw1_oh_only_struggling))

fa20_hw2_oh_only_struggling=oh_hw2_fa20[oh_hw2_fa20["anonStudent"].isin(fa20_hw2_struggling_students["anonid"])]
print(len(fa20_hw2_oh_only_struggling))

fa20_hw3_oh_only_struggling=oh_hw3_fa20[oh_hw3_fa20["anonStudent"].isin(fa20_hw3_struggling_students["anonid"])]
print(len(fa20_hw3_oh_only_struggling))

fa20_hw4_oh_only_struggling=oh_hw4_fa20[oh_hw4_fa20["anonStudent"].isin(fa20_hw4_struggling_students["anonid"])]
print(len(fa20_hw4_oh_only_struggling))

fa20_hw5_oh_only_struggling=oh_hw5_fa20[oh_hw5_fa20["anonStudent"].isin(fa20_hw5_struggling_students["anonid"])]
print(len(fa20_hw5_oh_only_struggling))

fa20_hw6_oh_only_struggling=oh_hw6_fa20[oh_hw6_fa20["anonStudent"].isin(fa20_hw6_struggling_students["anonid"])]
print(len(fa20_hw6_oh_only_struggling))


# In[298]:


fa20_hw1_oh_only_struggling=fa20_hw1_oh_only_struggling.rename(columns={"anonStudent": "anonid"})
fa20_hw2_oh_only_struggling=fa20_hw2_oh_only_struggling.rename(columns={"anonStudent": "anonid"})
fa20_hw3_oh_only_struggling=fa20_hw3_oh_only_struggling.rename(columns={"anonStudent": "anonid"})
fa20_hw4_oh_only_struggling=fa20_hw4_oh_only_struggling.rename(columns={"anonStudent": "anonid"})
fa20_hw5_oh_only_struggling=fa20_hw5_oh_only_struggling.rename(columns={"anonStudent": "anonid"})
fa20_hw6_oh_only_struggling=fa20_hw6_oh_only_struggling.rename(columns={"anonStudent": "anonid"})


# In[299]:


fa20_hw1_gscope_oh=pd.merge(fa20_hw1_oh_only_struggling, fa20_hw1_struggling_students, on=['anonid'])
fa20_hw2_gscope_oh=pd.merge(fa20_hw2_oh_only_struggling, fa20_hw2_struggling_students, on=['anonid'])
fa20_hw3_gscope_oh=pd.merge(fa20_hw3_oh_only_struggling, fa20_hw3_struggling_students, on=['anonid'])
fa20_hw4_gscope_oh=pd.merge(fa20_hw4_oh_only_struggling, fa20_hw4_struggling_students, on=['anonid'])
fa20_hw5_gscope_oh=pd.merge(fa20_hw5_oh_only_struggling, fa20_hw5_struggling_students, on=['anonid'])
fa20_hw6_gscope_oh=pd.merge(fa20_hw6_oh_only_struggling, fa20_hw6_struggling_students, on=['anonid'])


# In[300]:


fa20_hw1_gscope_oh['timestamp'] = pd.to_datetime(fa20_hw1_gscope_oh.timestamp).dt.tz_convert('utc')
fa20_hw2_gscope_oh['timestamp'] = pd.to_datetime(fa20_hw2_gscope_oh.timestamp).dt.tz_convert('utc')
fa20_hw3_gscope_oh['timestamp'] = pd.to_datetime(fa20_hw3_gscope_oh.timestamp).dt.tz_convert('utc')
fa20_hw4_gscope_oh['timestamp'] = pd.to_datetime(fa20_hw4_gscope_oh.timestamp).dt.tz_convert('utc')
fa20_hw5_gscope_oh['timestamp'] = pd.to_datetime(fa20_hw5_gscope_oh.timestamp).dt.tz_convert('utc')
fa20_hw6_gscope_oh['timestamp'] = pd.to_datetime(fa20_hw6_gscope_oh.timestamp).dt.tz_convert('utc')


# In[301]:


duringoh_gradescope_fa20_hw1=fa20_hw1_gscope_oh[(fa20_hw1_gscope_oh['timestamp'] >= fa20_hw1_gscope_oh['startedAt'])& (fa20_hw1_gscope_oh['timestamp'] <= fa20_hw1_gscope_oh['completedAt'])]
print(len(duringoh_gradescope_fa20_hw1))

duringoh_gradescope_fa20_hw2=fa20_hw2_gscope_oh[(fa20_hw2_gscope_oh['timestamp'] >= fa20_hw2_gscope_oh['startedAt'])& (fa20_hw2_gscope_oh['timestamp'] <= fa20_hw2_gscope_oh['completedAt'])]
print(len(duringoh_gradescope_fa20_hw2))

duringoh_gradescope_fa20_hw3=fa20_hw3_gscope_oh[(fa20_hw3_gscope_oh['timestamp'] >= fa20_hw3_gscope_oh['startedAt'])& (fa20_hw3_gscope_oh['timestamp'] <= fa20_hw3_gscope_oh['completedAt'])]
print(len(duringoh_gradescope_fa20_hw3))

duringoh_gradescope_fa20_hw4=fa20_hw4_gscope_oh[(fa20_hw4_gscope_oh['timestamp'] >= fa20_hw4_gscope_oh['startedAt'])& (fa20_hw4_gscope_oh['timestamp'] <= fa20_hw4_gscope_oh['completedAt'])]
print(len(duringoh_gradescope_fa20_hw4))

duringoh_gradescope_fa20_hw5=fa20_hw5_gscope_oh[(fa20_hw5_gscope_oh['timestamp'] >= fa20_hw5_gscope_oh['startedAt'])& (fa20_hw5_gscope_oh['timestamp'] <= fa20_hw5_gscope_oh['completedAt'])]
print(len(duringoh_gradescope_fa20_hw5))

duringoh_gradescope_fa20_hw6=fa20_hw6_gscope_oh[(fa20_hw6_gscope_oh['timestamp'] >= fa20_hw6_gscope_oh['startedAt'])& (fa20_hw6_gscope_oh['timestamp'] <= fa20_hw6_gscope_oh['completedAt'])]
print(len(duringoh_gradescope_fa20_hw6))


# In[ ]:




