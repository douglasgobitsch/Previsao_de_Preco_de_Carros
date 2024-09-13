import dask.dataframe as dd

# Ler o CSV forçando todas as colunas como string
df = dd.read_csv('dataset_cars.csv', dtype=str, low_memory=False)

# Definir colunas a serem convertidas
#colunas_float = ['coluna_x', 'coluna_y']  # Coloque os nomes das colunas que devem ser float
#colunas_int = ['coluna_z']  # Coloque os nomes das colunas que devem ser int

# Preencher valores nulos para colunas que serão convertidas
#for col in colunas_float + colunas_int:
#    df[col] = df[col].fillna('')  # Preencher valores nulos com string vazia

# Converter para float e int
#for col in colunas_float:
#    df[col] = df[col].astype(float, errors='coerce')  # Convertendo para float, forçando erros para NaN

#for col in colunas_int:
#    df[col] = df[col].astype(float, errors='coerce')  # Primeiro converter para float para lidar com valores nulos
#    df[col] = df[col].fillna(0).astype(int)  # Preencher NaN com 0 e converter para int

# Salvar o novo CSV
df.to_csv('dataset_cars_novo.csv', single_file=True, index=False)
