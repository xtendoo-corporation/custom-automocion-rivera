from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_insurance_company = fields.Boolean(string='Es aseguradora')

