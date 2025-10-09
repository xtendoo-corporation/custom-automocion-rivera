# Automation Rivera – Insurance Flag on Contacts

## Descripción

Este módulo añade un campo booleano **"Aseguradora"** (`is_insurance_company`) al modelo `res.partner` para identificar contactos que son compañías aseguradoras.

## Características

- **Campo booleano**: Marca si un contacto es una aseguradora
- **Vista mejorada**: El campo se muestra en el formulario de contacto
- **Filtro de búsqueda**: Filtro rápido "Aseguradoras" en la vista lista
- **Datos demo**: Incluye contactos de ejemplo marcados como aseguradoras
- **Tests**: Pruebas automatizadas para validar el comportamiento

## Requisitos

- Odoo 18.0 Community o Enterprise
- Python 3.10+

## Instalación

1. Clona este repositorio en tu carpeta de addons:
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/xtendoo-corporation/custom-automocion-rivera.git
   ```

2. Añade la ruta al `addons_path` en tu configuración de Odoo:
   ```ini
   [options]
   addons_path = /path/to/odoo/addons,/path/to/custom-automocion-rivera
   ```

3. Reinicia el servidor Odoo:
   ```bash
   odoo-bin -u all -d your_database
   ```

4. Ve a Aplicaciones, actualiza la lista de aplicaciones y busca "Automation Rivera – Insurance"

5. Instala el módulo

## Uso

### Marcar un contacto como aseguradora

1. Ve a **Contactos**
2. Abre o crea un contacto
3. En el formulario, encontrarás el campo **"Aseguradora"** en la pestaña principal
4. Marca el checkbox si el contacto es una compañía aseguradora
5. Guarda el contacto

### Filtrar aseguradoras

1. Ve a **Contactos**
2. Haz clic en **Filtros** en la barra de búsqueda
3. Selecciona **"Aseguradoras"**
4. Se mostrarán únicamente los contactos marcados como aseguradoras

## Estructura del módulo

```
automation_rivera_insurance_res_partner/
├── __init__.py
├── __manifest__.py
├── README.md
├── SECURITY.md
├── LICENSE
├── models/
│   ├── __init__.py
│   └── res_partner.py
├── views/
│   └── res_partner_views.xml
├── security/
│   └── ir.model.access.csv
├── i18n/
│   └── es.po
├── data/
│   └── demo_insurers.xml
└── tests/
    ├── __init__.py
    └── test_insurance_flag.py
```

## Desarrollo

### Tests

Para ejecutar los tests:

```bash
odoo-bin --test-enable --stop-after-init -d test_db -i automation_rivera_insurance_res_partner
```

### Calidad de código

El módulo cumple con las convenciones OCA y PEP8:

```bash
flake8 automation_rivera_insurance_res_partner
black automation_rivera_insurance_res_partner --check
```

## Créditos

### Autores

- Automoción Rivera
- Xtendoo <https://www.xtendoo.es>

### Colaboradores

- Xtendoo Development Team

## Licencia

LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

## Soporte

Para soporte técnico o consultas, contacta con:
- Xtendoo: info@xtendoo.es
- Automoción Rivera

