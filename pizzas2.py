# pip install patool necesario instarlo
# import patoolib
# patoolib.extract_archive("orders_formatted.rar", outdir="path here")

import pandas as pd
import datetime
import re

# para esta entrega, tenemos que limpiar lo siguiente:

# 1) en la columna quantity de order_details:
    # corregir huecos en blanco
    # quitar los -1
    # cambiar one o One por 1
# 2) en la columna pizza_id de order_details:
    # cambiar - por _
    # cambiar @ por a
    # cambiar 0 por o
    # cambiar " " por _
    # cambiar 3 por e

# 3) en la columna date de orders
    # quitar los nan/None
    # transformar fechas a pd.datetime
    # quitar/cambiar las que no son fechas (que den error)

# en orders no tengo en cuenta las horas

def extract(fichero):
    df = pd.read_csv(fichero, sep=";")
    return df

def transform_order_dates(df_order_dates):

    # vamos a contar cuantos nan y null por columna hay
    # vamos tambien a ver el tipo por columna
    print("Tipos de variables por columnas = \n", df_order_dates.dtypes)
    print("Numero de NaN por columnas = \n", df_order_dates.isna().sum()) # isnull tambien vale
    # con : df.isnull().sum(axis=1) vemos nulls por filas, axis=0 nulls por columnas

    # quitamos la columna de horas pues no nos interesa:
    df_order_dates = df_order_dates.drop(['time'], axis=1)

    # ahora vamos a transformar las fechas, quitando aquellas que den error
    for i in range(len(df_order_dates)):
        try:
            df_order_dates.loc[i, 'date'] = pd.to_datetime(df_order_dates.loc[i, 'date'])
        except:
            df_order_dates.loc[i, 'date'] = datetime.datetime.fromtimestamp(float(df_order_dates.loc[i, 'date'])).date()
            # df_order_dates.loc[i, 'date'] = pd.to_datetime(df_order_dates.loc[i, 'date'], unit = 'ms', origin=pd.Timestamp('2015-01-01')) # pasar a timestamps

    # Quitamos los nans
    df_order_dates = df_order_dates.dropna()

    # vamos a ordenar el dataframe por order_id
    df_order_dates = df_order_dates.sort_values('order_id')

    # reseteamos los index
    df_order_dates.reset_index(inplace=True, drop=True)
    print(df_order_dates.head(40))

    return df_order_dates


def transform_order_details(df_order_details):
    # vamos a contar cuantos nan y null por columna hay
    # vamos tambien a ver el tipo por columna
    print("\nTipos de variables por columnas = ", df_order_details.dtypes)
    print("\nNumero de NaN por columnas = ", df_order_details.isna().sum()) # isnull tambien vale
    # con : df.isnull().sum(axis=1) vemos nulls por filas, axis=0 nulls por columnas

    # quitamos los nans
    df_order_details = df_order_details.dropna()
    df_order_details.reset_index(inplace=True, drop=True)



    # ahora cambiamos los one/One por unos y quitamos los numeros negativos
    # tambien cambiamos @ por a , - por _, 0 por o, " " por _ y 3 por e
    for i in range(len(df_order_details)):
        pizza_id = df_order_details.loc[i, 'pizza_id']
        cantidad = df_order_details.loc[i, 'quantity']
    
        pizza_id = re.sub(" ", "_", pizza_id)
        pizza_id = re.sub("@", "a", pizza_id)
        pizza_id = re.sub("-", "_", pizza_id)
        pizza_id = re.sub("0", "o", pizza_id)
        pizza_id = re.sub("3", "e", pizza_id)
        
        try:
            cantidad = int(cantidad)
            if cantidad < 0:
                cantidad = -cantidad
                # ponemos las cantidades en positivo
                #eliminar_filas = eliminar_filas.append(i)
        except:
            if cantidad in ["one", "One"]:
                cantidad = 1
            elif cantidad in ["two", "Two"]:
                cantidad = 2
            
        df_order_details.loc[i, 'pizza_id'] = pizza_id
        df_order_details.loc[i, 'quantity'] = cantidad

    # ordenamos por order_id
    df_order_details = df_order_details.sort_values('order_id')
    # volvemos a poner los index
    df_order_details.reset_index(inplace=True, drop=True)
    print(df_order_details.head(20))
    return df_order_details



    
        




    






if __name__ == "__main__":

    df_order_dates = extract("orders.csv")
    df_order_details = extract("order_details.csv")
    df_order_dates = transform_order_dates(df_order_dates)
    df_order_details = transform_order_details(df_order_details)
