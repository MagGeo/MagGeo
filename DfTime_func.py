import pandas as pd
def DfTime_func (SwarmData, GPSTime,DT):
#     DT= 14400 #deltaT of 14400 secs, 4 hours, if the Period is 1s. 1440 for 10s of period. 240 for data every 60s.
    for index in SwarmData.index:
        if index == GPSTime:
            DataFrame_Per_Time = pd.DataFrame(SwarmData.loc[index-DT:index+DT])
    return DataFrame_Per_Time