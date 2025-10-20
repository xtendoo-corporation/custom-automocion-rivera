from odoo import models, fields

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    fsm_order_id = fields.Many2one('automocion.fsm.order', string='Orden FSM')
