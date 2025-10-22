# Automoción Rivera - FSM con Seguros

## Descripción

Módulo de integración de aseguradoras en órdenes de servicio de campo (FSM) con funcionalidad de split de facturación por franquicia para Odoo 18.0.

Este módulo permite gestionar trabajos cubiertos por seguros donde:
- El cliente paga la franquicia
- La aseguradora cubre el resto del presupuesto
- Se generan automáticamente dos facturas separadas

## Características principales

### 1. Gestión de Aseguradoras
- Campo `is_insurance` en contactos para marcar aseguradoras
- Filtros de búsqueda para localizar rápidamente aseguradoras
- Dominio específico para seleccionar solo aseguradoras en pedidos

### 2. Campos en Órdenes FSM
- **Compañía aseguradora**: Selección de la aseguradora que cubrirá el trabajo
- **Importe franquicia**: Cantidad que pagará el cliente
- Validación para evitar importes negativos
- Visibilidad condicional: franquicia solo visible si hay aseguradora seleccionada

### 3. Propagación a Pedidos de Venta
- Los campos de seguro se copian automáticamente de FSM a pedido de venta
- Indicador visual `has_insurance_split` en pedidos con facturación dividida
- Pestaña dedicada "Seguro" en el formulario de pedidos

### 4. Split de Facturación Automático
Cuando un pedido tiene aseguradora y franquicia > 0, al facturar se crean **dos facturas**:

#### Factura al Cliente (Franquicia)
- Partner: Cliente del pedido
- Contenido: 1 línea con producto "Franquicia seguro"
- Importe: Franquicia con impuestos aplicados

#### Factura a la Aseguradora (Resto)
- Partner: Compañía aseguradora
- Contenido: Todas las líneas del pedido + línea negativa de franquicia
- Importe: Total del pedido - franquicia (con impuestos)

#### Características del Split
- ✅ Suma de ambas facturas = Total del pedido (garantizado)
- ✅ Soporta múltiples líneas de pedido
- ✅ Compatible con impuestos incluidos/excluidos
- ✅ Respeta fiscal positions (mapeo de impuestos)
- ✅ Soporta múltiples monedas
- ✅ Multi-compañía
- ✅ Precisión decimal correcta (sin errores de redondeo)
- ✅ Mensajes en chatter con trazabilidad completa

## Instalación

### Requisitos previos
- Odoo 18.0
- Módulo `xtendoo_fsm` instalado
- Módulos estándar: `sale`, `account`, `contacts`

### Pasos de instalación

1. **Clonar o copiar el módulo** en el directorio de addons:
```bash
cd /path/to/odoo/addons
cp -r automocion_rivera_insurance_fsm ./
```

2. **Actualizar lista de aplicaciones**:
   - Modo desarrollador activado
   - Apps → Actualizar lista de aplicaciones

3. **Instalar el módulo**:
   - Buscar "Automoción Rivera - FSM con Seguros"
   - Hacer clic en "Instalar"

4. **Verificar instalación**:
   - Producto "Franquicia seguro" creado automáticamente
   - Campos visibles en FSM y pedidos de venta

## Uso

### Flujo completo de trabajo

#### 1. Crear Aseguradora
```
Contactos → Crear
- Nombre: "Mapfre", "Allianz", etc.
- Marcar: "Es aseguradora" ✓
```

#### 2. Crear Orden FSM con Seguro
```
FSM → Órdenes de Trabajo → Crear
- Cliente: Seleccionar cliente final
- Descripción: Detalle del trabajo
- Compañía aseguradora: Seleccionar aseguradora
- Importe franquicia: Ej. 60.50 € (incluye IVA)
```

#### 3. Generar Pedido de Venta
```
Desde la orden FSM → Botón "Crear Pedido de Venta"
- Los campos de seguro se copian automáticamente
- Añadir líneas de productos/servicios
- Confirmar pedido
```

#### 4. Facturar
```
Desde el pedido → Botón "Crear factura"
- Se crean automáticamente 2 facturas en borrador:
  1. Factura al cliente (franquicia)
  2. Factura a aseguradora (resto)
- Validar ambas facturas
- Contabilizar y cobrar según proceda
```

### Verificación de Resultados

✅ **Suma correcta**:
```
Total Factura Cliente + Total Factura Aseguradora = Total Pedido
```

✅ **Trazabilidad**:
- Mensajes en chatter del pedido
- Referencias cruzadas en facturas
- Campo `invoice_origin` apunta al pedido

## Configuración

### Producto "Franquicia seguro"

**XML-ID**: `automocion_rivera_insurance_fsm.product_franchise`

Características:
- Tipo: Servicio
- Política de factura: Por pedido
- Impuestos: Toma impuestos por defecto de la compañía

**Personalización**:
Si necesita cambiar impuestos por defecto, edite el producto desde:
```
Ventas → Productos → Franquicia seguro → Pestaña Ventas
```

### Impuestos y Fiscal Positions

El módulo respeta completamente las reglas fiscales:
- Si el cliente tiene una fiscal position, se aplica al producto franquicia
- Si la aseguradora tiene otra fiscal position, se aplica en su factura
- Soporta impuestos incluidos (`price_include=True`)

### Multi-compañía

El módulo es compatible con múltiples compañías:
- Los pedidos usan la moneda de su compañía
- Las facturas respetan las secuencias de cada compañía
- Los impuestos se obtienen de la compañía correspondiente

## Campos Técnicos

### res.partner
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_insurance` | Boolean | Marca si el contacto es una aseguradora |

### fsm.order
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `insurance_partner_id` | Many2one | Compañía aseguradora (domain: is_insurance=True) |
| `franchise_amount` | Monetary | Importe de franquicia con impuestos |
| `currency_id` | Many2one | Moneda (por defecto: moneda de la compañía) |

### sale.order
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `insurance_partner_id` | Many2one | Compañía aseguradora |
| `franchise_amount` | Monetary | Importe de franquicia |
| `has_insurance_split` | Boolean (computed) | Indica si habrá facturación dividida |

## Validaciones y Constraints

1. **Franquicia no negativa**: `franchise_amount >= 0`
2. **Franquicia vs Total**: `franchise_amount <= amount_total` del pedido
3. **Aseguradora obligatoria**: Si hay franquicia, debe haber aseguradora

## Tests

El módulo incluye 12 tests automáticos que cubren:

- ✅ Campo `is_insurance` en contactos
- ✅ Campos de seguro en FSM
- ✅ Constraints de validación
- ✅ Propagación FSM → Pedido
- ✅ Cálculo de `has_insurance_split`
- ✅ Split básico de facturación
- ✅ Split con múltiples líneas
- ✅ Pedidos sin seguro (facturación estándar)
- ✅ Validación franquicia vs total
- ✅ Impuestos incluidos en precio
- ✅ Multi-compañía

### Ejecutar tests
```bash
odoo-bin -c odoo.conf -d test_db -i automocion_rivera_insurance_fsm --test-enable --stop-after-init
```

## Limitaciones y Notas

### Limitaciones conocidas
1. **Una sola aseguradora por pedido**: No soporta múltiples aseguradoras en el mismo pedido
2. **Franquicia fija**: El importe de franquicia no se recalcula automáticamente si cambia el total del pedido
3. **No reversible**: Una vez creadas las facturas, no hay opción automática para unificarlas

### Notas sobre fiscalidad
- El módulo respeta las fiscal positions, pero **no calcula automáticamente** la franquicia con/sin impuestos. El usuario debe introducir el importe ya calculado.
- En caso de impuestos complejos (varios tipos en el mismo pedido), la distribución se hace proporcionalmente.

### Mejores prácticas
1. **Definir franquicia antes de confirmar**: Evite cambiar la franquicia después de confirmar el pedido
2. **Revisar totales**: Antes de validar las facturas, verifique que la suma coincide
3. **Comunicación con cliente**: Informe al cliente que recibirá una factura separada por la franquicia

## Troubleshooting

### Error: "No se encontró el producto 'Franquicia seguro'"
**Solución**: Reinstale el módulo o cree manualmente el producto con XML-ID `product_franchise`

### Las facturas no suman correctamente
**Causa**: Posible problema de redondeo con monedas de baja precisión
**Solución**: Verifique la configuración de decimales de la moneda (Settings → Monedas)

### La aseguradora no aparece en el desplegable
**Causa**: El contacto no tiene marcado `is_insurance=True`
**Solución**: Edite el contacto y marque la casilla "Es aseguradora"

### El campo franquicia no es visible
**Causa**: No se ha seleccionado una aseguradora
**Solución**: Primero seleccione la compañía aseguradora

## Soporte y Contribuciones

**Autor**: Xtendoo Software SLU
**Website**: https://xtendoo.es
**Licencia**: LGPL-3

Para reportar bugs o solicitar funcionalidades, por favor contacte con el equipo de desarrollo.

## Changelog

### 18.0.1.0.0 (2025-01-22)
- Versión inicial
- Split de facturación por franquicia
- Integración con xtendoo_fsm
- Tests completos
- Documentación en español

