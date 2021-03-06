import sys,pickle
from nltk.stem import WordNetLemmatizer
import nltk
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('stopwords')
nltk.download('omw-1.4')
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, GridSearchCV
from nltk.corpus import stopwords
from sqlalchemy import create_engine
import pandas as pd
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score



def load_data(database_filepath):
    """
    Function to load DataBase from file path to get X,y and categories
    Input: data base file path
    OutPut: returns X features , y target and categories 
    """
    engine = create_engine(f'sqlite:///'+database_filepath)
    df = pd.read_sql_table("disaster", engine)
    X = df['message']
    y = df.drop(['message','original',"id",'genre'],axis =1)
    category_names = y.columns
    return X,y,category_names


def tokenize(text):
    """
    Function to tokenize messages
    Input: messages (text)
    Output: Cleaned lemmatized messages
    """
    words = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    lem = []
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if w not in stop_words]
    for w in words:
        word = lemmatizer.lemmatize(w).lower().strip() 
        lem.append(word)
    return lem

def build_model():
    """
    Function to build amodel , create grid search pipeline
    Input: N/A
    Output: the model
    """
    pipeline = Pipeline([('vect', CountVectorizer(tokenizer=tokenize)),
                ('tfidf', TfidfTransformer()),
                   ('clf', MultiOutputClassifier(KNeighborsClassifier()))])
    
    parameters = {'clf__estimator__n_neighbors':[6,7,8]
             }
    cv =  GridSearchCV(estimator = pipeline,param_grid = parameters)
    return cv

def evaluate_model(model, X_test, Y_test, category_names):
    y_pred = model.predict(X_test)
    print('Accuracy Score: {}'.format(np.mean(Y_test.values == y_pred)))


def save_model(model, model_filepath):
    pickle.dump(model, open(model_filepath, 'wb'))



def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()