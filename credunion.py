"""credit union"""
#Month of data to start reading (0 = first month)
firstmonth = 16
lastmonth = 29

#%%
import pandas as pd
from os import listdir

#Find all files in specified directory, create a list of their paths
mypath = "c:/users/john/desktop/credit union/data" 
files = [mypath + "/" + filename for filename in listdir(mypath)]

#%%
#Read in each csv as a separate dataframe and append to list
dfs = []
for filename in files:
    mydf = pd.read_csv(filename)
    
    #Standardize names, POSActvty should be EFTActvty
    if "EFTActvty" in mydf.columns:
        mydf.rename(columns = {"EFTActvty":"POSActvty"}, inplace = True)
    dfs.append(mydf)

#%%
#Add indicator variable for month associated with data
origin = 1
for df in dfs:
    if origin in [1,3,11]:
        df["geoLatitudeIndImp24"] = None
        df["geoLongitudeIndImp24"] = None
    df["Month"] = origin
    origin += 1

#%%
#Combine list of dataframes into one df
massivedf = pd.concat(dfs)

#%%
"""
0 - AltServiceClassDescription
1 - ProductCodeAcct
2 - BalanceAcct
3 - OpeningBalanceAcct
4 - CreditLimitAcct
5 - InterestRateAcct
6 - OpenDateAcct
7 - MaturityDateAcct
8 - NSFSActvty
9 - ATMONUSActvty
10 - ATMFOREIGNActvty
11 - POSActvty
12 - TELLERTRANSActvty
13 - ATMFEESActvty
14 - ATMFOREIGNDEPActvty
15 - ATMFOREIGNWITHActvty
16 - ATMONUSDEPActvty
17 - ATMONUSWITHActvty
18 - SHAREDBRANCHTRANSActvty
19 - BALANCEFEESActvty
20 - NSFFEESActvty
21 - OTHERFEESActvty
22 - ACCOUNTTYPEAext
23 - CHARGEOFFACCOUNTAext
24 - CLASSAext
25 - CREDITCARDAext
26 - DATEOFDEATHAext
27 - DEBITCARDAext
28 - DEBITCARDTRANSAext
29 - DIRECTDEPOSITAext
30 - EMPLOYEECODEAext
31 - DEPOSITSPERMONTHAext
32 - WITHDRAWSPERMONTHAext
33 - AgeIND
34 - DurationYearsIND
35 - DurationMonthsIND
36 - TypeIND
37 - NumberofAccountsIND
38 - NumberofLoanAccountsIND
39 - NumberofDepositAccountsIND
40 - geoLatitudeIndImp24
41 - geoLongitudeIndImp24
42 - SCOREIndImp32
43 - SCOREDATEIndImp32
44 - SOURCEIndImp32
45 - Adj004_Last_Login_DateIndImp10
46 - Adj003_Registration_DateIndImp10
47 - Member Number
48 - Month
"""
#%%
#groupby = list(massivedf.groupby("Member Number"))
groupby = massivedf.groupby("Member Number")

#%%

survdata = pd.DataFrame(index = range(7000000))
cols = ["MemNum","Time","Churn","MemType","LoanAccts","DepAccts","POSTrans","TellerTrans","Age","CreditCard","DebitCard","DirectDeposit","NumDeposits","NumWithdrawals","Month"]

for col in cols:
    survdata[col] = None
survdata["Churn"] = 0
        
counter = 0
survdata.iat[0, 14] = 0
for memnum, temp in groupby:
    survdata.iat[0,0] = memnum
    print("Processing {}".format(memnum))
    time = 0
    for period, df in temp.groupby("Month"):

        time += 1
        counter += 1

        if survdata.iat[counter - 1, 14] + 1 != period and survdata.iat[counter - 1, 0] == memnum:
            survdata.iat[counter - 1, 2] = 1
            counter -= 1
            break
        
        survdata.iat[counter,0] = memnum
        survdata.iat[counter,1] = time
        survdata.iat[counter, 3] = df.iat[0, 36]
        survdata.iat[counter, 4] = df.iat[0, 38]
        survdata.iat[counter, 5] = df.iat[0, 39]
        survdata.iat[counter, 6] = df["POSActvty"].sum()
        survdata.iat[counter, 7] = df["TELLERTRANSActvty"].sum()
        survdata.iat[counter, 8] = df.iat[0, 33]
        survdata.iat[counter, 9] = any(df["CREDITCARDAext"] == "Y")
        survdata.iat[counter, 10] = any(df["DEBITCARDAext"] == "Y")
        survdata.iat[counter, 11] = any(df["DIRECTDEPOSITAext"] == "Y")
        survdata.iat[counter, 12] = df["DEPOSITSPERMONTHAext"].sum()
        survdata.iat[counter, 13] = df["WITHDRAWSPERMONTHAext"].sum()
        survdata.iat[counter, 14] = period
        
    if period != 25:
        survdata.iat[counter, 2] = 1


#%%
#Ad-Hoc analysis of member 245.16
twofitty = dfs[0][dfs[0]["Member Number"] == 245.16]
twofitty["Origin"] = 1
origin = 2
for df in dfs[1:]:
    temp = df[df["Member Number"] == 245.16]
    temp["Origin"] = origin
    twofitty = pd.concat([twofitty,temp])
    origin += 1
    
twofitty.to_csv("Mem24516.csv")
#%%
#Create a set containing all member numbers, print some summary statistics
allmembers = set(massivedf["Member Number"])
print("Total Members: {}".format(len(allmembers)))
print("Active Members: {}".format(len(set(dfs[-1]["Member Number"]))))
print("Number of Accounts (Sep 2016): {}".format(len(dfs[-1])))
#%%
#Create the base dataframe with beginning and end dates
#Dates initialized to dummy values for easier comparison
memberdf = pd.DataFrame(index = allmembers)
memberdf["Begin"] = "3000.01"
memberdf["End"] = "3000.01"
memberdf["Return"] = False
i = 0
date = "2014.09"

for i, date in zip(range(25), map(lambda x: x.split("_")[-1][:-4], files)):
    print("Looking at {}".format(date))
    
    #Get the ids of members present in the current month
    active = set(dfs[i]["Member Number"])

    #Get an indexer for the members who are present
    activebool = memberdf.index.isin(active)    
    
    #If they're present this month, and the month is before the value in "Begin" (default is year 3000), set to current month
    memberdf.loc[(date < memberdf["Begin"]) & activebool, "Begin"] = date
                 
    #If they're not present this month, and this month is after their beginning month, but before their end month (default is year 3000), set to current month
    memberdf.loc[((memberdf["Begin"] < date) & (date < memberdf["End"])) & (~activebool), "End"] = date
                 
    #If their end month has already been set, but then they're active in this month, reset end month to default
    #Mark these customers as repatriated
    memberdf.loc[(memberdf["End"] != "3000.01") & activebool, "Return"] = True
    memberdf.loc[(memberdf["End"] != "3000.01") & activebool, "End"] = "3000.01"

#Everyone who has a different date has churned
memberdf["Churned"] = memberdf["End"] != "3000.01"

#Get rid of remaining dummy values
memberdf.loc[memberdf.End == "3000.01","End"] = None
memberdf.loc[memberdf.Begin == "3000.01","Begin"] = None            
            
#Convert to datetime
memberdf.End = pd.to_datetime(memberdf.End)
memberdf.Begin = pd.to_datetime(memberdf.Begin)

#Check for correctness
all(pd.isnull(memberdf.End) | (memberdf.Begin < memberdf.End))

#%%
#Add more individual data to memberdf, here we define Lat/Long columns and find the number of different Lat/Long combinations a member has had
memberdf["Lat"] = None
memberdf["Long"] = None
lenuniq = lambda x: pd.notnull(x.unique()).sum()

#Aggregate by member number
aggdata = massivedf.groupby("Member Number").agg({"geoLatitudeIndImp24":lenuniq, "geoLongitudeIndImp24":lenuniq})

#Merge the aggregate data to the member dataframe
merged = pd.merge(memberdf, aggdata, left_index = True, right_index = True, how = "left")
merged.head()

#Assign the higher of number of unique lat/lon
merged["UniqueCoords"] = merged["geoLatitudeIndImp24"]
boolz = merged["UniqueCoords"] < merged["geoLongitudeIndImp24"]
merged.loc[boolz,"UniqueCoords"] = merged.loc[boolz,"geoLongitudeIndImp24"]

#Drop redundant columns
merged = merged.drop(["geoLongitudeIndImp24","geoLatitudeIndImp24"], 1)

#%%
#Grab the most recent Lat/Long pair possible
for i in range(24, -1, -1):
    print("Aggregating df {}".format(i))
    aggdata = dfs[i].groupby("Member Number").agg({"geoLatitudeIndImp24":max, "geoLongitudeIndImp24":max})
    merged = pd.merge(merged, aggdata, left_index = True, right_index = True, how = "left")
    boolz = pd.isnull(merged.Long)
    merged.loc[boolz, "Lat"] = merged.loc[boolz, "geoLatitudeIndImp24"]
    merged.loc[boolz, "Long"] = merged.loc[boolz, "geoLongitudeIndImp24"]
    merged = merged.drop(["geoLongitudeIndImp24","geoLatitudeIndImp24"], 1)

#%%
#Find the actual month of account opening
#Might not be entirely accurate...

"""Ended up not using this

merged.Begin = None
dates = list(pd.date_range("2014.09.01", "2016.09.01", freq = "MS"))
dates.reverse()

for i, date in zip(range(24, -1, -1), dates):
    print("Aggregating df {}".format(i))
    merged["Date"] = date
    aggdata = dfs[i].groupby("Member Number").agg({"DurationMonthsIND":max})
    merged = pd.merge(merged, aggdata, left_index = True, right_index = True, how = "left")
    boolz = pd.isnull(merged.Begin)
    merged.loc[boolz, "Begin"] = merged.loc[boolz, "Date"] - pd.to_timedelta(merged.loc[boolz, "DurationMonthsIND"], unit = "M") - pd.DateOffset(hours = 13)
    merged = merged.drop("DurationMonthsIND", 1)

merged = merged.drop("Date", 1)

"""

#%%
#Find most recent values for age, credit score, customer type, membership duration
cols = ["AgeIND","SCOREIndImp32","TypeIND","DurationMonthsIND"]

#Initialize columns to None
for data in cols:
    merged[data[:-3]] = None

#Loop through the list of dataframes backwards
for i in range(24, -1, -1):
    print("Aggregating df {}".format(i))
    for data in cols:
        #Aggregate by member number and find the max value from their accounts
        aggdata = dfs[i].groupby("Member Number").agg({data:max})
        
        #Merge the aggregated data
        merged = pd.merge(merged, aggdata, left_index = True, right_index = True, how = "left")
        
        #Find out which values in the associated column are still None
        boolz = pd.isnull(merged[data[:-3]])
        
        #Update the remaining None values with values that appear in the current month's data
        merged.loc[boolz, data[:-3]] = merged.loc[boolz, data]
        
        #Delete the temporary columns
        merged = merged.drop(data, 1)
#%%
#New columns, same process as above
cols = ["CHARGEOFFACCOUNTAext","CREDITCARDAext","DEBITCARDAext","DIRECTDEPOSITAext"]
for data in cols:
    merged[data[:-3]] = None

for i in range(24, -1, -1):
    print("Aggregating df {}".format(i))
    for data in cols:
        aggdata = dfs[i].groupby("Member Number").agg({data:lambda x: any(x == "Y")})
        merged = pd.merge(merged, aggdata, left_index = True, right_index = True, how = "left")
        boolz = pd.isnull(merged[data[:-3]])
        merged.loc[boolz, data[:-3]] = merged.loc[boolz, data]
        merged = merged.drop(data, 1)
#%%
cols = ["Adj004_Last_Login_DateIndImp10"]
for data in cols:
    memberdf[data[:-3]] = None

for i in range(24, 21, -1):
    print("Aggregating df {}".format(i))
    for data in cols:
        aggdata = dfs[i].groupby("Member Number").agg({data:lambda x: not all(x.isnull())})
        memberdf = pd.merge(memberdf, aggdata, left_index = True, right_index = True, how = "left")
        boolz = pd.isnull(memberdf[data[:-3]])
        memberdf.loc[boolz, data[:-3]] = memberdf.loc[boolz, data]
        memberdf = memberdf.drop(data, 1)
#%%
#Output for data vis
timeseries = pd.DataFrame(index = pd.date_range("2014.09.01", "2016.10.01", freq= "M"))
timeseries["NumMembers"] = None
timeseries["NumChurn"] = None

for time in timeseries.index:
    timeseries.loc[time, "NumMembers"] = len(merged.loc[(merged.Begin < time) & ((pd.isnull(merged.End) | (time < merged.End)))])
    timeseries.loc[time, "NumChurn"] = len(merged.loc[(~pd.isnull(merged.End) & (time > merged.End) & (merged.End > (time - pd.DateOffset(months = 1))))])

timeseries.to_csv("attrition.csv")

#%%
import pandas as pd
gps = pd.read_csv("c:/users/john/desktop/credit union/gps.txt", sep = "\t")
locations = list(zip(gps.Latitude, gps.Longitude))[:-1]

import math

def haversine_distance(origin, destination):
    """ Haversine formula to calculate the distance between two lat/long points on a sphere """
    radius = 6371 # FAA approved globe radius in km
    
    dlat = math.radians(destination[0]-origin[0])
    dlon = math.radians(destination[1]-origin[1])
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(origin[0])) * math.cos(math.radians(destination[0])) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

  # Return distance in km
    return d
    
def getlowest(origin, destinations):
    distances = []
    for place in destinations:
        distances.append(haversine_distance(origin, place))
    return min(distances)

merged["distance"] = merged.apply(lambda x: getlowest((x.Lat, x.Long), locations), axis = 1)

#%%
merged.NumberofLoanAccounts = merged.NumberofLoanAccounts.fillna(0)
merged.NumberofDepositAccounts = merged.NumberofDepositAccounts.fillna(0)

merged.rename(columns = {"EMPLOYEECODEA":"credit unionEmp","DATEOFDEATHA":"IsDeceased","CHARGEOFFACCOUNTA":"AccountChargedOff","Adj004_Last_Login_DateIndIm":"OnlineBanker"}, inplace = True)
#%%
merged.to_csv("merged.csv")
#%%
import pandas as pd
merged = pd.read_csv("merged.csv")
merged.set_index("Unnamed: 0", inplace = True)

merged.NumberofLoanAccounts = merged.NumberofLoanAccounts.fillna(0)
merged.NumberofDepositAccounts = merged.NumberofDepositAccounts.fillna(0)
merged.Begin = pd.to_datetime(merged.Begin)
merged.End = pd.to_datetime(merged.End)
#%%
dates = pd.date_range("2014.09.01", periods = len(dfs), freq= "MS")
dfdict = {}
for date, df in zip(dates, dfs):
    dfdict[date] = df

#%%
def totaldep(df):
    if len(df) < 1:
        return 0
    result = 0
    for row in df.itertuples():
        if row.CLASSAext == "L":
            result += row.BalanceAcct
    return result

def totalloan(df):
    if len(df) < 1:
        return 0
    result = 0
    for row in df.itertuples():
        if row.CLASSAext != "L":
            result += row.BalanceAcct
    return result

def loanaccts(df):
    if len(df) < 1:
        return 0
    return df.iloc[0,:]["NumberofLoanAccountsIND"]

def depaccts(df):
    if len(df) < 1:
        return 0
    return df.iloc[0,:]["NumberofDepositAccountsIND"]

def numdeps(df):
    return df["DEPOSITSPERMONTHAext"].sum()

def numwiths(df):
    return df["WITHDRAWSPERMONTHAext"].sum()

def numfordep(df):
    return df["ATMFOREIGNDEPActvty"].sum()

def numforwith(df):
    return df["ATMFOREIGNWITHActvty"].sum()

def numtelltrans(df):
    return df["TELLERTRANSActvty"].sum()

def numpostrans(df):
    return df["POSActvty"].sum()

def numltdep(df):
    return (df["ACCOUNTTYPEAext"] == "TD").sum()

def numltloan(df):
    return ((df["ACCOUNTTYPEAext"].isin(["CML","CNS"])) & (df["AltServiceClassDescription"].isin(["Business Visa","VISA"]))).sum()

def credutil(df):
    df = df[df["CreditLimitAcct"] > 0]
    if len(df) < 1:
        return 0
    else:
        return df["BalanceAcct"].sum() / df["CreditLimitAcct"].sum()

def atmfees(df):
    return df["ATMFEESActvty"].sum()

def balancefees(df):
    return df["BALANCEFEESActvty"].sum()

def nsffees(df):
    return df["NSFFEESActvty"].sum()

def otherfees(df):
    return df["OTHERFEESActvty"].sum()
#%%
#Let's calculate values in the final period, 3 months prior, 6 months prior, and 12 months prior
calc = ["TotalDeposits","TotalLoans","LoanAccts","DepAccts","NumDep","NumWith","ForeignDep","ForeignWith","TellerTrans","POSAct","LTDep","LTLoan","CreditUtilization"]
funcs = [totaldep, totalloan, loanaccts, depaccts, numdeps, numwiths,numfordep, numforwith, numtelltrans, numpostrans, numltdep, numltloan, credutil]
data = list(zip(calc, funcs))
newdata = pd.DataFrame(index = merged.index)
for stat in calc:
    for name in ["now","minus3","minus6","minus12"]:
        newdata[stat + name] = None

i = 0

for row in merged.itertuples():
    cnum = row.Index
    last = pd.to_datetime("2016.10.01") if pd.isnull(row.End) else row.End
    times = pd.date_range(end = last, periods = 14, freq= "MS")
    
    for time, name in [(-2,"now"), (-5,"minus3"), (-8,"minus6"), (-14,"minus12")]:
        themonth = times[time]
        if themonth < row.Begin:
            continue
        else:
            monthdf = dfdict[themonth]
            monthdf = monthdf[monthdf["Member Number"] == cnum]
            
            for stat, func in data:
                newdata.at[cnum, stat + name] = func(monthdf)
        
    i += 1
    if i % 1000 == 0:
        print("On row {}".format(i))
        
#%%
def nummaturing(df, currmonth, offset):
    result = 0
    for row in df.itertuples():
        if pd.notnull(row.MaturityDateAcct) and pd.to_datetime(row.MaturityDateAcct) <= currmonth + pd.DateOffset(months = offset):
            result += 1
            
    return result

for time in ["Within3","Within6","Within12"]:
    newdata["LoanMaturing" + time] = None

i = 0

for row in merged.itertuples():
    cnum = row.Index
    last = pd.to_datetime("2016.10.01") if pd.isnull(row.End) else row.End
    times = pd.date_range(end = last, periods = 14, freq= "MS")
    
    for time, name in [(-5,"Within3"), (-8,"Within6"), (-14,"Within12")]:
        themonth = times[time]
        if themonth < row.Begin:
            continue
        else:
            monthdf = dfdict[themonth]
            monthdf = monthdf[monthdf["Member Number"] == cnum]

            bill = 3 if time == -5 else 6 if time == -8 else 12
            newdata.at[cnum, "LoanMaturing" + name] = nummaturing(monthdf, themonth, bill)
        
    i += 1
    if i % 1000 == 0:
        print("On row {}".format(i))
    
#%%
newdata.to_csv("newdata.csv")
merged = pd.merge(merged, newdata, left_index = True, right_index = True)
#%%
merged.to_csv("custdata.csv")

#%%
#Clean up columns
import pandas as pd
custdata = pd.read_csv("custdata.csv")

custdata.set_index("Unnamed: 0", inplace=True)

#Get rid of erroneous credit scores
custdata.loc[custdata.SCOREIndIm == 111, "SCOREIndIm"] = None
custdata.loc[custdata.SCOREIndIm == 448, "SCOREIndIm"] = None
custdata.loc[custdata.SCOREIndIm > 850, "SCOREIndIm"] = 850
custdata.loc[custdata.SCOREIndIm < 350, "SCOREIndIm"] = 350

#Businesses shouldn't have ages.  Impute missing ages for residential members
custdata.loc[custdata.Type == "C", "Age"] = None
custdata.loc[pd.isnull(custdata.Age) & (custdata.Type == "R"), "Age"] = custdata.Age[custdata.Type == "R"].median()            

for extra in ["now","minus3","minus6","minus12"]:
    
    for col in ["TotalDeposits","TotalLoans","CreditUtilization"]:
        custdata.loc[custdata[col + extra] < 0, col + extra] = 0
    
    custdata.loc[custdata["CreditUtilization"+extra] > 1, "CreditUtilization" + extra] = 1
    
    for col in ["LoanAccts"]:
        custdata[col + extra] = custdata[col + extra].fillna(0)
        custdata.loc[pd.isnull(custdata["DepAccts" + extra]), col + extra] = None

feecols = [col for col in custdata.columns if "Fees" in col]

for col in feecols:
    custdata.drop(col, axis = 1, inplace = True)


custdata.to_csv("custdata.csv")

#%%
#Create a function for easy viewing of column statistics
def tellme(x):
    result = "\n\nStatistics for {}:\n".format(x)
    result += str(custdata[x].describe())
    result += "\nNum Null:  " + str(pd.isnull(custdata[x]).sum())
    return result

#%%
#Call function on each column and write output to a file
with open("statistics.txt", "a") as file:
    for column in custdata.columns:
        file.write(tellme(column))
        
#%%
#Grab status as of 3 and 6 months back
sixback = lastmonth - 6
threeback = lastmonth - 3

activemems = pd.DataFrame(index = allmembers)
nowactive = set(dfs[-1]["Member Number"])
threeactive = set(dfs[threeback]["Member Number"])
sixactive = set(dfs[sixback]["Member Number"])

activemems["ActiveNow"] = None
activemems["Active3"] = None
activemems["Active6"] = None
          
activemems.loc[nowactive, "ActiveNow"] = True
activemems.loc[threeactive, "Active3"] = True
activemems.loc[sixactive, "Active6"] = True
              
activemems = activemems[activemems.sum(axis = 1) > 0]
activemems.fillna(False, inplace = True)
activemems = activemems[~(activemems.Active6 & ~activemems.Active3 & activemems.ActiveNow)]
activemems["Active6Churn3"] = activemems.Active6 & ~activemems.Active3
activemems["Active6ChurnNow"] = activemems.Active6 & ~activemems.ActiveNow
activemems["Active3ChurnNow"] = activemems.Active3 & ~activemems.ActiveNow

#%%
#Grab customer-level data for remaining active members
#Find most recent values for age, credit score, customer type, membership duration
cols = ["AgeIND"]

#Initialize columns to None
for data in cols:
    activemems[data[:-3]] = None

#Loop through the list of dataframes backwards
for i in range(lastmonth, sixback-1, -1):
    print("Aggregating df {}".format(i))
    for data in cols:
        #Aggregate by member number and find the max value from their accounts
        aggdata = dfs[i].groupby("Member Number").agg({data:max})
        
        #Merge the aggregated data
        activemems = pd.merge(activemems, aggdata, left_index = True, right_index = True, how = "left")
        
        #Find out which values in the associated column are still None
        boolz = pd.isnull(activemems[data[:-3]])
        
        #Update the remaining None values with values that appear in the current month's data
        activemems.loc[boolz, data[:-3]] = activemems.loc[boolz, data]
        
        #Delete the temporary columns
        activemems = activemems.drop(data, 1)

cols = ["CHARGEOFFACCOUNTAext","CREDITCARDAext","DEBITCARDAext","DIRECTDEPOSITAext"]
for data in cols:
    activemems[data[:-3]] = None

for i in range(lastmonth, sixback-1, -1):
    print("Aggregating df {}".format(i))
    for data in cols:
        aggdata = dfs[i].groupby("Member Number").agg({data:lambda x: any(x == "Y")})
        activemems = pd.merge(activemems, aggdata, left_index = True, right_index = True, how = "left")
        boolz = pd.isnull(activemems[data[:-3]])
        activemems.loc[boolz, data[:-3]] = activemems.loc[boolz, data]
        activemems = activemems.drop(data, 1)
        
#%%
activemems.to_csv("activemembers.csv")
#%%
#Find current/historical values for active members
calc = ["TotalDeposits","TotalLoans","LoanAccts","DepAccts","NumDep","NumWith","ForeignDep","ForeignWith","TellerTrans","POSAct","LTDep","LTLoan","CreditUtilization"]
funcs = [totaldep, totalloan, loanaccts, depaccts, numdeps, numwiths,numfordep, numforwith, numtelltrans, numpostrans, numltdep, numltloan, credutil]
data = list(zip(calc, funcs))
newdata = pd.DataFrame(index = activemems.index)
for stat in calc:
    for name in ["minus3","minus6","minus12"]:
        newdata[stat + name] = None

i = 0

for cnum in activemems.index:
    for time, name in [(threeback,"minus3"), (threeback-3,"minus6"), (threeback-9,"minus12")]:
    
        monthdf = dfs[time]
        monthdf = monthdf[monthdf["Member Number"] == cnum]
        
        for stat, func in data:
            newdata.at[cnum, stat + name] = func(monthdf)
            
    i += 1
    if i % 1000 == 0:
        print("On row {}".format(i))
       
reallynewdata = activemems.merge(newdata, how = "outer", left_index = True, right_index = True)
reallynewdata.to_csv("threebackval.csv")

#%%
#Find current/historical values for active members
calc = ["TotalDeposits","TotalLoans","LoanAccts","DepAccts","NumDep","NumWith","ForeignDep","ForeignWith","TellerTrans","POSAct","LTDep","LTLoan","CreditUtilization"]
funcs = [totaldep, totalloan, loanaccts, depaccts, numdeps, numwiths,numfordep, numforwith, numtelltrans, numpostrans, numltdep, numltloan, credutil]
data = list(zip(calc, funcs))
newdata = pd.DataFrame(index = activemems.index)
for stat in calc:
    for name in ["minus6","minus12"]:
        newdata[stat + name] = None

i = 0

for cnum in activemems.index:
    for time, name in [(sixback,"minus6"), (sixback-6,"minus12")]:
    
        monthdf = dfs[time]
        monthdf = monthdf[monthdf["Member Number"] == cnum]
        
        for stat, func in data:
            newdata.at[cnum, stat + name] = func(monthdf)
            
    i += 1
    if i % 1000 == 0:
        print("On row {}".format(i))
        
reallynewdata = activemems.merge(newdata, how = "outer", left_index = True, right_index = True)
reallynewdata.to_csv("sixbackval.csv")
