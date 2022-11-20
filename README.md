# Practica2_bloque2
Practica 2 del bloque 2, predicción de ingredientes necesarios para la semana con limpieza de datos.

El objetivo de esta Práctica es extraer los datos de la Pizzería Maven Pizzas de 2016, y transformarlos para así
cargar una predicción de la cantidad de ingredientes que necesitaría la pizzería cada semana.

A diferencia de la práctica anterior, esta práctica contenía datos erróneos, vacíos o mal introducidos, por lo que a la hora de transformar, hemos tenido que implementar una limpieza de datos para corregir esa información.

Para obtener esta predicción hemos cargado primero todos los csv en dataframe para poder trabajar con ellos con la librería pandas.

Antes de comenzar a trabajar con dichos datos hemos realizado una limpieza sobre ellos, eliminando los Nans en algunas columnas, o cambiándolos por la media en otros. También, hemos cambiado algunos datos como por ejemplo: numeros negativos por su valor absoluto, numeros introducidos alfabeticamente por su valor numerico correspondiente, caracteres erroneos en palabras como @, 3... (los hemos cambiado por a y e respectivamente)...

Una vez hecho esto, procedemos a analizar los datos de la misma forma que en la práctica anterior.

En primer lugar, hemos obtenido una lista que contiene el rango de orders de cada semana. Es decir, las orders estan enumeradas con un identificador, y dado que este va en orden ascendente, con saber la primera order que se hace una semana y la última nos es suficiente para aglomerar todos los pedidos que se hacen una semana determinada.

Sabiendo esto y accediendo a la información de order_details.csv, podemos ver a través del order_id las pizzas (y el tamaño de dichas pizzas) que se piden en cada order. De esta forma, podemos ver cuantas pizzas de cada tipo se piden cada semana. Dado que los tamaños de pizza van de S a XXL, he considerado como tamaño normal la S, y para el resto de tamaños he considerado la siguiente correspondencia: s = 1, m = 1.5, l = 2, xl = 2.5, xxl = 3. Esto lo he hecho dado que no es lo mismo la cantidad de ingredientes que se necesitan para una pizza de tamaño s, que para una pizza de tamaño XXL.

Sabiendo ya aproximadamente cuantas pizzas de tamaño "estándar" se necesitan cada semana. Creamos un dataframe que contenga los ingredientes, y la cantidad necesaria de cada ingrediente para cada semana. Para ello, multiplicamos la cantidad pedida de cada pizza por sus ingredientes, y se los sumamos a su fila correspondiente.

Una vez ya sabemos la cantidad de cada tipo de ingrediente que se ha necesitado cada semana, solo nos queda calcular la predicción. Para ello, tomamos la media para cada tipo de ingrediente y multiplicamos por 1.5 (esto es para evitar que pueda haber escasez de algun ingrdiente). Finalmente, cargamos dicha predicción en "predicciones.csv".
