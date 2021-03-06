import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import WindowGenerator as wg
import Models

#Input variables.
EPOCHS = 5
BATCH_SIZE = 1000

#Import data from csv.
df = pd.read_csv("EURUSDDATA.csv")

#Remove data rows with missing SMA values.
df = df.dropna(subset=["SMA20","SMA50","SMA200"])
df = df.reset_index(drop=True)

#Encode day of week catagory.
days = df[["DayOfWeek"]]
print(len(days))
def encode_day(day):
    return time.strptime(day, "%A").tm_wday
days_encoded = pd.Series(map(encode_day, days["DayOfWeek"]))
print(len(days_encoded))
df["DayOfWeek"] = days_encoded

#Convert time inputs to oscillating signals.
df["YearSin"] = np.sin(2*np.pi*df["DayOfYear"]/364)
df["YearCos"] = np.cos(2*np.pi*df["DayOfYear"]/364)
df["DaySin"] = np.sin((2*np.pi/6)*df["DayOfWeek"])
df["DayCos"] = np.cos((2*np.pi/6)*df["DayOfWeek"])
df["HourSin"] = np.sin((2*np.pi/23)*df["Hour"])
df["HourCos"] = np.cos((2*np.pi/23)*df["Hour"])

#Remove original time columns.
df = df.drop(columns=["DayOfYear", "DayOfWeek", "Hour"])

#Normalise ask, sma20 and sma50 using sma200.
df["Open"] = df["Open"]-df["SMA200"]
df["Close"] = df["Close"]-df["SMA200"]
df["High"] = df["High"]-df["SMA200"]
df["Low"] = df["Low"]-df["SMA200"]
df["SMA20"] = df["SMA20"]-df["SMA200"]
df["SMA50"] = df["SMA50"]-df["SMA200"]
df["Open"] = df["Open"]/max(abs(df["Open"]))
df["Close"] = df["Close"]/max(abs(df["Close"]))
df["High"] = df["High"]/max(abs(df["High"]))
df["Low"] = df["Low"]/max(abs(df["Low"]))
df["SMA20"] = df["SMA20"]/max(abs(df["SMA20"]))
df["SMA50"] = df["SMA50"]/max(abs(df["SMA50"]))

#Remove SMA200.
df = df.drop(columns=["SMA200"])

#Function to split data into training, validation and test sets.
def split_train_val_test(data, train_prop=0.7, val_prop=0.2):
    n = len(data)
    train_df = data[0:int(n*train_prop)]
    val_df = data[int(n*train_prop):int(n*(train_prop+val_prop))]
    test_df = data[int(n*(train_prop+val_prop)):]
    return train_df, val_df, test_df

#Create window.
train_df, val_df, test_df = split_train_val_test(df)
window = wg.WindowGenerator(input_width=24*5, label_width=24, shift=24, label_columns=["Close"], 
                            train_df=train_df, val_df=val_df, test_df=test_df, batch_size=BATCH_SIZE)

#Create shallow LSTM model.
shallow_LSTM, model_name = Models.Shallow_LSTM()

#Compile and fit deep LSTM model.
history = Models.Compile_And_Fit(shallow_LSTM, window, EPOCHS)

#Save the trained model.
path = "Saved Models\\" + model_name
Models.Save_Model(shallow_LSTM, path)

#Plot results.
pd.DataFrame(history.history).plot(figsize=(8,5))
plt.grid(True)
window.plot("Close", shallow_LSTM)
plt.show()