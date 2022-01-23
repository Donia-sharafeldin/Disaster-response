import sys
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
from sqlalchemy import create_engine

def load_data(messages_filepath,categories_filepath):
    """
    Function to load messages and categories Data
    Input: messages and categories data file path
    Output: merged dataframe
    """
    categories = pd.read_csv(categories_filepath)
    messages = pd.read_csv(messages_filepath)
    df = messages.merge(categories,'outer', on = 'id')

    return df

def clean_data(df):
    """
    Function to clean merged data
    Input: Merged dataframe
    Output: Cleaned dataFrame
    """
    categories = df['categories'].str.split(';',expand = True)
    row = pd.Series(categories.iloc[0,:])

    cat_col=[]
    for x in row:
        x = x[:-2]
        cat_col.append(x)
    categories.columns = cat_col
    categories = categories.astype(str)
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    df.drop('categories',inplace =True,axis = 1)
    df = pd.concat([df,categories],axis =1)
    df.drop_duplicates(inplace = True)
    df = df[df['related'] != 2]

    return df



def save_data(df, database_filepath):
    """
    Function to save data into sql database
    Input: merged DataFrame and file path to save database
    Output: na
    """
    engine = create_engine('sqlite:///'+ database_filepath)
    df.to_sql('disaster', engine, index=False)  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()