from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fsm_order_id = fields.Many2one(
        'automocion.fsm.order',
        string='Orden de Trabajo FSM',
        help="Orden de trabajo FSM que originó esta orden de venta"
    )
    insurance_partner_id = fields.Many2one(
        'res.partner',
        string='Aseguradora',
        help='Compañía aseguradora asociada a la orden de venta.'
    )
    franchise_amount = fields.Float(
        string='Importe Franquicia',
        help='Importe de la franquicia asociada a la orden de venta.'
    )

    def _create_invoices(self, grouped=False, final=False, date=None):
        self.ensure_one()
        invoices = self.env['account.move']
        # Si hay aseguradora y franquicia, factura al cliente solo la franquicia
        if self.insurance_partner_id and self.franchise_amount:
            # Factura para el cliente: solo la franquicia
            invoice_vals_cliente = self._prepare_invoice()
            invoice_line_vals_cliente = [
                (0, 0, {
                    'name': 'Franquicia',
                    'quantity': 1,
                    'price_unit': self.franchise_amount,
                    'tax_ids': [(6, 0, self.order_line[0].tax_id.ids)] if self.order_line else [],
                })
            ]
            invoice_vals_cliente['invoice_line_ids'] = invoice_line_vals_cliente
            invoice_cliente = self.env['account.move'].create(invoice_vals_cliente)
            invoices += invoice_cliente
            # Factura para la aseguradora: todo el trabajo menos la franquicia
            invoice_vals_aseguradora = self._prepare_invoice()
            invoice_vals_aseguradora['partner_id'] = self.insurance_partner_id.id
            invoice_line_vals_aseguradora = []
            for line in self.order_line:
                invoice_line_vals_aseguradora.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, line.tax_id.ids)],
                }))
            invoice_vals_aseguradora['invoice_line_ids'] = invoice_line_vals_aseguradora
            invoice_aseguradora = self.env['account.move'].create(invoice_vals_aseguradora)
            # Añadir línea negativa de franquicia
            invoice_aseguradora.write({
                'invoice_line_ids': [(0, 0, {
                    'name': 'Franquicia',
                    'quantity': 1,
                    'price_unit': -self.franchise_amount,
                    'tax_ids': [(6, 0, self.order_line[0].tax_id.ids)] if self.order_line else [],
                })]
            })
            invoices += invoice_aseguradora
        else:
            # Si no hay aseguradora, factura estándar al cliente
            invoice_vals_cliente = self._prepare_invoice()
            invoice_line_vals_cliente = []
            for line in self.order_line:
                invoice_line_vals_cliente.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, line.tax_id.ids)],
                }))
            invoice_vals_cliente['invoice_line_ids'] = invoice_line_vals_cliente
            invoice_cliente = self.env['account.move'].create(invoice_vals_cliente)
            invoices += invoice_cliente
        return invoices
