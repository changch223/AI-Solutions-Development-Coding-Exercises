import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

import joblib 

from flask import Flask, jsonify
app = Flask(__name__)

model_filename = "My_KNN_model.sav"
model = joblib.load(model_filename)

@app.route('/')
def home():
    return "<h1>Welcome to Iris Classifier. Use '/classify' route to classify an iris sample. </h1>"

@app.route("/classify")
def classify():
    data = {'SepalLengthCm': [1.3],
            'SepalWidthCm': [3.5],
            'PetalLengthCm': [5.1],
            'PetalWidthCm': [3.5]
    }

    sample = pd.DataFrame(data, columns=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
    class_label = model.predict(sample)

    return {
        'code': 200,
        'message': f'Sample is classified as {class_label[0]}',
        'class': class_label[0]
    }

if __name__ == "__main__":
    app.run()