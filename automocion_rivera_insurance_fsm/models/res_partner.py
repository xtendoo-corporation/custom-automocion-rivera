# Copyright 2025 Xtendoo Software SLU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_insurance = fields.Boolean(
        string="Es aseguradora",
        index=True,
        help="Marque esta casilla si este contacto es una compañía aseguradora"
    )

