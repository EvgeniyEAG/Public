import sys
import os
import hashlib
import timeit
import pandas as pd

directory = ['C:/1/Новая папка/']
directory += ['C:/1/Новая папка/1','C:/1/Новая папка/2']

fileForWriteName='ResDpubleU.xlsx'
filtsize=0.05 *1024*1024    #Минимальный размер файла для анализа, взятие хэша дорогая процедура 
listFiles=[]

df = pd.DataFrame( ) 
timerStart = timeit.default_timer()

def gethash(filename,size_out=None):    
    try:
        filehash = hashlib.sha512(open(filename, 'rb').read(size_out)).hexdigest()
    except Exception:
        filehash="Exception"
    return filehash

def getsize(filename,size_out=1):
    try:
        filehash = os.path.getsize(filename)
    except Exception:
        filehash=-1
    return filehash

for path in directory:
    for d, dirs, files in os.walk(path):
        for file in files:            
            fullname = os.path.join(d, file)            
            try:
                listFiles.append( [fullname,getsize(fullname)])
            except (OSError,):                
                pass      
                
print("Список файлов создан")
print(timeit.default_timer() - timerStart)
df = pd.DataFrame.from_records(listFiles) 

def fgroupby(df, col, num='num'):
    df = pd.concat([df, pd.DataFrame(df[col]).rename(columns={col: num})], axis=1)
    mediandone = df.groupby([col]).count()['num']   
    m = pd.DataFrame(mediandone)
    m = m.reset_index(level=[0])
    df = df.drop([num], axis=1)  
    return df.merge(m, on=col, how="left")

dfout=fgroupby(df, 1) 
print("Число файлов: ", len(dfout[0]) )  
print(timeit.default_timer() - timerStart)
print("После анализа по size: %d файлов %.2d MB" % (len(dfout[dfout.num>1][0]) ,dfout[dfout.num>1][1].sum()/1024/1024))
print(timeit.default_timer() - timerStart)

print("Идет Анализ Hash1024")
listFiles=[]
if dfout[dfout.num > 1][1].sum()>150*1024*1024:    #Если сумарный объем данных превышает указанное значение, файлы размером менее filtsize искл из рассмотрения
    print("После анализа по size: %d %.2d MB" % (len(dfout[dfout.num > 1][dfout[1]>filtsize][0]),
                                                 dfout[dfout.num > 1][dfout[1]>filtsize][1].sum() / 1024 / 1024))
    dfout=dfout[dfout[1]>filtsize]
for index, row in dfout.loc[dfout.num>1][[0,1]].iterrows():
    listFiles.append([row[0], row[1],gethash(row[0],1024)])
df = pd.DataFrame.from_records(listFiles)
dfout=fgroupby(df, 2)
print("Число файлов: ",len(dfout[0]))
print("После анализа по Hash1024: ",len(dfout[dfout.num>1][0]))
print(timeit.default_timer() - timerStart)

print("Идет Анализ Hash All")
listFiles=[]
for index, row in dfout[dfout.num>1][[0,1,2]].iterrows():
    listFiles.append([row[0], row[1], gethash(row[0],None)])
df = pd.DataFrame.from_records(listFiles)
dfout=fgroupby(df, 2)
print("Число файлов: ",len(dfout[0]))
print(timeit.default_timer() - timerStart)

print("Идет Запись")
print("Число ДУБЛИКАТОВ: ",len(dfout[dfout.num>1][0]))

pd.DataFrame(dfout).to_csv('ResHash1.txt')   #резервная запись csv

pd.DataFrame(dfout).to_excel('ResHash1.xlsx', 'Data') #Запись excel

writer = pd.ExcelWriter(fileForWriteName)
dfout[dfout.num>1].to_excel(writer,'Double')     #Запись через  OpenPyXl, 
writer.save()

print(timeit.default_timer() - timerStart) 