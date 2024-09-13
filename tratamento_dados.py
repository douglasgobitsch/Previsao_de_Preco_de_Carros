import dask.dataframe as dd
# Ler o CSV forçando todas as colunas como string
df = dd.read_csv('Automotive.csv', dtype=str, low_memory=False)

# Definir colunas a serem convertidas
colunas_float = ['msrp', 'askPrice', 'vf_BasePrice']  # Coloque os nomes das colunas que devem ser float
#colunas_int = ['', '']  # Coloque os nomes das colunas que devem ser int
colunas_data = ['firstSeen', 'lastSeen', 'vf_ModelYear']  # Coloque os nomes das colunas que devem ser convertidas para datetime

# Preencher valores nulos para colunas que serão convertidas
for col in colunas_float + colunas_data:
    df[col] = df[col].fillna('')  # Preencher valores nulos com string vazia

# Converter para float
for col in colunas_float:
    df[col] = dd.to_numeric(df[col], errors='coerce')  # Convertendo para float, forçando erros para NaN

# Converter para datetime
for col in colunas_data:
    df[col] = dd.to_datetime(df[col], errors='coerce')  # Convertendo para datetime, forçando erros para NaT (Not a Time)

# Colunas que serão mantidas
colunas_desejadas = ['msrp', 'askPrice', 'vf_BasePrice', 'firstSeen', 'lastSeen', 'vf_ModelYear', 'color', 'brandName', 'modelName', 'vf_BodyClass', 'vf_FuelTypePrimary', 'vf_Series', 'vf_TransmissionStyle']
df_selecionado = df[colunas_desejadas]

# Salvar o novo CSV com apenas as colunas selecionadas
df_selecionado.to_csv('dataset_cars_selecionado.csv', single_file=True, index=False)
