import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

dataset = pd.read_csv('Restaurant_Reviews.tsv', delimiter='\t', quoting=3)

import re
import nltk

nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

corpus = []

for i in range(0, 1000):
    review = re.sub('[^a-zA-Z]', ' ', dataset['Review'][i])
    review = review.lower()
    review = review.split()
    ps = PorterStemmer()
    all_stopwords = stopwords.words('english')
    all_stopwords.remove('not')
    all_stopwords.remove('no')
    all_stopwords.remove('but')
    all_stopwords.remove("won't")
    review = [ps.stem(word) for word in review if word not in set(all_stopwords)]
    review = ' '.join(review)
    corpus.append(review)

from sklearn.feature_extraction.text import CountVectorizer
import joblib

cv = CountVectorizer(max_features=1500)

X = cv.fit_transform(corpus).toarray()

# Extract the target variable from the dataset
y = dataset.iloc[:, -1].values

# Saving the vectorizer
joblib.dump(cv, 'vectorizer_reviews.joblib')

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

models = [
    ('Logistic Regression', LogisticRegression(C=1.)),
    ('Naive Bayes', MultinomialNB()),
    ('Support Vector Machine', SVC(C=1., kernel='rbf')),
    ('Random Forest', RandomForestClassifier())
]

for model_name, model in models:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'{model_name} accuracy: {accuracy}')

best_model = models[0][1]
best_accuracy = 0

for model_name, model in models:
    accuracy_scores = cross_val_score(model, X_train, y_train, cv=10)
    mean_accuracy = np.mean(accuracy_scores)
    if mean_accuracy > best_accuracy:
        best_accuracy = mean_accuracy
        best_model = model_name

print(f'Best model: {best_model}')
print(f'Accuracy with k-fold cross-validation: {best_accuracy}')

# choosing logistic regression as the best model
classifier = LogisticRegression(C = 1.0)
classifier.fit(X_train, y_train)

import joblib

# Save the trained model to a file
joblib.dump(classifier, 'logistic_regression_NLPreviews.joblib')

# Load the saved model from a file
import joblib
loaded_model = joblib.load('logistic_regression_NLPreviews.joblib')
loaded_vectorizer = joblib.load('vectorizer_reviews.joblib')

new_review = loaded_vectorizer.transform(['The food could have been better.'])
predictions = loaded_model.predict(new_review)

if predictions == 0:
    print('negative sentiment')
else:
    print('positive sentiment')
