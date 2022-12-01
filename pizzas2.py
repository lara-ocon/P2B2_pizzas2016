# Práctica 2 Bloque 2 - Adquisición de datos - IMAT
# Autor: Lara Ocón Madrid

# Predicción ingredientes de la semana con limipieza de datos de la 
# Pizzería "Maven Pizzas"

"""
En esta práctica vamos a tomar los datos de la pizzería Maven Pizzas y calcular 
para cada semana del año la cantidad de cada ingrediente que se ha necesitado. 

Una vez obtenida la cantidad de cada ingrediente para cada semana, calcularemos la 
media de cada uno de ellos y multiplicaremos dicha media por 1.2 (valor que he 
decidido tomar para que no haya falta de ingredientes una semana).

Es decir, emplearemos una ETL, extrayendo los datos, transfromándolos para quedarnos 
con lo que necesitamos cada semana, y cargando dicha predicción en un csv.

A diferencia de la práctica anterior, en esta práctica debemos controlar que los 
datos estén "limpios". Por ello a la hora de trasnfromar los datos tendremos que 
eliminar Nans, arreglar nombres/números mal introducidos, cambiar caracteres en 
determinados dataframes por otros (por ejemplo: @ por a, 3 por e...)

En resumen, estos son las reglas que vamos a aplicar para limpiar los datos:
1) en la columna quantity de order_details:
    - quitar las celdas vacías
    - cambiar los números ngeativos por su valor absoluto
    - cambiar los números introducidos alfabeticamente por su número (por ejemplo: one = 1)
    
2) en la columna pizza_id de order_details:
    - cambiar - por _
    - cambiar @ por a
    - cambiar 0 por o
    - cambiar " " por _
    - cambiar 3 por e

3) en la columna date de orders
    - quitar los nan/None
    - transformar fechas a formato datetime
    - quitar las que no son fechas o transformar las fechas introducidad en otro tipo de formato
"""

# importamos las librerias necesarias
import pandas as pd
import funciones2 as f2


# Funciones de extracción de datos =============================================
def extract(fichero):
    df = pd.read_csv(fichero, sep=";")
    return df

def extract_2(fichero):
    # Creamos una segunda función para leer los csv cuyos separadores
    # sean comas (order_details.csv y orders.csv) 
    df = pd.read_csv(fichero, sep=",")
    return df


# Funciones de transformación de datos ==========================================
def transform(df_pizza_types, df_order_dates, df_order_details):
    """
    En esta función vamos a transformar los datos de los distintos csvs de las pizzas,
    para obtener la cantidad de cada ingrediente que se ha utilizado cada semana del 
    año y a partir de esa cantidad calcular la predicción de cada ingrediente para una
    semana cualquiera.
    """
    # En primer lugar, nos guardamos los nombres de las pizzas y un 
    # diccionario que guarde los ingredientes necesarios para cada pizza:
    pizzas_id = list(df_pizza_types['pizza_type_id'])
    dic_ingredientes = f2.extraer_ingredientes(df_pizza_types)

    # Después, transformamos las fechas del csv de order_dates. Esta función además
    # de convertir las fechas a tipo pandas datetime, limpia los datos del df
    print("\n"+"\033[1;32m"+"Limpiando datos de los dataframes ..."+"\033[0;m"+"\n")
    df_order_dates = f2.transform_order_dates(df_order_dates)

    # Antes de obtener la información de los orders por semana, limpiamos el df de
    # orders_details
    df_order_details = f2.transform_order_details(df_order_details)

    # Ahora obtenemos el rango de orders que corresponden a cada semana
    print("\n"+"\033[1;34m"+"Obteniendo identificadores de pedidos para cada semana..."+"\033[0;m"+"\n")
    orders_semanas = f2.extraer_rango_orders_semana(df_order_dates)

    # Ahora obtenemos la información de los orders por semana, obteniendo un dataframe
    # con la cantidad de cada tipo de pizza que se ha pedido cada semana
    print("\n"+"\033[1;35m"+"Obteniendo información acerca de los pedidos ..."+"\033[0;m"+"\n")
    df_pizzas_semana = f2.pizzas_por_semana(orders_semanas, df_order_details, pizzas_id)

    # Calculamos los ingredientes que han sido necesarios cada semana
    print("\n"+"\033[1;36m"+"Calculando predicción ..."+"\033[0;m"+"\n")
    df_ingredientes_semanas = f2.extraer_ingredientes_semanas(df_pizzas_semana, dic_ingredientes)

    # Finalmente hacemos la predicción de la siguiente forma:
    # Calculamos la media de cada ingrediente por semana y la multiplicamos por 1.2
    df_prediccion = f2.obtener_prediccion_ingredientes(df_ingredientes_semanas)

    return df_prediccion
    

# Funciones de carga de datos ==================================================

def cargar_predicciones(df_prediccion):
    """
    Finalmente, solo nos queda pasar el dataframe de la prediccion, a un csv.
    """
    df_prediccion.to_csv("predicciones.csv")
    print("\n"+"\033[1;32m"+"Predicción cargada en un csv !!!"+"\033[0;m"+"\n")


if __name__ == "__main__":

    # 1) cargamos los datos:
    df_order_dates = extract("orders.csv")
    df_order_details = extract("order_details.csv")
    df_pizza_types = extract_2('pizza_types.csv')

    # 2) Transformamos los datos
    df_prediccion = transform(df_pizza_types, df_order_dates, df_order_details)

    # 3) Guardamos los datos
    cargar_predicciones(df_prediccion)

    