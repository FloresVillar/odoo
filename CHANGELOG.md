## Declaracion del docker-compose 

**primeros comandos**

Parafraseado  y sintetizado por mi persona de los diversas respuestas de gpt y gemini, para rigor tecnico revisar las documentaciones correspondiente, pero siendo honestos ¿alguien lo hace?.

<!-- programar un correccion de plural a singular o viceversa -->

La clave de nivel superior Services, se declaran web y db para ambos servicios.
Y en ellas las claves de segundo nivel , como parametros de configuracion **image, ports y volumes** , tambien directivas de orquestacion **depends_on**
y las variables **environment**. Se recomienda revisar el manifiesto.


Luego de declarado dicho manifiesto.Levantamos  construyendose implicitamente las imagenes 

```bash
    docker compose up -d
    curl http://localhost:8069
```

Seguidamente , aprovechamos el bind mount (mapeo de volumen ) **volumes: -./addons:./mnt/extra-addons** el cual nos permite ejecutar **odoo scaffold modulo /mnt/extra-addons** de modo que gracias a  scaffolf creamos una estructura de archivos estandar para **modulo** , con archivos como  __manifest__.py y otros.

Y este queda reflejado (Creado) en nuestro directorio host. Esto es que creamos esa misma estructura.

comandos de ejecucion
```bash
    docker ps  # averiguar el nombre del contenedor odoo, normalmente docker usa una convecion de nomenclatura carpeta , nombre_servicio , numero_instancia
    docker exec -it odoo-web-1 
    odoo scaffold clientes /mnt/extra-addons   # Errno 13
    exit
```

Sin embargo la carpeta (addons en nuestro host) pertenece a **root** , luego odoo no puede cambiar( no deberia) los permisos de esa carpeta , de modo que se ingresa al contenedor como root **docker exec -u 0 -it odoo-web-1**

Una vez hecho esto le damos todos los permisos **chmod -R 777 /mnt/extra-addons**.

Hecho eso se ejecuta scaffold

```bash
    docker exec -u 0 -it /bin/bash
    chmod  -R 777 /mnt/extra-addons
    odoo scaffold clientes /mnt/extra-addons
```

## Construccion de entidades
Primero aclaremos en que consiste una entidad.

Entidad ~ tabla (base de datos)

Entidad ~ Clase (programacion)

Esta entidad está compuesta de  
- La estructura (models.Model)
- La tabla en la DB, al crear el modelo **hospital.paciente**
- Los registros (records) : cada fila de esa tabla es una instancia de la entidad. 

```bash
# EJEMPLO DE ENTIDAD
import odoo import models,fields # importamos la API

class Entidad(models.Model): # heredamos de los modelos de odoo, entonces la clase sera una base de datos
    _name = 'hospital.paciente'  # registramos la entidad  
    _descripcion = '..'

    name = fields.Char(string='Nombre')
    fecha = fields.Date(string='Fecha de Registro')
```
De modo definiendo la clase ~ base de datos via **docker compose restart** odoo traduce esta clase a una base de datos. Lee **name** y convierte **hospital.paciente** a **hospital_paciente** que es nuestra tabla (entidad~clase~tabla) con columnas name y fecha (atributos de la clase Entidad). 

Entonces en odoo(la pagina) clickeamos **crear** y escribimos **Perez Jose** y **10/03/2026** , eso es una fila (instancia) de la clase Entidad.

Pero veamos a cuasi bajo nivel como sucede esta lectura/ interpretacion. Cómo al reiniciar el contenedor  el ORM (object relational mapping) actua como el motor traductor entre python y SQL(postgres).

**carga del codigo**<br>
Sucede esto: el interprete de python lee **__manifest__.py**  →  odoo importa los scripts listados en  **models/__init__.py**  →  como la clase herada de **models.Model** odoo la registra en un diccionario interno **Registry**.

**check de la base de datos**<br>
Cuando esta clase/tabla/entidad , el ORM se conecta a la base de datos **db** esto es posible a las variables de entorno del manifiesto **enviroment: -HOST=db - USER=odoo -PASSWORD=odoo**.Se crea una cadena de conexion(DSN) hacia en contenedor de la base de datos **db**.Es entonces que  motor de odoo (escrito en python) usa la libreria **psycopg2(Driver)** para  el envio de comandos SQL.Finalmente se realiza la  consulta de metadatos 

-Pregunta: Hay una tabla llamada **hospital_paciente** 
- Si no existe: Odoo ejecuta un comando SQL **CREATE TABLE hospital_paciente (...);**
- Si existe : Odoo compara las columnas de la tabla con los **fields** de la clase

**Generacion automatica de sql**<br>
Luego se traduce los tipos de campo python **fields.Char(Tipo='Nombre')**
- fields.Char → VARCHAR
- fields.Integer → INTEGER
- fields.Text → TEXT
- fields.Boolean → BOOLEAN
Además , Odoo siempre añade automaticamente las columnas **id(Serial/PK)** , **create_uid**, **create_date**, **write_uid** , **write_date**

**Sincronizacion del esquema**<br>
Si en la clase Python Entidad creamos un nuevo fields como **edad = fields.Float()** , al actualizar el ORM detecta la columna **edad** no esta presente en la tabla y ejecuta un **ALTER TABLE hospital_paciente ADD COLUMN precio double precision;** 

 
Esquema ascii del pipeline

```bash
[ TU MÁQUINA (HOST) ]          [ CONTENEDOR ODOO (WEB) ]            [ CONTENEDOR POSTGRES (DB) ]

          |                               |                                      |
  (1) Editas .py   ----[Volumen]--->  /mnt/extra-addons                          |

          |                               |                                      |
          |                    (2) REINICIO / UPDATE                             |
          |                  (docker compose restart)                            |
          |                               |                                      |
          |                 [ INTÉRPRETE PYTHON ODOO ]                           |
          |                 /             |          \                           |
          |      (3) Carga __init__   (4) Lee Clase  (5) Registro en             |
          |          y Models            Model         ORM Registry              |
          |             |                 |              |                       |
          |             V                 V              V                       |
          |      [ Importación ] ---> [ Análisis ] ---> [ ORM Engine ]           |
          |                                              |                       |
          |                                     (6) Generación de SQL            |
          |                                     (CREATE/ALTER TABLE)             |
          |                                              |                       |
          |                                     (7) Envío vía PSYCOPG2 --------> |
          |                                              |          [ PUERTO 5432 ]
          |                                              |                 |
          |                                              |      (8) Ejecución SQL Real
          |                                              |      (Persistencia en Disco)
          |                                              |                 |
          | <--- [ CONFIRMACIÓN ] <--- [ LOGS DE ODOO ] <+------- [ OK / ERROR ] --'

```
Entonces si tenemos una clase class Entidad con _name = hospital.paciente  con atributo name en **web**  , se ejcutaran comandos sql **CREATE TABLE hospital_paciente (id SERIAL PRIMAY KEY, name VARCHAR NOT NULL, edad INTEGER, create_uid INTEGER, create_date TIMESTAP)**. Como se menciono id es creado automatiamente y los create_uid y create_date  son creados auditados automaticamente.Todo esto en **db**.

Algo mas de sintaxis, los atributos que empiezan con **_** como **_name** son instrucciones de configuracion para ORM, en tanto que los fields son estructura de datos.

Y el valor que se asigna a **_name** lleva un '**.**' pues de de ese modo  es posible establecer el prefijo como un namespace y el sufijo como el modulo , de tal forma que **hospital.paciente** sea  diferenciado de por ejemplo **veterinaria.paciente**.

Para terminar la teoria de entidades en odoo, se nota que la clase no es instanciada de forma convencional **entidad = Entidad()** . En este entorno es ORM Registry quien instancia la clase , como se dijo, registra la clase en Registry. Cuando odoo arranca el ORM recorre nuestro codigo y crea una sola instancia(SINGLETON) de la clase para todo el sistema, guardandose este en un diccionario **env**.

Luego solo usamos la instancia creada para realizar las consultas **self.env['hospital.paciente']**.

- **Recordset**

En Odoo una instancia es una coleccion de IDS con una conexion a la base de datos. Esto es **Active Patron**. A diferencia de otros sistemas donde se tiene un objeto por cada fila , en odoo un objeto puede tener 0,1, o muchas filas.

Cuando se ejecuta **search** def metodo: pacientes_mayores = self.env['hospital.pacientes'].search(['edad','>','50'])
print(len(pacientes_mayores)).

Al realizar esta consulta , odoo trae solo los IDS que cumplen la condicion. Como se mencionó, los comandos se envian via psycopg2 y estos se interpretan en bd como SELECT id FROM hospital_pacientes WHERE edad > 50;

Luego en el RECORDSET se tendra un objeto que sabe que tiene los IDS que cumplen la condicion, que hizo odoo? fue a la tabla en ese momento y se creo el objeto, no se consulta toda la tabla, sino que se crea un puntero inteligente a un grupo especifico de filas.


comandos de ejecucion
```bash
    sudo chown -R $USER:$USER ./addons #para poder editar ,pues por defecto se estaba en modo root
    docker exec -it odoo_container_name /bin/bash
    odoo scaffold module_name /mnt/extra-addons
    # esto crea el modulo con nombre module_name en la carpeta addons, al mismo tiempo que se crea tambien dentro del contenedor en la ruta /mnt/extra-addons

```
Un detalle acerca de los usuarios y permisos de las carpetas, no es un detalle menor.El usuario dentro del contenedor es **odoo** mientras que en nuestro host tiene a nuestro usuario , en este caso **esau**.Que el usuario del contenedor sea odoo , otorga una capa de seguridad de modo que si alguien logra vulnerar e ingresar al contenedor , no podra borrar archivos , ya que eso solo corresponde a acciones del root.

Los permisos 777 775 , permiten que odoo tenga permisos de "otros", de manera que tanto odoo como usuario trabajaran sobre el mismo archivo

En linux, los nombre de usuario son solo etiquetas, lo relevante es el ID numerico.Casi siempre el primer usuario creado tiene ID 1000 , si el usuario dentro del contenedor tuviera ID 1000 , para linux serian la misma "persona".

**Editando scripts**

Precisado la teoria se procede a editar los archivos 









 


