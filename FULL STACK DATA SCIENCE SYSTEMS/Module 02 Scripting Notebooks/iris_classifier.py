# IRIS Classifier

# import libraries
import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from sklearn.datasets import load_iris

# from get_data import get_data
# from clean_data import clean_data
# from train_model import train_model
# from evaluatee_model import evaluate_model
# from classify import classify

def get_data():
    iris = load_iris()
    print(iris.keys())
    return iris.data, iris.target

def clean_data(data):
    pass

def train_model(X, y):
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X, y)
    return knn

def evaluate_model():
    pass

def classify(model, sample):
    prediction = model.predict(sample)

    if prediction == 0:
        label = "Versicolor"
    return {
        "code": 200,
        "label": label
    }

def main():
    # get data
    X, y = get_data()
    print(X.shape, y.shape)

    # # clean data
    # cleaned_data = clean_data(data)

    # # training
    model = train_model(X, y)
    print(model)

    # # metric benchmarks
    # evaluation = evaluate_model()

    # # infer (predict)
    # # takes a sample of 4 features (s.w, s.l, p.w, p.l) and gets one of the 3 classes
    # # versicolor, sertosa, virginica
    sample = [1.5, 2.5, 1.8, 3.5] # versicolor
    sample = np.array(sample)
    print(type(sample), sample)
    prediction = classify(model, sample.reshape(1, -1))
    print(prediction)


if __name__ == "__main__":
    main()
