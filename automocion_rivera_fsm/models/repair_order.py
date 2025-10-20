from odoo import models, fields

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    fsm_order_id = fields.Many2one(
        'automocion.fsm.order',
        string='Orden de Trabajo FSM',
        help="Orden de trabajo FSM relacionada con esta reparación"
    )
