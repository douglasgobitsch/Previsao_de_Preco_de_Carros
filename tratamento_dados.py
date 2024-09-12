import pandas as pd

df = pd.read_csv('dataset_cars.csv')

df.fillna(0, inplace=True)

df.to_csv('dataset_cars_novo.csv', index=False)