import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

import joblib 

from flask import Flask, jsonify


@app.route('/')
def home():
    return "<h1>Welcome to Iris Classifier. Use '/classify' route to classify an iris sample. </h1>"

@app.route("/classify")
def classify():
    
    return {
        'code': 200,
        'message': f'Sample is classified as {class_label[0]}',
        'class': class_label[0]
    }

if __name__ == "__main__":
    app.run()