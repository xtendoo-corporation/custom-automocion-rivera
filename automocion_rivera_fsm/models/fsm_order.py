from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AutomocionFSMOrder(models.Model):
    _name = 'automocion.fsm.order'
    _description = 'Orden de Trabajo Automoción'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'priority_level desc, date_scheduled asc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Número', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'), tracking=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True, help="Cliente final para quien se realiza el servicio")
    insurance_partner_id = fields.Many2one('res.partner', string='Aseguradora', required=False, tracking=True, help="Compañía aseguradora que gestiona y paga el servicio")
    franchise_amount = fields.Float(string='Importe Franquicia', tracking=True, digits=(16, 2), help="Importe de la franquicia a cargo del cliente cuando hay aseguradora")
    location_id = fields.Many2one('res.partner', string='Dirección del Servicio', tracking=True, domain="[('parent_id', '=', partner_id)]", help="Dirección de entrega donde se realizará el servicio")
    contact_id = fields.Many2one('res.partner', string='Contacto', help="Persona o empresa de contacto en la ubicación del servicio")
    description = fields.Text(string='Descripción del Trabajo', required=True, tracking=True)
    internal_note = fields.Text(string='Notas Internas', help="Notas internas no visibles para el cliente")
    customer_note = fields.Text(string='Notas del Cliente', help="Notas visibles para el cliente")
    priority_level = fields.Selection([
        ('0', 'Muy Baja'),
        ('1', 'Baja'),
        ('2', 'Normal'),
        ('3', 'Alta'),
        ('4', 'Muy Alta'),
        ('5', 'Urgente')
    ], string='Prioridad', default='2', tracking=True)
    date_created = fields.Datetime(string='Fecha de Creación', default=fields.Datetime.now, readonly=True)
    date_scheduled = fields.Datetime(string='Fecha Programada', tracking=True, help="Fecha y hora programada para el servicio")
    date_start = fields.Datetime(string='Fecha de Inicio', tracking=True)
    date_end = fields.Datetime(string='Fecha de Finalización', tracking=True)
    duration = fields.Float(string='Duración (Horas)', compute='_compute_duration', store=True, help="Duración del trabajo en horas")
    responsible_id = fields.Many2one('res.users', string='Responsable', tracking=True, help="Empleado responsable de esta orden de trabajo")
    person_ids = fields.Many2many('res.users', 'automocion_fsm_order_user_rel', 'order_id', 'user_id', string='Técnicos Asignados', tracking=True, help="Empleados asignados a esta orden de trabajo")
    tag_ids = fields.Many2many('automocion.fsm.tag', string='Etiquetas', help="Etiquetas para clasificar y analizar órdenes")
    repair_order_ids = fields.One2many('repair.order', 'fsm_order_id', string='Reparaciones', help="Partes de reparación relacionados con esta orden de trabajo")
    repair_count = fields.Integer(string='Número de Reparaciones', compute='_compute_repair_count')
    sale_order_ids = fields.One2many('sale.order', 'fsm_order_id', string='Ventas', help="Órdenes de venta relacionadas con esta orden de trabajo")
    sale_count = fields.Integer(string='Número de Órdenes de Venta', compute='_compute_sale_count')
    access_url = fields.Char(string='URL de Acceso', compute='_compute_access_url')
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company, help="Compañía para la que se realiza esta orden de trabajo")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('automocion.fsm.order') or _('Nuevo')
        return super().create(vals_list)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0

    def _compute_repair_count(self):
        for record in self:
            record.repair_count = len(record.repair_order_ids)

    def _compute_sale_count(self):
        for record in self:
            record.sale_count = len(record.sale_order_ids)

    def _compute_access_url(self):
        for record in self:
            record.access_url = f'/my/fsm/{record.id}'

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        stage_ids = self.env['automocion.fsm.stage'].search([('company_id', 'in', [self.env.company.id, False])])
        return stage_ids

    def action_start_work(self):
        if self.date_start:
            raise UserError(_('El trabajo ya ha sido iniciado.'))
        self.write({'date_start': fields.Datetime.now()})
        progress_stage = self.env['automocion.fsm.stage'].search([('code', '=', 'progress'), ('company_id', 'in', [self.env.company.id, False])], limit=1)
        if progress_stage:
            self.stage_id = progress_stage
        return True

    def action_finish_work(self):
        if not self.date_start:
            raise UserError(_('Debe iniciar el trabajo antes de finalizarlo.'))
        if self.date_end:
            raise UserError(_('El trabajo ya ha sido finalizado.'))
        self.write({'date_end': fields.Datetime.now()})
        done_stage = self.env['automocion.fsm.stage'].search([('code', '=', 'done'), ('company_id', 'in', [self.env.company.id, False])], limit=1)
        if done_stage:
            self.stage_id = done_stage
        return True

    def action_print_order(self):
        return self.env.ref('automocion_rivera_fsm.action_report_fsm_order').report_action(self)

    def action_create_repair(self):
        """Crea un parte de reparación vinculado a la orden de trabajo y lo abre en formulario"""
        self.ensure_one()
        repair_vals = {
            'partner_id': self.partner_id.id,
            'fsm_order_id': self.id,
            'name': f'Parte de reparación - {self.name}',
        }
        repair_order = self.env['repair.order'].create(repair_vals)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parte de Reparación',
            'res_model': 'repair.order',
            'res_id': repair_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_sale_order(self):
        """Crea una orden de venta basada en la orden de trabajo"""
        self.ensure_one()
        sale_order_vals = {
            'partner_id': self.partner_id.id,
            'insurance_partner_id': self.insurance_partner_id.id if self.insurance_partner_id else False,
            'franchise_amount': self.franchise_amount,
        }
        sale_order = self.env['sale.order'].create(sale_order_vals)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Orden de Venta'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'view_id': self.env.ref('sale.view_order_form').id,
            'target': 'current',
        }

    def action_view_repairs(self):
        list_view = self.env.ref('automocion_rivera_fsm.view_repair_order_tree', False)
        form_view = self.env.ref('automocion_rivera_fsm.view_repair_order_form', False)
        views = []
        if list_view:
            views.append((list_view.id, 'list'))
        if form_view:
            views.append((form_view.id, 'form'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reparaciones',
            'res_model': 'repair.order',
            'view_mode': 'list,form',
            'views': views or False,
            'domain': [('fsm_order_id', '=', self.id)],
            'context': {'default_fsm_order_id': self.id},
        }

    def action_view_sale_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Venta',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('fsm_order_id', '=', self.id)],
            'context': {'default_fsm_order_id': self.id},
        }
