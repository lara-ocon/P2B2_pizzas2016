# pip install patool necesario instarlo
# import patoolib
# patoolib.extract_archive("orders_formatted.rar", outdir="path here")

import pandas as pd
import datetime
import re
import numpy as np

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


def extract_2(fichero):
    df = pd.read_csv(fichero, sep=",")
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
            df_order_dates.loc[i, 'date'] = pd.to_datetime(df_order_dates.loc[i, 'date'], dayfirst=True)
        except:
            fecha = datetime.datetime.fromtimestamp(float(df_order_dates.loc[i, 'date'])).date()
            # quiero que tenga el mismo formato
            df_order_dates.loc[i, 'date'] = pd.to_datetime(fecha)

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

    # ahora cambiamos los one/One por unos y quitamos los numeros negativos
    # tambien cambiamos @ por a , - por _, 0 por o, " " por _ y 3 por e
    for i in range(len(df_order_details)):
        pizza_id = df_order_details.loc[i, 'pizza_id']
        cantidad = df_order_details.loc[i, 'quantity']
        try:
            pizza_id = re.sub(" ", "_", pizza_id)
            pizza_id = re.sub("@", "a", pizza_id)
            pizza_id = re.sub("-", "_", pizza_id)
            pizza_id = re.sub("0", "o", pizza_id)
            pizza_id = re.sub("3", "e", pizza_id)
        except:
            # esto es el caso de que sean Nan
            ... 
        
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

    # cambiamos los Nans de cuantity por la media
    df_order_details['quantity'] = df_order_details['quantity'].fillna(value=int(df_order_details['quantity'].mean()))
    # quitamos todos los nans sobrantes (columna de pizzas)
    df_order_details = df_order_details.dropna()
    df_order_details.reset_index(inplace=True, drop=True)

    # ordenamos por order_id
    df_order_details = df_order_details.sort_values('order_id')
    # volvemos a poner los index
    df_order_details.reset_index(inplace=True, drop=True)

    return df_order_details

# debido a que se ha perdido informacion en ambos dataframe, es probable que haya orders de las cuales
# tengamos la fecha, pero no lo que se ha pedido en dicha order, y viceversa
# Dado que los order_id van en orden (con respecto al tiempo). Lo plantearemos igual que la anterior
# practica, es decir, guardaremos un rango de order_id para cada semana, (de esta forma si el order 3 no está
# en el dataframe pero si sabemos que en la primera semana la primera order fue la 1, y la ultima la 10 por ejemplo, 
# entonces sabremos que la 3 se realizó esa semana)

# Una vez guardemos el rango de orders de cada semana, iremos a ver los detalles de estas orders.
# POdrá ocurrir que no encontremos una order porque se hayan perdido su informacion, controlaremos esto
# con trys y excepts

def extraer_rango_orders_semana(df_order_dates):
    # buscamos el primer martes
    # el primer dia del dataframe es:

    orders_semanas = [[np.inf, -np.inf] for t in range(53)]

    # veo que dia de la semana es el 1 de enero de 2016
    primer_lunes = pd.to_datetime("01-01-2016").dayofweek

    
    # print(df_order_dates.loc[i, 'date'].day_of_year)
    
    i = 0
    while i < len(df_order_dates):
        orders_semana = orders_semanas[(df_order_dates.loc[i, 'date'].day_of_year + primer_lunes) // 7]
        if (df_order_dates.loc[i, 'order_id']) > orders_semana[1]:
            orders_semana[1] = df_order_dates.loc[i, 'order_id']
        if (df_order_dates.loc[i, 'order_id']) < orders_semana[0]:
            orders_semana[0] = df_order_dates.loc[i, 'order_id']
        
        orders_semanas[(df_order_dates.loc[i, 'date'].day_of_year + primer_lunes) // 7] = orders_semana
        
        i +=1 

    print(orders_semanas)
    return orders_semanas


def obtener_pizzas_semana(orders_semanas, df_order_details, pizzas_id):
    df_pizzas_semana = pd.DataFrame()
    datos = {}
    for i in range(53):
        datos[f'semana {i}'] = [0 for i in range(len(pizzas_id))]
    df_pizzas_semana = pd.DataFrame(datos, index=pizzas_id)

    i = 0
    semana = 0
    print("order details tiene una longitud de; ", len(df_order_details))
    while semana < len(orders_semanas) and i < len(df_order_details):
        # buscamos la primera order de la semana
        # puede haberse perdido este dato para esta order, 
        # le decimos que busque hasta que sea mayor o igual
        while df_order_details.loc[i, 'order_id'] < orders_semanas[semana][0]:
            i += 1
        # en el momento que lo encontramos, empezamos a añadir las pizzas hasta
        # salir del reango de orders de esa semana
        while df_order_details.loc[i, 'order_id'] <= orders_semanas[semana][1]:
            pizza, cantidad = obtener_nombre_y_can_pizza(df_order_details.iloc[i])
            df_pizzas_semana.loc[pizza, f'semana {semana}'] += cantidad
            i += 1
        semana += 1
        print("pasamos a la siguiente semana")
    
    return df_pizzas_semana



def obtener_nombre_y_can_pizza(order):
    # añado la pizza asociada a ese order
    pizza = order['pizza_id']
    tam = 3
    # vemos su tamaño
    if re.search("_s$", pizza):
        pizza = re.sub("_s$","", pizza)
        tam = 1
    elif re.search("_m$", pizza):
        pizza = re.sub("_m$","", pizza)
        tam = 1.5
    elif re.search("_l$", pizza):
        pizza = re.sub("_l$","", pizza)
        tam = 2
    elif re.search("_xl$", pizza):
        pizza = re.sub("_xl$","", pizza)
        tam = 2.5
    elif re.search("_xxl$", pizza):
        pizza = re.sub("_xxl$","", pizza)
        tam = 3
    
    cantidad = order['quantity']
    
    return pizza, cantidad*tam


def extraer_ingredientes(df):
    dic = {}
    for i in range(len(df)):
        pizza = df.iloc[i]
        clave = pizza['pizza_type_id']
        ingredientes = pizza['ingredients'].strip().split(", ")
        dic[clave] = ingredientes
    return dic


def extraer_ingredientes_semanas(df_ingredientes_semanas, df_pizzas_semana, dic_ingredientes):
    for pizza in df_pizzas_semana.index:
        
        ingredientes = dic_ingredientes[pizza]

        for j in range(len(df_ingredientes_semanas)):
            # voy recorriendo las filas del df de ingredientes (semanas) y obtengo cuantas pizzas
            # de ese tipo se hacen cada semana
            num = df_pizzas_semana.loc[pizza, f"semana {j}"]
            # añado el numero a cada ingrediente
            for ingrediente in ingredientes:
                df_ingredientes_semanas.loc[f"semana {j}", ingrediente] += num
            
    return df_ingredientes_semanas


def obtener_prediccion_ingredientes(df_ingredientes_semanas):
    # df_ingredientes_semanas.append(pd.Series([df_ingredientes_semanas.mean()*1,5]), ignore_index=True)
    predicciones = df_ingredientes_semanas.mean()*1.5
    df_prediccion = pd.DataFrame(data=predicciones, columns=['cantidad'])
    return df_prediccion


# LOAD ============================================================#
def cargar_predicciones(df_prediccion):
    # pasamos el dataframe a un csv
    df_prediccion.to_csv("predicciones.csv")


if __name__ == "__main__":

    df_order_dates = extract("orders.csv")
    df_order_details = extract("order_details.csv")
    df_order_dates = transform_order_dates(df_order_dates)
    df_order_details = transform_order_details(df_order_details)

    df_pizza_types = extract_2('pizza_types.csv')
    print(df_pizza_types)

    pizzas_id = list(df_pizza_types['pizza_type_id'])

    print(df_order_dates.iloc[60:100])
    print(df_order_details.head(40))

    orders_semanas = extraer_rango_orders_semana(df_order_dates)
    print(df_order_dates.head(80))

    df_pizzas_semana = obtener_pizzas_semana(orders_semanas, df_order_details, pizzas_id)
    print(df_pizzas_semana)

    # obtenemos un diccionario con para cada pizza sus ingredientes
    dic_ingredientes = extraer_ingredientes(df_pizza_types)

    # creamos un dataframe para los ingredientes de cada semana ======================#
    total_ingredientes = []
    datos = {}
    for ingredientes in  list(dic_ingredientes.values()) :
        for ingrediente in ingredientes:
            if ingrediente not in total_ingredientes:
                total_ingredientes.append(ingrediente)
                datos[ingrediente] = [0 for i in range(53)]
    
    semanas = [f"semana {i}" for i in range(53)]

    # ahora creamos un dataframe con los ingredientes de cada semana
    df_ingredientes_semanas = pd.DataFrame(datos, index=semanas)
    # =================================================================================#

    # completamos ese dataframe sabiendo las pizzas que se piden cada semana y con el diccionario
    # de ingredientes para cada pizza
    df_ingredientes_semanas = extraer_ingredientes_semanas(df_ingredientes_semanas, df_pizzas_semana, dic_ingredientes)
    print(df_ingredientes_semanas)


    # obtengo la media de los ingredientes y multiplico por 1.5 para tener de mas
    df_prediccion = obtener_prediccion_ingredientes(df_ingredientes_semanas)

    # Cargamos los datos en un csv =====================================================#
    cargar_predicciones(df_prediccion)





