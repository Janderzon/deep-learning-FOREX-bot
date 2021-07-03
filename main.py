import pandas as pd
import time

#Import data from csv.
df = pd.read_csv("EURUSDDATA.csv")

#Remove data rows with missing SMA values.
df = df.dropna(subset=["SMA20","SMA50"])

#Encode day of week catagory.
days = df[["DayOfWeek"]]
def encode_day(day):
    return time.strptime(day, "%A").tm_wday
days_encoded = pd.Series(map(encode_day, days["DayOfWeek"]))
df[["DayOfWeek"]] = days_encoded

#Function to split data into training, validation and test sets.
def split_train_val_test(data, train_prop=0.7, val_prop=0.2):
    n = len(data)
    train_df = data[0:int(n*train_prop)]
    val_df = data[int(n*train_prop):int(n*(train_prop+val_prop))]
    test_df = data[int(n*(train_prop+val_prop)):]
    return train_df, val_df, test_df