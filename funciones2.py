import pandas as pd
import numpy as np
import re
import datetime

def transform_order_dates(df_order_dates):
    """
    En esta función vamos a limpiar el csv que contiene las orders que se han realizado 
    cada día. De esta forma devolvemos el mismo csv, eliminando los nans, corrigiendo 
    números mal introducidos y cambiando el formato de las fechas a datetime.
    """

    # vamos a transformar las fechas, quitando aquellas que den error
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

    return df_order_dates


def transform_order_details(df_order_details):
    """
    La siguiente función tranforma el csv de los detalles de cada order
    para ello sustituye caracteres mal introducidos en los nombres de las
    pizzas como (@ por a) y sustituye los nans de la cantidad de pizzas pedidas
    por la media (1). Con los nans restantes, elimina dichas filas.
    Por último, ordena el dataframe por order_id y resetea los index.
    """

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


def extraer_rango_orders_semana(df_order_dates):
    """
    creamos una función que devuelva una lista que contenga
    para cada semana su rango de orders. Es decir, las orders 
    están enumeradas por un identificador, el cual va en orden
    ascendente. Por lo que solo con el limite inferior y superior
    de cada semana podemos saber que orders corresponden a cada semana
    """
    orders_semanas = [[np.inf, -np.inf] for t in range(53)]

    # veo que dia de la semana es el 1 de enero de 2016, esto lo necesitamos
    # para la operacion que calcula que dia de la semana es una fecha determinada
    primer_dia_semana = pd.to_datetime("01-01-2016").dayofweek

    i = 0
    while i < len(df_order_dates):
        orders_semana = orders_semanas[(df_order_dates.loc[i, 'date'].day_of_year + primer_dia_semana) // 7]
        if (df_order_dates.loc[i, 'order_id']) > orders_semana[1]:
            orders_semana[1] = df_order_dates.loc[i, 'order_id']
        if (df_order_dates.loc[i, 'order_id']) < orders_semana[0]:
            orders_semana[0] = df_order_dates.loc[i, 'order_id']
        
        orders_semanas[(df_order_dates.loc[i, 'date'].day_of_year + primer_dia_semana) // 7] = orders_semana
        
        i +=1 

    return orders_semanas


def pizzas_por_semana(orders_semanas, df_order_details, pizzas_id):
    """
    Creamos una función que nos devuelva un df con el numero de 
    pizzas de cada tipo que se han pedido en cada semana
    Esta función recibe la lista que contiene los rangos de las orders
    por semana (orders_semanas), el df con los detalles de las orders para 
    cada semana (df_order_details) y una lista con todas las pizzas.
    """

    df_pizzas_semana = pd.DataFrame()               # creamos el dataframe
    datos = {}
    for i in range(53):                             # creamos los indices del dataframe
        datos[f'semana {i}'] = [0 for i in range(len(pizzas_id))] # inicializamos la cantidad de cada pizza en 0
    df_pizzas_semana = pd.DataFrame(datos, index=pizzas_id) 

    i = 0
    semana = 0                                      # empezamos en la semana 0
    while semana < len(orders_semanas) and i < len(df_order_details):
        # buscamos la primera order de la semana correspondiente
        while (i < len(df_order_details)) and (df_order_details.loc[i, 'order_id'] < orders_semanas[semana][0]):
            i += 1
        # en el momento que lo encontramos, empezamos a añadir las pizzas hasta
        # salir del rango de orders de esa semana
        while (i < len(df_order_details)) and (df_order_details.loc[i, 'order_id'] <= orders_semanas[semana][1]):
            pizza, cantidad = obtener_nombre_y_can_pizza(df_order_details.iloc[i])
            df_pizzas_semana.loc[pizza, f'semana {semana}'] += cantidad
            i += 1
        semana += 1           # hemos terminado, pasamos a la siguiente semana
    
    return df_pizzas_semana


def obtener_nombre_y_can_pizza(order):
    """
    Dado que en order details, además del id de pizza que se pide tenemos el tamaño
    de dicha pizza, y la cantidad de pizzas que se piden, vamos a crear una función
    que interprete para cada tamaño de pizza, cuantas pizzas se corresponden a un 
    tamaño de pizza "normal" y lo multiplique por la cantidad de dicha pizza.
    Esto nos servirá a la hora de calcular los ingredientes necesarios puesto que 
    no es lo mismo los ingredientes necesarios para una pizza xxl que una m.
    Como los tamaños van de s a xxl usaremos la siguiente correspondencia:
    s = 1, m = 1.5, l = 2, xl = 2.5, xxl = 3
    """
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
    """
    creamos una función que devuelva un diccionario con los
    ingredientes de cada pizza
    """
    dic = {}
    for i in range(len(df)):
        pizza = df.iloc[i]
        clave = pizza['pizza_type_id']
        ingredientes = pizza['ingredients'].strip().split(", ")
        dic[clave] = ingredientes
    return dic


def extraer_ingredientes_semanas(df_pizzas_semana, dic_ingredientes):
    """
    Esta función toma el dataframe de los ingredientes que se han ido
    necesitando para cada semana, y hace la media de cada ingrediente
    para todas las semanas. Después multiplica es media por 1.2, para
    así asegurarnos que no pueda haber escasez de ingredientes una 
    semana concreta.
    """

    # Creamos el dataframe que contendrá la cantidad necesaria de cada ingrediente
    # para cada semana

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
    """
    Finalmente, sabiendo la cantidad de ingredientes de cada tipo que hemos
    necesitado cada semana, podemos obtener la predicción. Para realizar dicha
    predicción, simplemente calculamos la media de cada ingrediente
    y multiplicamos dicha cantidad por 1.5, de esta forma evitamos que pueda 
    llegar a haber escasez de un determinado ingrediente una semana.
    """
    predicciones = df_ingredientes_semanas.mean()*1.5
    df_prediccion = pd.DataFrame(data=predicciones, columns=['cantidad'])
    return df_prediccion


def informe_calidad_datos(df, nombre):
    """
    Esta función nos permite obtener un informe de la calidad de los datos
    que tenemos en nuestro dataframe. Para ello, nos muestra el número de
    valores nulos que hay en cada columna, el número de valores únicos que
    hay en cada columna, y el tipo de dato que hay en cada columna.
    """
    dict = {}
    dict['nulos'] = df.isnull().sum()
    dict['unicos'] = df.nunique()
    dict['tipo'] = df.dtypes

    return dict