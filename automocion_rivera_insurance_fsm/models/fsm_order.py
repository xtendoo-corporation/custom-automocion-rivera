# Copyright 2025 Xtendoo Software SLU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FsmOrder(models.Model):
    _inherit = 'fsm.order'

    insurance_partner_id = fields.Many2one(
        'res.partner',
        string="Compañía aseguradora",
        domain=[('is_insurance', '=', True)],
        tracking=True,
        help="Compañía aseguradora que cubrirá parte del presupuesto"
    )

    franchise_amount = fields.Monetary(
        string="Importe franquicia",
        currency_field='currency_id',
        tracking=True,
        help="Importe que paga el cliente en concepto de franquicia. "
             "El resto será facturado a la aseguradora."
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Moneda",
        compute='_compute_currency_id',
        store=True,
        readonly=False
    )

    @api.depends('company_id')
    def _compute_currency_id(self):
        """Calcula la moneda basada en la compañía"""
        for order in self:
            order.currency_id = order.company_id.currency_id or self.env.company.currency_id

    @api.constrains('franchise_amount')
    def _check_franchise_amount(self):
        """Valida que el importe de franquicia no sea negativo"""
        for rec in self:
            if rec.franchise_amount and rec.franchise_amount < 0:
                raise ValidationError(
                    _("El importe de la franquicia no puede ser negativo.")
                )

    def action_create_sale_order(self):
        """
        Crea un pedido de venta desde la orden FSM y propaga campos de seguro.
        Si el método no existe en el padre, crea el pedido manualmente.
        """
        # Intentar llamar al método padre si existe
        if hasattr(super(FsmOrder, self), 'action_create_sale_order'):
            result = super().action_create_sale_order()

            # Si se creó un pedido de venta, propagamos los campos
            if result.get('res_id'):
                sale_order = self.env['sale.order'].browse(result['res_id'])
                sale_order.write({
                    'insurance_partner_id': self.insurance_partner_id.id,
                    'franchise_amount': self.franchise_amount,
                })

            return result
        else:
            # Si no existe el método, crear el pedido manualmente
            return self._create_sale_order_manual()

    def _create_sale_order_manual(self):
        """Crea un pedido de venta manualmente desde la orden FSM"""
        self.ensure_one()

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'fsm_order_id': self.id,
            'insurance_partner_id': self.insurance_partner_id.id,
            'franchise_amount': self.franchise_amount,
            'origin': self.name,
            'company_id': self.company_id.id,
        })

        # Mensaje en el chatter
        self.message_post(
            body=_("Pedido de venta creado: %s") % sale_order.name
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

