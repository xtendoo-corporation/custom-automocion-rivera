# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Automation Rivera – Insurance flag on Contacts",
    "summary": "Añade un check 'Aseguradora' en contactos y un filtro rápido.",
    "version": "18.0.1.0.0",
    "category": "Contacts",
    "author": "Automoción Rivera / Xtendoo",
    "website": "https://www.xtendoo.es",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
    ],
    "demo": [
        "data/demo_insurers.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

