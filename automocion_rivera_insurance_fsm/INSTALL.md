# Guía de Instalación - automocion_rivera_insurance_fsm

## ✅ Módulo Creado Exitosamente

El módulo **automocion_rivera_insurance_fsm** ha sido creado completamente en:
```
/home/xtendoo/Documentos/odoo/18verifactu/odoo/custom/src/custom-automocion-rivera/automocion_rivera_insurance_fsm/
```

## 📦 Configuración Completada

✅ Añadido al `addons.yaml`
✅ Estructura de archivos completa
✅ Todos los modelos, vistas y tests creados
✅ Traducciones al español incluidas

## 🚀 Opciones de Instalación

### Opción 1: Instalación Automática con Script

He creado un script de instalación que puedes ejecutar:

```bash
cd /home/xtendoo/Documentos/odoo/18verifactu
./install_insurance_fsm.sh
```

**Importante**: Antes de ejecutar el script, edítalo y reemplaza `DBNAME` con el nombre de tu base de datos.

### Opción 2: Instalación Manual desde la Interfaz Web

1. **Accede a Odoo**:
   - URL: http://localhost:18069
   - Inicia sesión con usuario administrador

2. **Activa el Modo Desarrollador**:
   - Settings → Activate Developer Mode

3. **Actualiza la Lista de Aplicaciones**:
   - Apps → Menú (⋮) → Update Apps List
   - Confirma la actualización

4. **Busca e Instala el Módulo**:
   - En la barra de búsqueda escribe: "Automoción Rivera"
   - Busca: **"Automoción Rivera - FSM con Seguros"**
   - Haz clic en **"Instalar"** (o "Install")

5. **Verifica la Instalación**:
   - Ve a **Contactos** → Deberías ver el campo "Es aseguradora"
   - Ve a **Field Service** → Órdenes → El campo "Compañía aseguradora" debe estar visible

### Opción 3: Instalación por Línea de Comandos (Docker)

```bash
cd /home/xtendoo/Documentos/odoo/18verifactu

# 1. Asegúrate de que los contenedores estén corriendo
docker-compose up -d

# 2. Instala el módulo (reemplaza 'tu_base_datos' con tu DB real)
docker-compose run --rm odoo odoo \
  --stop-after-init \
  -i automocion_rivera_insurance_fsm \
  -d tu_base_datos

# 3. Reinicia Odoo
docker-compose restart odoo
```

### Opción 4: Instalación con Invoke (Doodba)

Si estás usando las tareas de Invoke del proyecto:

```bash
cd /home/xtendoo/Documentos/odoo/18verifactu

# Instalar el módulo
invoke install automocion_rivera_insurance_fsm

# O usando el método completo
invoke install -d devel -m automocion_rivera_insurance_fsm
```

## 🔍 Verificación Post-Instalación

Después de instalar, verifica que todo funcione correctamente:

### 1. Producto "Franquicia seguro" creado
```
Ventas → Productos → Buscar "Franquicia seguro"
```
Debe existir un producto de tipo servicio.

### 2. Campo en Contactos
```
Contactos → Crear/Editar → Debe aparecer checkbox "Es aseguradora"
```

### 3. Campos en FSM
```
Field Service → Órdenes → Crear/Editar
→ Debe aparecer "Compañía aseguradora" e "Importe franquicia"
```

### 4. Campos en Pedidos de Venta
```
Ventas → Pedidos → Crear/Editar
→ Debe aparecer pestaña "Seguro"
```

## 🧪 Ejecutar Tests (Opcional)

Para verificar que todo funciona correctamente:

```bash
cd /home/xtendoo/Documentos/odoo/18verifactu

docker-compose run --rm odoo odoo \
  --test-enable \
  --stop-after-init \
  -i automocion_rivera_insurance_fsm \
  -d test_database \
  --log-level=test
```

Deberías ver todos los tests (20 en total) pasando exitosamente.

## ❓ Solución de Problemas

### El módulo no aparece en la lista

**Solución**:
1. Verifica que el contenedor esté corriendo: `docker-compose ps`
2. Actualiza la lista: Apps → Update Apps List
3. Busca sin filtros o con "Todos" activado

### Error: "Module not found"

**Solución**:
```bash
# Reconstruye el contenedor
docker-compose build odoo
docker-compose up -d
```

### Error: "xtendoo_fsm not found"

**Solución**: El módulo `xtendoo_fsm` debe estar instalado primero:
```bash
docker-compose run --rm odoo odoo \
  --stop-after-init \
  -i xtendoo_fsm \
  -d tu_base_datos
```

### Permisos de archivos

Si tienes problemas de permisos:
```bash
cd /home/xtendoo/Documentos/odoo/18verifactu/odoo/custom/src/custom-automocion-rivera
sudo chown -R $USER:$USER automocion_rivera_insurance_fsm
```

## 📝 Próximos Pasos Después de la Instalación

1. **Crear una Aseguradora de Prueba**:
   - Contactos → Crear → Nombre: "Mapfre Test"
   - Marcar: "Es aseguradora" ✓

2. **Crear una Orden FSM con Seguro**:
   - Field Service → Nueva Orden
   - Cliente: Cualquier cliente
   - Aseguradora: "Mapfre Test"
   - Franquicia: 60.50 €

3. **Generar Pedido y Facturar**:
   - Desde la orden FSM → Crear Pedido de Venta
   - Añadir líneas de servicio
   - Confirmar pedido
   - Crear factura → Se generarán 2 facturas automáticamente

4. **Verificar el Split**:
   - Verifica que la suma de ambas facturas = total del pedido

## 📚 Documentación Completa

Consulta los siguientes archivos para más información:

- **README.md**: Documentación técnica completa
- **USAGE.rst**: Guía de uso paso a paso
- **tests/**: Casos de prueba con ejemplos

## 🆘 Soporte

Si encuentras algún problema durante la instalación:

1. Revisa los logs: `docker-compose logs -f odoo`
2. Verifica la configuración: `cat addons.yaml`
3. Contacta con el equipo de desarrollo de Xtendoo

---

**¡Listo para usar!** 🎉

