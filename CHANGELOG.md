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
el motor de docker  corre como root , si ./addons no existe en nuestro host docker la creara con **root** como dueño.Por ello tiene sentido lo siguiente
<!-- comentario que complementa el comentario↑ -->
Sin embargo la carpeta (addons en nuestro host) pertenece a **root** , luego odoo no puede cambiar( no deberia) los permisos de esa carpeta , de modo que se ingresa al contenedor como root , -u 0 id del usuario root ,y el modo iterativo -terminal **it**, mediante : **docker exec -u 0 -it odoo-web-1**

Una vez hecho esto le damos todos los permisos **chmod -R 777 /mnt/extra-addons**.

Hecho eso se ejecuta scaffold

```bash
    docker exec -u 0 -it odoo-web-1 /bin/bash
    chmod  -R 777 /mnt/extra-addons
    odoo scaffold clientes /mnt/extra-addons
```

Otras posibles maneras son: 
- Haber creado la carpeta **./addons** antes de ejecutar docker compose up -d.
- En el manifiesto en el servicio web , indicamos a docker compose ejecute con nuestra propia identidad. **services: web: user: "1000:1000"** , establecemos user como nuestro usuario (con id 1000)

Para automatizar esos pasos podemos tambien ejecutar comnados makefile up y scaffold.
**make up , make scaffold NAME=MI_MODULO** mi_modulo es el nombre de la subcarpeta de addons, en este caso clientes o ventas_custom

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

Hace algo parecido a lo siguiente:<br>
-Pregunta: Hay una tabla llamada ?**hospital_paciente** 
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
Entonces si tenemos una clase class Entidad con _name = hospital.paciente  con atributo name en **web**  , se ejecutaran comandos sql **CREATE TABLE hospital_paciente (id SERIAL PRIMAY KEY, name VARCHAR NOT NULL, edad INTEGER, create_uid INTEGER, create_date TIMESTAP)**. Como se mencionó id es creado automatiamente y los create_uid y create_date  son creados/auditados automaticamente.Todo esto en **db**.

Algo mas de sintaxis, los atributos que empiezan con **_** como **_name** son instrucciones de configuracion para ORM, en tanto que los fields son estructura de datos.

Y el valor que se asigna a **_name** lleva un '**.**' pues de de ese modo  es posible establecer el prefijo como un namespace y el sufijo como el modulo , de tal forma que **hospital.paciente** sea  diferenciado de por ejemplo **veterinaria.paciente**.

Para terminar la teoria de entidades en odoo, se nota que la clase no es instanciada de forma convencional **entidad = Entidad()** . En este entorno es ORM Registry quien instancia la clase , como se dijo, registra la clase en Registry. Cuando odoo arranca el ORM recorre nuestro codigo y crea una sola instancia(SINGLETON) de la clase para todo el sistema, guardandose este en un diccionario **env**.

Luego solo usamos la instancia creada para realizar las consultas **self.env['hospital.paciente']**.

- **Recordset**

En Odoo una instancia es una coleccion de IDS con una conexion a la base de datos. Esto es **Active Patron**. A diferencia de otros sistemas donde se tiene un objeto por cada fila , en odoo un objeto puede tener 0,1, o muchas filas.

Cuando se ejecuta **search** def metodo: pacientes_mayores = self.env['hospital.pacientes'].search(['edad','>','50'])
print(len(pacientes_mayores)).

Al realizar esta consulta , odoo trae solo los IDS que cumplen la condicion. Como se mencionó, los comandos se envian via psycopg2 y estos se interpretan en bd como SELECT id FROM hospital_pacientes WHERE edad > 50;

Luego en el RECORDSET se tendra un objeto que sabe que tiene los IDS que cumplen la condicion, ¿qué hizo odoo? fue a la tabla en ese momento y se creo el objeto(recordset), no se consulta toda la tabla, sino que se crea un puntero inteligente a un grupo especifico de filas.


comandos de ejecución
```bash
    sudo chown -R $USER:$USER ./addons #para poder editar ,pues por defecto se estaba en modo root
    docker exec -it odoo_container_name /bin/bash
    odoo scaffold module_name /mnt/extra-addons
    # esto crea el modulo con nombre module_name en la carpeta addons, al mismo tiempo que se crea tambien dentro del contenedor en la ruta /mnt/extra-addons

```
Un detalle acerca de los usuarios y permisos de las carpetas, no es un detalle menor.El usuario dentro del contenedor es **odoo** mientras que en nuestro host tiene a nuestro usuario , en este caso **esau**.Que el usuario del contenedor sea odoo , otorga una capa de seguridad de modo que si alguien logra vulnerar e ingresar al contenedor , no podra borrar archivos , ya que eso solo corresponde a acciones del root.

Los permisos 777 775 , permiten que odoo tenga permisos de "otros", de manera que tanto odoo como usuario trabajaran sobre el mismo archivo

En linux, los nombre de usuario son solo etiquetas, lo relevante es el ID numerico.Casi siempre el primer usuario creado tiene ID 1000 , si el usuario dentro del contenedor tuviera ID 1000 , para linux serian la misma "persona".

Chown parece redundante pero es necesario, aunque chmod 777 le da permisos de lectura , escritura y ejecucion (100 010 001) a usuario(dueño) grupo  y otros respectivamente (rwx 111 rwx 111 rwx 111); muchos editores verifican quien es el propietario de la carpeta/archivos.De modo que **sudo chown -R $USER:$USER ./addons** cambia de modo recursivo(-R) la propiedad de usuario:grupo al usuario actual.

Desde luego,dentro del makefile se usa la expansion de comandos DOLAR() y dentro el comando **shell** quien ejecuta comandos de shell en make, **$(shell whoami)**.


**Editando scripts**

Precisado la teoria general se procede a editar los archivos, los cuales a su vez , tienen teoria muy interesante.

## RELACIONES

**Muchos a Uno**

Los campos **fields** seran las columnas de nuestra tabla, la relacion se define mediante **fields.Many2one** o **fields.One2many**.  

**fields.Many2one** en la linea **cliente_id = fields.Many2one()** es una clave foranea (Foreign key) SQL. Define que muchos registros de la tabla ACTUAL apuntan a uno solo de otra tabla
```bash
#El ejemplo es totalmente referencial
#la tabla actual Colegio.cursos 
id (Curso)	name (Título)	 entre otros fields...
1	        Física Cuántica	 
2	        Relatividad	 
3	        Electricidad	 
# la otra tabla profesores (en el caso del codigo es res.partner es la tabla que odoo crea , tambien se puede agregar resgistros desde la ui , pagina web)
id	        name
10	        Prof. Einstein
11	        Prof. Tesla
#entonces profesor_id =  fields.Many2one('colegio.profesores') crea la columna profesor_id como una clave foranea, de modo que : muchos cursos * --- 1 profesor
id (Curso)	name (Título)	profesor_id (FK)
1	        Física Cuántica	    10
2	        Relatividad	        10
3	        Electricidad	    11
```
En el caso del codigo **cliente_id = fields.Many2one('res.partner',String="Cliente")** crea(en SQL) la columna  cliente_id de modo que los registros (filas) de la tabla Venta , tendran el id de un cliente una o varias veces por cada fila. 
Un detalle más, la etiqueta **Cliente** tiene un fin visual para la interfaz de usuario(la pagina web).

Una convencion util es declarar el nombre de ese fields con un **_id**, esto es un estandar para que este campo sea reconocido como una RELACION y no un campo (texto) mas.

vale la pena profundizar **res.partner** .<br>
Una de las ventajas de odoo es que un ERP , viene con un nucleo de tablas preinstaladas, Clientes, Proveedores, Empresas, Personas Fisicas . Tal como se menciono esto puede editarse desde la web de odoo.

Dichas tablas usamos aunque lo las declaramos antes, merced al script **__manifest__.py** , donde **'depends: ['base']'** el modulo base crea la tabla **res_partner** en postgreSQL en cuanto se instala odoo.El ORM de odoo luego busca esa tabla.La tabla desde el cual se referencia tenga un registro con un valor de la columna, que es el **id** de la tabla **res_partner**.

Ahora bien esta logica se ejecuta en **web** contenedor odoo, pero qué del contenedor **db** postgresql. Docker crea el servidor de base de datos(db) , al arrancar se crea una base de datos normalmente llamada **postgres** o el nombre detallado en **db : enviroment: POSTGRES_DB=postgres**.
Cuando entramos a **localhost:8069** se edita un formulario, quee al ser creado mediante **create badatase** el codigo de python en odoo envia el comando SQL a db para crea esa base de datos.

```bash
    # contenedor de la base de datos
    # odoo-db-1 es el nombre del contenedor
    # psql es el programa cliente que vive dentro del contenedor
    # odoo es el usuario odoo 
    # postgres es el nombre de la base de datos
    docker exec -it odoo-db-1 psql -U odoo -d postgres
    # ya dentro del contenedor,listamos las bases de datos
    \l   
```

**Uno a Muchos**

La siguiente linea a analizar es **lineas_id = fields.One2many('venta.ventas.linea','venta_id',string="Lineas")**. La relación muchos a uno es casi intuitivo ; la relacion uno a muchos es un tanto mas demandante.Es preciso entender el negocio. 

En el modelo:  Venta(padre) → VentaLinea(hijos) . Venta es el padre pues representa una transaccion completa **venta 001 (cliente: Juan)** , mientras que VentaLinea es el detalle de la venta **VentaLinea 1→Laptop<br>        VentaLinea 2→Mouse** 

El ejemplo proporcionado por gpt es siempre muy clarificante

```bash
# TICKET DE VENTA
Cliente : Juan

Items:
- Laptop x1  1000
- Mouse  x2  100

TOTAL: 1100

#VENTA(padre)
id = 1 
cliente = Juan
total = 1100

#VentaLinea (hijo)
id = 1   laptop
id = 2   Mouse
```
Como se ve VentaLinea por si solo no tiene sentido por si sola. 

Algunos modelos estandar en ERP's **factura → lineas de factura** , **Pedido → Lineas de pedido** , **Compra → Lineas de compra**. <br>
De  modo que la FK venta_id = fields.Many2one('ventas.venta') indica quee cada lineaventa pertenece a tal o cual venta.

```bash
#uml
+----------------------+
|     Venta            |
+----------------------+
| - id                 |
| - name               |
| - cliente_id         |
| - fecha              |
| - total              |
+----------------------+
| + _compute_total()   |
+----------------------+
          |
          | 1
          |
          |---------------------- 
                                 \
                                  \  *
                          +--------------------------+
                          |   VentaLinea             |
                          +--------------------------+
                          | - id                     |
                          | - venta_id               |
                          | - producto               |
                          | - precio                 |
                          | - cantidad               |
                          | - subtotal               |
                          +--------------------------+
                          | + _compute_subtotal()    |
                          +--------------------------+
```
## campos computados reactivos

@api.depends('precio','cantidad') def _compute_(self): . Es un mecanismo del ORM de odoo para campos computados reactivos.<br>
Queremos que un campo **subtotal** se actualicen de acuerdo a **precio** y **cantidad** (por ejemplo) automaticamente.

No es un listener en tiempo real, sino un sistema de invalidacion + recomputacion diferida. 

Cuando se cambia **linea.precio** (linea es una instancia de la entidad/clase) odoo marca el campo como **dirty** , subtotal → invalido , guarda en cache que debe recalcularse, entonces antes de usarlo recalcula **subtotal = precio * cantidad** . El tipo de campo que usa esto **subtotal = fields.Float(compute='_compute_subtotal')**. Comparando con base de datos clasica, para realizar **subtotal=precio*cantidad** , se tendria que recalcular manualmente con triggers.<br>
con odoo : columna derivada + trigger automatico(depends).

```bash
cambio precio/cantidad→ @api.depends → cambio subtotal se invalida → ORM recalcula automaticamente
```
Equivalente:
- SQL       trigger/computed column
- Excel     formula (=A1*B1)
- React     estado derivado
- Odoo      campo computado + depends

**Tipos de computo**

**fields.Float(compute="_compute_subtotal_)**, se calcula cada vez que se necesita. **fields.Float(compute="_compute_subtotall",store=True)**  se guarda en DB

## CONVENCIONES DE SINTAXIS
Como se mencionó la entidad / clase / tabla  **Venta** tendrá por nombre **ventas_venta** mientras que **VentaLinea** **ventas_venta_linea**. Esto se entiende como linea de venta (ventas → venta → linea) Esto es solo semantico, odoo establece la relacion mediante **venta_id = fields.Many2one('ventas.venta')** que es la FK. En tanto que ventas.venta.linea ayuda a organizar visualmente la relacion.

Para reforzar esta idea el nombre de VentaLinea podria bien ser **_name = 'Venta.detalle'** o incluso **_name='linea'** y todo seguira funcionando normalmente si se mantiene **venta_id = fields.Many2one('ventas.venta')**

De modo que usamos esta convencion por claridad **ventas.venta.linea** muestra exactamente que es. Y este patron permite legibilidad , escalado y es un estandar en odoo **modulo.entidad  modulo.entidad.subentidad**.

## Base de datos
Precisemos el uso de postgres en el ecosistema de ODOO.Esto se realizará de modo iterativo , valga la redundancia (-it).<br>
Entramos al contenedor de la base de datos **docker exec -it odoo-db-1 /bin/bash**. Dentro de ella nos conectamos a la base de datos declarado en el manifiesto **environment: POSTGRES_DB: postgres**. Entonces psql -

**Problemas con el admin_pass**

La ui de odoo en localhost:8069 no reconocia el admin_passwd generado y hasheado en el conteneddor odoo. Se intento modificar el archivo /etc/odoo/odoo.conf via **sed '||'** , no funciono. De modo que en lugar de intentar modificar ese archivo nuevamente, pues al ejecutar docker compose restart , odoo hashea nuevamente dicha contraseña, lo cual genera una inconsistencia.<br>
Luego lo que  se hace es montar un volumnen, **volumes: ./config:/etc/odoo/odoo.conf** en el servicio web. El contenido de ./config/odoo.conf en nuestro host es la que usara odoo, evitando la configuracion predeterminada.

Lo cual resuelve la autenticacion.Ello resuelto se procede a detallar con profundidad **ventas_custom/__manifest.py**. Este archivo es un diccionario de python. Odoo implementa algo como <br>
**sistema de modulos = grafo de dependencias + metadata declarativa**<br>
Que es tu modulo y como se integra al sistema.Cuando odoo arranca o actualiza escane **addons_path** encuentra **__manifest__.py** lo evaua y construye el grafo de dependencias , decidiendo luego el orden de carga.

El contenido son pares claves-valor 
- La metadata es la informacion que no afecta la logica **'name' , 'summary', 'description'..**.

- Dependencias **'depends':['base']**. Esto define un grafo dirigido **ventas_custom → base**. Instala primero base luego el modulo propio y nos da acceso a sus modulos.

- Datos **'data':[...]** es una lista de scripts declarativos, odoo los ejecuta en orden **.csv** para permisos, **views.xml** para vistas y acciones, **templates.xml** QWeb fronted. Odoo usa un modelo ACL (access control list) de modo que se define quien puede leer , escribir, crear y eliminar definido en security/ir.model.access.csv.

```bash
'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
```
- flags de comportamiento  **'installable': True** Si es False odoo ignora el modulo, **'application': True** aparece como una app principal.

- Demo data **'demo':['demo/demo.xml']** para ver el demo

Odoo usa este principio arquitectonico : **declarative modular system** , para desacoplar, para un orden automatico de carga .
La analogia seria : **__manifest__.py = packeges.json(Node) + migrations(DB) + metadata**.

```bash
                ┌──────────────────────────┐
                │   __manifest__.py        │
                │ (metadata + depends)    │
                └──────────┬──────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────┐
        │  Resolver dependencias (GRAFO)      │
        │  topological sort                  │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  Orden de instalación de módulos    │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  IMPORTAR CÓDIGO PYTHON             │
        │  (__init__ → models.py)             │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  REGISTRY (ORM)                    │
        │  - registrar modelos (_name)       │
        │  - registrar fields                │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  SINCRONIZAR BASE DE DATOS          │
        │  - crear tablas                    │
        │  - alterar columnas                │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  EJECUTAR 'data' (XML/CSV)          │
        │  (EN ORDEN DEFINIDO)               │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  SEGURIDAD (ACL + rules)            │
        │  ir.model.access.csv               │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  VISTAS (XML)                       │
        │  form / tree / actions              │
        └──────────┬──────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────┐
        │  MÓDULO LISTO EN UI                 │
        └─────────────────────────────────────┘
```

## VIEWS
Un parafraseo por gpt. **Un modelo no aparece en la UI por existir sino que aparece porque se conecta explicitmente**, de la siguiente manera.

```bash
models.py
   │
   ▼
(ir.model)  ← ORM registra modelo
   │
   ▼
VISTA (XML: form / tree)
   │
   ▼
ACCIÓN (ir.actions.act_window)
   │
   ▼
MENÚ (ir.ui.menu)
   │
   ▼
 INTERFAZ ODOO
```
**models.py** define la estructura (tabla + campos) pero aun no hay ui. Entonces definimos 
- vistas(record id ="" model ="" representacion declarativa del modelo)
- acciones(record id="" model="" instruccion de navegacion, **cuando alguien haga clic, abre este modelo con estas vistas**)
- menu (menu = punto de entrada en la ui)

Un resumen intuitivo util 
```bash
models.py == que es
views.xml == como se ve
action == como se abre
menu == como llegas
```
Tambien es importante el orden en el __manifest__.py , primero los permisos **'security/ir.model.access.csv'** y luego las vistas **'views/views.xml'**

El archivo **ventas_custom/views/views.xml** ; un archivo xml en odoo no es solo para diseño , es un archivo que carga datos. Cada vez que se instala o actualiza algo , odoo lee el xml y "traduce" las etiquetas a filas en sus tablas internas.

- **<odoo>** Es la etiqueta raiz que envuelve todo<br>
- **<data>** Indica que que los registros son para la base de datos<br>
- **<record>** Define un nuevo registro , este tiene dos atributos clave. **MODEL** indica en que tabla interna de odoo se guardara este diseño **ir.ui.view** para vistas, **ir.actions.act_windows** para acciones.Mientras que **ID** es un identificador unico XML ID , que sirve para que otros archivos puedan referenciar este registro sin conocer su ID numerico de la base de datos,es arbitrario.

- **<field** Define el valor de una columna especifica para ese registro


Mientras que **menuitem** es el puente final, es un acceso directo (shorthand) que odoo nos da en el xml para insertar filas en esas tablas sin tener que escribir toda la estructura de un **<record>**.Pues los menus no son archivos de configuracion estaticos, sino registros en una tabla de la base de datos **ir.ui.menu**. <br>
Odoo organiza los menus como un arbol.

- Menu raiz (root) **<menuitem id="menu_root" name="Ventas.."** ,sin parent , en la UI es el icono que aparece en "app switcher" es la puerta a la aplicacion

- La categoria(folder) **<menuitem id="menu_1" name="operaciones" parent="menu_root"** en la UI una vez que se entra a la app , se ve una barra horizontal morada, con un texto **operaciones** , si se hace clic se despliega como una lista (como una carpeta)

- La accion (leaf/boton) **<menuitem id="menu_list" name="listado" parent="menu_1" action="action_id"** En la ui es la opcion final dentro del desplegable de operaciones. cuando se hace clic aqui, es cuando odoo ejecuta **res_model** y nos muestra la tabla con los datos de **models.py**


- Categorias (folders) 
El nexo con nuestro **models/models.py** es **res_model** (resource model), este campo no esta en un archivo python sino que es un campo de una tabla interna de odoo **ir.actions.act_window**.

Luego cuando se hace clic en un menu, odoo busca una accion de Ventana.Esa accion es la que le dice al navegador "Ve a la base de datos , busca la tabla de este modelo y muestrame sus datos". En xml esta accion se define en **<record model="ir.actions.act_window"..**. El valor debe ser exactamente el **_name** de nuestro **models.py**. En este caso el nombre del modulo es **_name = 'ventas.venta'** , en el XML el res_model es **ventas.venta**


## security/ir.model.access.csv 
Este archivo define los permisos de acceso a nivel de modelo. Odoo implementa ACL + record rules, este csv pertenece a la primera capa ACL. 

El separador(en este caso ) es un **,** de modo que las columnas se definen en la primera fila:
- **id** External ID de la regla, nombre unico para la regla, se suele usar **access_** seguido del nombre del modelo. En este caso seria access_ventas_custom_venta

- **name** un titulo para la regla (puede ser el nombre del modelo)

- **model_id** ID: critico, debe ser **model_** seguido del **_name** de nuestra clase en models.py cambiando los puntos por guiones bajos, en este caso model_ventas_venta 

- **group_id** id: el grupo de usarios normalmente **base.group_user**

- Permisos (1,1,1,1) cuatro columnas de si o no para (ver, editar, crear, borrar)

Ademas, en odoo cada tabla de la base de datos es un mundo independiente, cada uno necesita su propios permisos. En este proyecto se tiene Venta y VentaLinea 


modificado estos scripts se ejecuta **docker compose restart** y en **localhost:8069** activando en settings el modo desarrollo , luego buscando en app **ventas_custom**, damos clic a activate y luego a new.