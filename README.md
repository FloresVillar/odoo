# Odoo, una  introduccion

**teoria amablemente resumida por gpt**

Odoo es un ERP (Enterprise Resource Plannig) modular

Un sistema que integra toda la empresa en un solo lugar, cada modulo cubre un area:
- Ventas
- Inventario 
- Contabilidad
- CRM 
- RRHH 
- eCommerce

No es una app , es una plataforma extensible basada en modulos

## Arquitectura

1. Capa de presentacion Frontend

Web (html, css, js framework propio)

2. Capa logica backend 

logica del negocio , reglas, automatizaciones
```bash
    class SaleOrder(models.Model):
        _name = 'sale.order'
        total  =field.Float()
        def calcular_total(self):
            self.total = sum (line.price for line in self.lines)
```

3. Capa de base de datos

DB (postgresl)

```bash
usuario (web) → controladores (http) → modelos(python orm)→ postgres → respuesta
```

## ORM de odoo

Odoo no es una sql directo , usa ORM (Object Relational Mapping). 
```bash
self.env['res.partner'].search([('name','=','Juan')])  
# en lugar de 
SELECT * FROM rest_partner WHERE name = 'Juan';
```

## Estructura de un modulo 

``` mi_modulo/
mi_modulo/
│
├── __init__.py
├── __manifest__.py
├── models/
│   └── modelo.py
├── views/
│   └── vista.xml
├── security/
│   └── ir.model.access.csv
```

**archivos cruciales**

__manifest__.py
```bash
{
    'name' : 'Mi modulo',
    'version' : '1.0'
    'depends' : ['base'],
}
```

models/*.py , la logica

views/*.xml 
```bash
    <form>
        <field name="nombre"/>
    </form>
```

## Despliegue
local (desarrollo)

Servidor(produccion)


VPS, digitalOcean,AWS, GoogleCloud

**docker**

nginx, odoo container, Postgresl container

**Para un rigor terorico revisar la evolucion del changelog**

## Proyecto
Por sugerencia de gpt y gemini, lo ideal es comenzar con un Sistema de ventas + inventario

ejecucion
```bash
    make up
    make scaffold NAME=moodulo 
    
```
