import dask.dataframe as dd
# Ler o CSV forçando todas as colunas como string
df = dd.read_csv('dataset_cars.csv', dtype=str,  low_memory=False)


# Definir colunas a serem convertidas
colunas_float = ['msrp', 'askPrice', 'vf_BasePrice']  # Coloque os nomes das colunas que devem ser float
colunas_int = ['vf_ModelYear']  # Coloque os nomes das colunas que devem ser int
colunas_data = ['firstSeen', 'lastSeen']  # Coloque os nomes das colunas que devem ser convertidas para datetime

# Preencher valores nulos para colunas que serão convertidas
for col in colunas_float + colunas_data + colunas_int:
    df[col] = df[col].fillna('')  # Preencher valores nulos com string vazia

# Converter para float
for col in colunas_float:
    df[col] = dd.to_numeric(df[col], errors='coerce')  # Convertendo para float, forçando erros para NaN

# Converter para int
for col in colunas_int:
    df[col] = dd.to_numeric(df[col], errors='coerce')  # Convertendo para int, forçando erros para NaN

# Converter para datetime
for col in colunas_data:
    df[col] = dd.to_datetime(df[col], errors='coerce')  # Convertendo para datetime, forçando erros para NaT (Not a Time)

# Dividir os dados por ano
anos = df['vf_ModelYear'].dropna().unique().compute()  # Obter anos únicos

for ano in anos:
    df_ano = df[df['vf_ModelYear'] == ano]

# Colunas que serão mantidas
colunas_desejadas = ['msrp', 'askPrice', 'vf_BasePrice', 'firstSeen', 'lastSeen', 'vf_ModelYear', 'color', 'brandName', 'modelName', 'vf_BodyClass', 'vf_FuelTypePrimary', 'vf_Series', 'vf_TransmissionStyle']
df_selecionado = df[colunas_desejadas]

# Salvar o novo CSV com apenas as colunas selecionadas
df_selecionado.to_csv('dataset_cars_novo.csv', single_file=True, index=False)
