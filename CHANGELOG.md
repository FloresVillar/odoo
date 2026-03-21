# Declaracion del docker-compose 

## primeros comandos
La clave de nivel superior
<!-- programar un correccion de plural a singular o viceversa -->

Services, se declaran web y db para ambos servicios.

Luego de declarado el manifiesto.Levantamos (construyendo implicitamente las imagenes) los contenedores
```bash
    docker compose up -d
    curl http://localhost:8069
```

Seguidamente , aprovechamos el bind mount (mapeo de volumen ) **volumes: -./addons:./mnt/extra-addons** el cual nos permite ejecutar **odoo scaffold modulo /mnt/extra-addons** de modo que gracias a  scaffolf creamos una estructura de archivos estandar para **modulo** , con archivos como  __manifest__.py y otros.

Y este queda reflejado (Creado) en nuestro directorio host. Esto es que creamos esa misma estructura.

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

