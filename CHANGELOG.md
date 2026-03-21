# Declaracion del docker-compose 

## primeros comandos
La clave de nivel superior
<!-- programar un correccion de plural a singular o viceversa -->

Services, se declaran web y db para ambos servicios.

Luego de declarado el manifiesto.Levantamos (construyendo implicitamente las imagenes) los contenedores
````bash
    docker compose up -d
    curl http://localhost:8069
```

