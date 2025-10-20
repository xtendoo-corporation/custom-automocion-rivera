from odoo import api, fields, models, _
import re

class AutomocionFSMStage(models.Model):
    _name = 'automocion.fsm.stage'
    _description = 'Etapas de Orden de Trabajo Automoción'
    _order = 'sequence, name'

    name = fields.Char(string='Nombre', required=True, translate=True)
    code = fields.Char(string='Código', required=True, help="Código único para identificar la etapa")
    description = fields.Text(string='Descripción')
    sequence = fields.Integer(string='Secuencia', default=10)
    is_closed = fields.Boolean(string='Etapa Cerrada', help="Las órdenes en esta etapa se consideran completadas")
    is_default = fields.Boolean(string='Etapa por Defecto', help="Esta etapa se asigna por defecto a nuevas órdenes")
    color = fields.Char(string='Color', default='#FFFFFF', help="Color hexadecimal para mostrar en vistas kanban")
    active = fields.Boolean(string='Activo', default=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    order_count = fields.Integer(string='Número de Órdenes', compute='_compute_order_count')
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'El código de la etapa debe ser único.'),
        ('default_unique', 'EXCLUDE (company_id WITH =) WHERE (is_default = true)', 'Solo puede haber una etapa por defecto por compañía.'),
    ]

    @api.depends('name')
    def _compute_order_count(self):
        for record in self:
            orders = self.env['automocion.fsm.order'].search([('stage_id', '=', record.id)])
            record.order_count = len(orders)

    def _generate_code_from_name(self, name):
        if not name:
            return 'stage'
        code = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        code = re.sub(r'\s+', '_', code.strip())
        base_code = code
        counter = 1
        while self.search([('code', '=', code)]):
            code = f"{base_code}_{counter}"
            counter += 1
        return code

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'code' in vals and vals['code']:
                vals['code'] = re.sub(r'[^a-zA-Z0-9_]', '_', vals['code']).lower()
            if not vals.get('code') and vals.get('name'):
                vals['code'] = self._generate_code_from_name(vals['name'])
            elif not vals.get('code'):
                vals['code'] = 'stage'
        return super().create(vals_list)
