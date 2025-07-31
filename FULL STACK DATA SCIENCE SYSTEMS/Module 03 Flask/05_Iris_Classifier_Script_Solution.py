import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

import joblib

def classify(model, sample):
    class_label = model.predict(sample)
    return {
        'code': 200,
        'message': f'Sample is classified as {class_label[0]}',
        'class': class_label[0]
    }

def train():
    df = pd.read_csv("Iris.csv")
    X=df[['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']]
    y=df[['Species']]

    X_train,X_test,y_train,y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=0
    )


    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train,y_train)

    model_filename = 'My_KNN_model.sav'
    joblib.dump(knn, model_filename)

    model = joblib.load(model_filename)
    predict1 = model.predict(X_test)
    
    print("The accuracy of the KNN Classifier is: ",metrics.accuracy_score(predict1, y_test))
    return knn

def main():
    model = train()
    data = {'SepalLengthCm': [5.8],
            'SepalWidthCm': [2.8],
            'PetalLengthCm': [5.1],
            'PetalWidthCm': [2.4]
    }

    test_sample = pd.DataFrame(data, columns=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
    prediction = classify(model, test_sample)
    print(prediction)
    

if __name__ == "__main__":
    main()