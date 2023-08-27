import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle

def linear():
	dataset=pd.read_csv("odi.csv")
	print(dataset.head())
	X = dataset.iloc[:,[7,8,9,12,13]].values #Input features
	y = dataset.iloc[:, 14].values
	from sklearn.model_selection import train_test_split
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25,random_state=42)
	from sklearn.linear_model import LinearRegression
	lin = LinearRegression()
	lin.fit(X_train,y_train)
	pickle.dump(lin,open('model.pkl','wb'))
'''
def custom_accuracy(y_test,y_pred,thresold):
	right = 0
    l = len(y_pred)
    for i in range(0,l):
        if(abs(y_pred[i]-y_test[i]) <= thresold):
            right += 1
    return ((right/l)*100)
 '''
def random_forest():
	dataset1=pd.read_csv("odi.csv")
	print(dataset1.head())
	X = dataset1.iloc[:,[7,8,9,12,13]].values
	y = dataset1.iloc[:, 14].values
	from sklearn.model_selection import train_test_split
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0)
	from sklearn.ensemble import RandomForestRegressor
	reg = RandomForestRegressor(n_estimators=100,max_features=None)
	reg.fit(X_train,y_train)
	pickle.dump(reg,open('random_forestmodel.pkl','wb'))


if __name__ == "__main__":
    linear()
    random_forest()
