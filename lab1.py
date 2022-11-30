import glob
import json
import numpy as np
import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression  
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt


dataset_path = './email_json_dataset1'


if __name__ == '__main__':
    print('Running')
    files = glob.glob(pathname='*.json', root_dir=dataset_path, recursive=False)
    jsons = []
    for file in files:
        filepath = dataset_path + '/' + file
        f = open(filepath,)
        jsons.append(json.load(f))
    dataframe = pd.DataFrame.from_records(jsons)
    print(dataframe.head())
    vectorizer = CountVectorizer(min_df=10)
    X = vectorizer.fit_transform(dataframe['body'].to_numpy())
    #print(vectorizer.get_feature_names_out())
    print('Size of the array', X.shape)
    df_bow_sklearn = pd.DataFrame(X.toarray(),columns=vectorizer.get_feature_names_out())
    #print(df_bow_sklearn.head())
    logreg = LogisticRegression(random_state = 0)  
    skf = StratifiedKFold(n_splits=3)
    y = dataframe['label'].to_numpy()
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1)
    #print(y_train)
    logreg.fit(X_train, y_train)
    prob = logreg.predict_proba(X_val)
    print(prob)
    y_pred_prob = prob[:,1]
    print(y_pred_prob)
    print(y_val)
    y_val[y_val=='ham'] = 0
    y_val[y_val=='spam'] = 1
    print(y_val)
    fpr, tpr, thresholds = roc_curve(y_val, y_pred_prob)
    plt.plot([0, 1], [0, 1], 'k--')
    print(tpr)
    print(fpr)
    plt.plot(fpr, tpr, label='Logisitc Regression')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Logistic Regression ROC Curve')
    plt.show()




