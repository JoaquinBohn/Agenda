'''
El siguiente programa modela y administra una base de datos de una agenda telefonica basica. Ocupa SQLite como para la gestión de la base de datos y la libreria sqlite3 como interfaz para la misma. La agenda cuenta con la implementacion de un CRUD basico. Al momento de ejecutar el programa por primera vez se creara una base de datos con el nombre de agenda en el directorio raiz del usuario.
Para un mejor funcionamiento se recomienda agregar algunos contactos al comenzar para poder hacer uso de las demas funciones.
'''


import sqlite3 as sql

#nombre que se aginara a la base de datos
AGENDA = "agenda.db"

#Funcion principal de la agenda
def main():
    """Funcion principal de la agenda. Organiza los pasos necesarios para el funcionamiento de la agenda y la correcta conexion con la base de datos."""
    connection = conectar_db(AGENDA)
    crear_tabla(connection)
    cursor = connection.cursor()

    print("Bienvenido a su agenda virtual.")

    reproducir_menu_principal(connection, cursor)

    cerrar_db(connection)


#---------------------------------------------------------------


#Seccion de conexion con la base de datos
def conectar_db(base):
    """Dado un nombre de base de datos, conecta con la base
    y devuelve el objeto connection."""
    try:
        connection = sql.connect(base)
        return connection
    except:
        print("Ocurrió un error al intentar abrir la base de datos.")

def cerrar_db(connection):
    """Recibe un objeto connection y cierra la base de datos."""
    connection.close()

def crear_tabla(connection):
    """Recibe un objeto connection de una base de datos.
    Crea la tabla 'contactos' si no existe, con los campos:
    -id
    -nombre
    -telefono
    """
    cursor = connection.cursor()
    instruccion = "CREATE TABLE IF NOT EXISTS contactos (id INTEGER PRIMARY KEY     AUTOINCREMENT, nombre TEXT NOT NULL, numero INTEGER NOT NULL)"
    cursor.execute(instruccion)
    connection.commit()

#---------------------------------------------------------------

#Seccion de menus
def menu_principal():
    """Despliega el menu principal de la agenda:
    1-Agregar contacto
    2-Buscar contacto
    3-Salir
    """

    print("\n")
    print("Menu:")
    print("1-Ver contactos")
    print("2-Buscar contacto")
    print("3-Agregar nuevo contacto")
    print("4-Eliminar contacto")
    print("5-Editar contacto")
    print("6-Salir")

    opcion = input("Qué acción desea realizar?: ")
    return opcion


def reproducir_menu_principal(connection, cursor):
    """Ejecuta el menu principal hasta que se elija una opcion valida.
    Llama a la función que corresponde a la opcion elegida."""
    opcion = menu_principal()
    posibles_opciones = ["1", "2", "3", "4", "5", "6"]
    while opcion not in posibles_opciones:
        print("Elija una opcion válida.")
        opcion = menu_principal()
    if opcion=='1':
        imprimir_contactos(cursor)
    elif opcion=='2':
        buscar_contacto(cursor, "")
    elif opcion=='3':
        agregar_contacto(connection, cursor)
    elif opcion=='4':
        eliminar_contacto(connection, cursor)
    elif opcion=='5':
        editar_contacto(connection, cursor)
    else:
        return salir()
    reproducir_menu_principal(connection, cursor)

#---------------------------------------------------------------

#Seccion de CRUD
def imprimir_contactos(cursor):
    """Recibe el objeto cursor, solicita todos los registros de la base de datos y los imprime por pantalla."""

    instruccion = "SELECT nombre, numero FROM contactos ORDER BY nombre"
    contactos = cursor.execute(instruccion)

    print("\n")
    for contacto in contactos:
        print(contacto[0]+": "+str(contacto[1]))


def buscar_contacto(cursor, nombre):
    """Recibe el objeto cursor y un nombre, solicita todos los registros de la base de datos que coincidan con dicho nombre, luego los imprime por pantalla.
    Devuele un valor booleano que indica si se encontraron registros o no."""

    if(not nombre):
        nombre = input("Buscar: ")

    instruccion = 'SELECT * FROM contactos WHERE contactos.nombre LIKE "{}"'.format(nombre)

    try:
        contactos = cursor.execute(instruccion).fetchall()

        if(len(contactos)==0):
            print("No se han encontrado contactos con ese nombre.")
            return False
        print("\n")
        for contacto in contactos:
            print("id: "+str(contacto[0])+"-"+contacto[1]+": "+str(contacto[2]))
            return True
    except:
        print("No se ha encontrado ningun contacto")


def agregar_contacto(connection, cursor):
    """Crea y agrega un nuevo contacto en la base de datos. En caso de ingresar un numero ya existente en la db, fallara y volvera al menu principal."""
    datos = confirmar_datos()

    instruccion = ('INSERT INTO contactos(nombre, numero) VALUES("{}", "{}")'.format(datos[0], datos[1]))

    try:
        cursor.execute(instruccion)

        print("Contacto agregado.")

        connection.commit()
    except:
        print("Ocurrió un error al intentar crear el nuevo contacto. Puede deberse a que ya existe un contacto con el mismo numero.")


def eliminar_contacto(connection, cursor):
    """Recibe los objetos connection y cursor. Obtiene el contacto a eliminar, una vez que el usuario confirma su eliminacion se procede a borrar el registro de la db que coincida con el id ingresado. En caso de no obtener ningun contacto termina y vuelve al menu principal. """

    contacto = obtener_contacto_por_id(connection, cursor, "eliminar")

    if(not contacto):
        return

    id = contacto[0]
    nombre = contacto[1]
    numero = contacto[2]

    print('Se eliminará el siguiente contacto: {}-{}: {}'.format(id, nombre, numero))
    confirmacion = not bool(input("Presione Enter para confirmar, si desea cancelar presione la tecla n y luego Enter:  "))

    if(confirmacion):
        instruccion = 'DELETE FROM contactos WHERE id="{}"'.format(id)
        cursor.execute(instruccion)
        connection.commit()
        print("Contacto eliminado.")
    else:
        print("Operacion cancelada.")


def editar_contacto(connection, cursor):
    """Recibe los objetos connection y cursor. Si se obtiene un contacto pide confirmacion al usuario y llama a la funcion encargada de realizar las modificaciones en la db. En caso de no obtener un contacto vuelve al menu principal."""
    contacto = obtener_contacto_por_id(connection, cursor, "editar")

    if(not contacto):
        return

    id = contacto[0]
    nombre = contacto[1]
    numero = contacto[2]

    print('Se modificará el siguiente contacto: {}-{}: {}'.format(id, nombre, numero))
    confirmacion = not bool(input("Presione Enter para confirmar, si desea cancelar presione la tecla n y luego Enter:  "))

    if(confirmacion):
        dato_a_modificar = validar_opcion_dato_a_modificar()
        modificar(connection, cursor, dato_a_modificar, id)
        print("Contacto editado.")
    else:
        print("Operacion cancelada.")


def modificar(connection, cursor, opcion, id):
    """Recibe los objetos connection y cursor, una opcion (nombre o numero), y el id del contacto a modificar. Actualiza los datos del registro por los nuevos ingresados por el usuario."""
    dato = input('Ingrese el nuevo {}: '.format(opcion))

    if(opcion == "numero"):
        validar_numero(dato)

    while(not dato):
        dato = input('Debe ingresar un {}: '.format(opcion))

        if(opcion == "numero"):
            validar_numero(dato)

    instruccion = 'UPDATE contactos SET {}="{}" WHERE id="{}"'.format(opcion, dato, id)
    cursor.execute(instruccion)
    connection.commit()

#---------------------------------------------------------------


#Seccion de funciones auxiliares
def confirmar_datos():
    """Pide confirmacion al usuario para continuar con el proceso de agregar un nuevo contacto. Una vez que los datos son validos y se tiene la confirmacion del usuario, devuelve los datos del contacto a agregar."""
    datos = validar_datos_contacto()

    print('Se agregará un nuevo contacto con los siguientes datos: {} {}'.format(datos[0], str(datos[1])))

    confirmacion = input("Presione Enter para confirmar, si desea modificar los datos presione la tecla n y luego Enter: ")

    while(confirmacion):
        datos = validar_datos_contacto()
        print('Se agregará un nuevo contacto con los siguientes datos: {} {}'.format(datos[0], str(datos[1])))

        confirmacion = input("Presione Enter para confirmar, si desea modificar los datos presione la tecla n y luego Enter:  ")

    return datos


def validar_datos_contacto():
    """Comprueba que los datos nombre y numero sean correctos y los devuelve."""

    datos = solicitar_datos()
    nombre = datos[0]
    numero = datos[1]

    while(not (nombre and numero)):
        datos = solicitar_datos()
        nombre = datos[0]
        numero = datos[1]

    return datos


def solicitar_datos():
    """Solicita al usuario el ingreso del nombre y numero del nuevo contacto a agregar. Luego los devuelve en una lista."""

    nombre = input("Ingrese el nombre: ")
    try:
        numero = int(input("Ingrese el numero: "))
    except ValueError:
        numero = 0
        print("Por favor ingrese caracteres numericos unicamente.")

    return [nombre, numero]


def buscar_contacto_por_id(cursor, nombre):
    """Recibe un objeto cursor y el nombre del contacto deseado. Solicita a la db el registro cuyo id y nombre coincidan con el solicitado por el usuario. En caso de encontrarlo lo devuelve, si no devuelve 0 para indicar que no se encontro ningun contacto que coincida."""
    contacto = 0

    try:
        id = int(input("Ingrese el id del contacto que desea buscar: "))
        instruccion = 'SELECT * FROM contactos WHERE id="{}" AND nombre="{}"'.format(id, nombre)
        contacto = cursor.execute(instruccion).fetchone()

    except:
        print("Id incorrecto.")

    return contacto


def obtener_contacto_por_id(connection, cursor, accion):
    """Recibe los objetos connection y cursor, y la accion que se desea realizar sobre el contacto (eliminar o editar). Comprueba que se encuentre el registro que coincida con el id y nombre ingresados, si tiene exito lo devuelve."""
    cancelar = ""

    nombre = input('Ingrese el nombre del contacto que desee {}: '.format(accion))
    busqueda = buscar_contacto(cursor, nombre)

    if(not busqueda):
        return

    contacto = buscar_contacto_por_id(cursor, nombre)

    while(not contacto and not cancelar):
        print("No se encontro ningun contacto con el id ingresado, por favor vuelva a intentar.")
        cancelar = input("Ingrese n para cancelar la busqueda, Enter para continuar: ")
        if(cancelar):
            print("Se canceló la busqueda")
            return
        contacto = buscar_contacto_por_id(cursor, nombre)
    return contacto


def validar_opcion_dato_a_modificar():
    """Comprueba que el usuario ingrese una opcion valida entre 1 y 2. Devuelve la opcion elegida: nombre o numero."""
    print("Que dato desea modificar?")
    print("1-Nombre")
    print("2-Numero")
    opcion = input("Ingrese su opcion: ")

    while(opcion!="1" and opcion!="2"):
        opcion = input("Debe ingresar una opcion valida: ")

    if(opcion == "1"):
        dato_a_modificar = "nombre"
    else:
        dato_a_modificar = "numero"

    return dato_a_modificar


def validar_numero(numero):
    """Recibe un dato, comprueba que sea efectivamente un valor numerico y lo devuelve."""
    try:
        numero = int(numero)
    except:
        numero = 0
    return numero


def salir():
    """Muestra un mensaje de cierre de programa."""
    print("Cerrando agenda...")
    return


#---------------------------------------------------------------

#Ejecucion del programa
main()

