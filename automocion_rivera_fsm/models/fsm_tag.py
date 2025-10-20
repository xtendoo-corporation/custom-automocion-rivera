from odoo import api, fields, models, _

class AutomocionFSMTag(models.Model):
    _name = 'automocion.fsm.tag'
    _description = 'Etiqueta de Orden de Trabajo Automoción'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color', default=0)
    active = fields.Boolean(string='Activo', default=True)
    description = fields.Text(string='Descripción')
    order_count = fields.Integer(string='Número de Órdenes', compute='_compute_order_count')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre de la etiqueta debe ser único.'),
    ]
    @api.depends('name')
    def _compute_order_count(self):
        for record in self:
            orders = self.env['automocion.fsm.order'].search([
                ('tag_ids', 'in', record.id)
            ])
            record.order_count = len(orders)
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result
