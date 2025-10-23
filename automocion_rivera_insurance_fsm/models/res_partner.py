from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_insurance = fields.Boolean(string='Es aseguradora')

