# Copyright 2025 Xtendoo Software SLU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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

    has_insurance_split = fields.Boolean(
        string="Facturación dividida",
        compute='_compute_has_insurance_split',
        store=True,
        help="Indica si este pedido se facturará dividido entre cliente y aseguradora"
    )

    @api.depends('insurance_partner_id', 'franchise_amount')
    def _compute_has_insurance_split(self):
        """Calcula si el pedido tendrá facturación dividida"""
        for order in self:
            order.has_insurance_split = bool(
                order.insurance_partner_id and order.franchise_amount > 0
            )

    @api.constrains('franchise_amount')
    def _check_franchise_amount(self):
        """Valida que el importe de franquicia no sea negativo"""
        for rec in self:
            if rec.franchise_amount and rec.franchise_amount < 0:
                raise ValidationError(
                    _("El importe de la franquicia no puede ser negativo.")
                )

    @api.constrains('franchise_amount', 'amount_total')
    def _check_franchise_vs_total(self):
        """Valida que la franquicia no supere el total del pedido"""
        for rec in self:
            if rec.franchise_amount and rec.amount_total:
                precision = rec.currency_id.decimal_places
                if float_compare(
                    rec.franchise_amount,
                    rec.amount_total,
                    precision_digits=precision
                ) > 0:
                    raise ValidationError(
                        _("El importe de la franquicia (%.2f) no puede ser mayor "
                          "que el total del pedido (%.2f).") %
                        (rec.franchise_amount, rec.amount_total)
                    )

    def action_view_insurance_info(self):
        """Muestra información sobre la facturación dividida"""
        self.ensure_one()
        message = _(
            "Este pedido tiene configurada facturación dividida:\n\n"
            "• Cliente: %s\n"
            "• Aseguradora: %s\n"
            "• Franquicia: %.2f %s\n"
            "• Total pedido: %.2f %s\n\n"
            "Al crear la factura se generarán automáticamente:\n"
            "1. Factura al cliente por la franquicia\n"
            "2. Factura a la aseguradora por el resto"
        ) % (
            self.partner_id.name,
            self.insurance_partner_id.name,
            self.franchise_amount,
            self.currency_id.symbol,
            self.amount_total,
            self.currency_id.symbol
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Información de Facturación Dividida'),
                'message': message,
                'type': 'info',
                'sticky': False,
            }
        }

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Override para crear facturas divididas cuando hay aseguradora y franquicia.
        Si el pedido tiene insurance_partner_id y franchise_amount > 0:
        - Crea dos facturas personalizadas (cliente y aseguradora)
        Si no, llama al proceso estándar
        """
        orders_with_insurance = self.filtered('has_insurance_split')
        orders_without_insurance = self - orders_with_insurance

        invoices = self.env['account.move']
        # Procesar pedidos con seguro y franquicia
        for order in orders_with_insurance:
            invoice_pair = order._create_insurance_split_invoices(date=date)
            invoices |= invoice_pair
        # Procesar pedidos normales con el proceso estándar
        if orders_without_insurance:
            invoices |= super(SaleOrder, orders_without_insurance)._create_invoices(
                grouped=grouped, final=final
            )
        return invoices

    def _create_insurance_split_invoices(self, date=None):
        """
        Crea dos facturas:
        1. Factura al cliente por la franquicia
        2. Factura a la aseguradora por el resto
        """
        self.ensure_one()

        if not self.has_insurance_split:
            return self.env['account.move']

        franchise_product = self.env.ref(
            'automocion_rivera_insurance_fsm.product_franchise',
            raise_if_not_found=False
        )

        if not franchise_product:
            raise UserError(
                _("No se encontró el producto 'Franquicia seguro'. "
                  "Por favor, reinstale el módulo automocion_rivera_insurance_fsm.")
            )

        # 1. Crear factura al cliente (franquicia)
        customer_invoice = self._create_franchise_invoice(
            franchise_product, date=date
        )

        # 2. Crear factura a la aseguradora (resto)
        insurance_invoice = self._create_insurance_invoice(
            franchise_product, date=date
        )

        # Mensajes en el chatter
        customer_msg = _(
            "Factura de franquicia creada: %s (%.2f %s). "
            "Pedido de venta: %s"
        ) % (
            customer_invoice.name,
            self.franchise_amount,
            self.currency_id.symbol,
            self.name
        )

        insurance_total = insurance_invoice.amount_total
        insurance_msg = _(
            "Factura a aseguradora creada: %s (%.2f %s). "
            "Pedido de venta: %s"
        ) % (
            insurance_invoice.name,
            insurance_total,
            self.currency_id.symbol,
            self.name
        )

        self.message_post(body=customer_msg + "<br/>" + insurance_msg)
        customer_invoice.message_post(
            body=_("Factura de franquicia del pedido %s") % self.name
        )
        insurance_invoice.message_post(
            body=_("Factura a aseguradora del pedido %s. "
                   "Resto tras descontar franquicia de %.2f %s.") %
            (self.name, self.franchise_amount, self.currency_id.symbol)
        )

        return customer_invoice | insurance_invoice

    def _create_franchise_invoice(self, franchise_product, date=None):
        """Crea la factura al cliente SOLO con la línea de franquicia"""
        self.ensure_one()

        invoice_vals = self._prepare_invoice()
        if date:
            invoice_vals['invoice_date'] = date
        invoice_vals['ref'] = _("Franquicia - %s") % self.name
        invoice_vals['move_type'] = 'out_invoice'

        taxes = franchise_product.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        price_unit = self.franchise_amount

        # SOLO incluir la línea de franquicia
        invoice_line_vals = {
            'product_id': franchise_product.id,
            'name': franchise_product.display_name or _("Franquicia seguro"),
            'quantity': 1.0,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, taxes.ids)] if taxes else False,
        }
        invoice_vals['invoice_line_ids'] = [(0, 0, invoice_line_vals)]

        # Crear la factura
        invoice = self.env['account.move'].sudo().create(invoice_vals)

        # Vincular con el pedido
        self.invoice_ids |= invoice

        return invoice

    def _create_insurance_invoice(self, franchise_product, date=None):
        """
        Crea la factura a la aseguradora con:
        - Solo las líneas facturables (policy 'order' o entregadas)
        - Una línea negativa de franquicia para ajustar el total
        """
        self.ensure_one()

        invoice_vals = self._prepare_invoice()
        invoice_vals['partner_id'] = self.insurance_partner_id.id
        invoice_vals['move_type'] = 'out_invoice'

        # Obtener la posición fiscal del partner aseguradora
        fiscal_position = self.insurance_partner_id.property_account_position_id
        if fiscal_position:
            invoice_vals['fiscal_position_id'] = fiscal_position.id
        if date:
            invoice_vals['invoice_date'] = date
        invoice_vals['ref'] = _("Aseguradora - %s") % self.name

        invoice_line_vals_list = []
        for line in self.order_line:
            if line.display_type:
                continue
            policy = line.product_id.invoice_policy
            if policy == 'order' or (policy == 'delivered' and line.qty_delivered > 0):
                line_vals = line._prepare_invoice_line()
                if line_vals:
                    invoice_line_vals_list.append((0, 0, line_vals))

        taxes = franchise_product.taxes_id
        if fiscal_position:
            taxes = fiscal_position.map_tax(taxes)
        price_unit = -self.franchise_amount
        franchise_line_vals = {
            'product_id': franchise_product.id,
            'name': _("Descuento franquicia abonada por cliente"),
            'quantity': 1.0,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, taxes.ids)] if taxes else False,
        }
        invoice_line_vals_list.append((0, 0, franchise_line_vals))
        invoice_vals['invoice_line_ids'] = invoice_line_vals_list

        invoice = self.env['account.move'].sudo().create(invoice_vals)
        self.invoice_ids |= invoice
        return invoice

    def action_create_fsm_order(self):
        """
        Crea una orden de trabajo (FSM) desde la orden de venta y transfiere los campos
        'insurance_partner_id' y 'franchise_amount'.
        """
        self.ensure_one()
        fsm_order = self.env['fsm.order'].create({
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'insurance_partner_id': self.insurance_partner_id.id,
            'franchise_amount': self.franchise_amount,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'origin': self.name,
        })
        self.message_post(body=_("Orden de trabajo creada: %s") % fsm_order.name)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.order',
            'res_id': fsm_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
