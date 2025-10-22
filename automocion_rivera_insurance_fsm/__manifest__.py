# Copyright 2025 Xtendoo Software SLU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Automoción Rivera - FSM con Seguros",
    "summary": "Integración de aseguradoras en órdenes FSM con split de facturación por franquicia",
    "version": "18.0.1.0.0",
    "category": "Field Service",
    "author": "Xtendoo Software SLU",
    "website": "https://xtendoo.es",
    "license": "LGPL-3",
    "depends": [
        "xtendoo_fsm",
        "sale",
        "account",
        "contacts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_data.xml",
        "views/res_partner_views.xml",
        "views/fsm_order_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

