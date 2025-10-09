# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_insurance_company = fields.Boolean(
        string="Aseguradora",
        help="Marca esta opción si el contacto es una compañía aseguradora.",
        default=False,
    )

