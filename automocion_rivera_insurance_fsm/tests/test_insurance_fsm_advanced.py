# Copyright 2025 Xtendoo Software SLU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestInsuranceFSMAdvanced(TransactionCase):
    """Tests avanzados para casos edge del módulo"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id

        cls.customer = cls.env['res.partner'].create({
            'name': 'Cliente Avanzado',
        })

        cls.insurance = cls.env['res.partner'].create({
            'name': 'Aseguradora Avanzada',
            'is_insurance': True,
        })

        cls.stage = cls.env['fsm.stage'].search([], limit=1)
        if not cls.stage:
            cls.stage = cls.env['fsm.stage'].create({
                'name': 'Nueva',
                'code': 'new',
            })

        cls.product = cls.env['product.product'].create({
            'name': 'Producto Avanzado',
            'type': 'service',
            'list_price': 500.0,
        })

        # Crear impuestos con diferentes características
        cls.tax_normal = cls.env['account.tax'].create({
            'name': 'IVA 21%',
            'amount': 21.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
        })

        cls.tax_reduced = cls.env['account.tax'].create({
            'name': 'IVA 10%',
            'amount': 10.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
        })

    def test_domain_insurance_partner(self):
        """Test que el dominio de insurance_partner_id funciona"""
        fsm_order = self.env['fsm.order'].create({
            'partner_id': self.customer.id,
            'description': 'Test',
            'stage_id': self.stage.id,
        })

        # El dominio debería filtrar solo aseguradoras
        domain = fsm_order._fields['insurance_partner_id'].domain
        self.assertEqual(domain, [('is_insurance', '=', True)])

    def test_franchise_zero_no_split(self):
        """Test que franquicia = 0 no genera split"""
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 0.0,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 500.0,
            })],
        })

        self.assertFalse(so.has_insurance_split)
        so.action_confirm()
        invoices = so._create_invoices()

        # Solo debe haber 1 factura (sin split)
        self.assertEqual(len(invoices), 1)

    def test_franchise_equals_total(self):
        """Test cuando la franquicia es igual al total"""
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 500.0,
            })],
        })

        so.action_confirm()
        # Franquicia = total
        so.write({'franchise_amount': so.amount_total})

        invoices = so._create_invoices()

        # Deben ser 2 facturas
        self.assertEqual(len(invoices), 2)

        customer_invoice = invoices.filtered(lambda i: i.partner_id == self.customer)
        insurance_invoice = invoices.filtered(lambda i: i.partner_id == self.insurance)

        # La factura del cliente debe ser el total
        self.assertAlmostEqual(
            customer_invoice.amount_total,
            so.amount_total,
            places=2
        )

        # La factura de la aseguradora debe ser ~0
        self.assertAlmostEqual(
            insurance_invoice.amount_total,
            0.0,
            places=2
        )

    def test_mixed_taxes_in_lines(self):
        """Test con diferentes impuestos en las líneas"""
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 100.0,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 200.0,
                    'tax_id': [(6, 0, [self.tax_normal.id])],
                }),
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 200.0,
                    'tax_id': [(6, 0, [self.tax_reduced.id])],
                }),
            ],
        })

        so.action_confirm()
        invoices = so._create_invoices()

        self.assertEqual(len(invoices), 2)

        # Validar que la suma es correcta
        total_invoices = sum(invoices.mapped('amount_total'))
        self.assertAlmostEqual(
            total_invoices,
            so.amount_total,
            places=2
        )

    def test_invoice_messages_in_chatter(self):
        """Test que se crean mensajes en el chatter"""
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 50.0,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 500.0,
            })],
        })

        so.action_confirm()

        # Contar mensajes antes
        messages_before = len(so.message_ids)

        invoices = so._create_invoices()

        # Contar mensajes después
        messages_after = len(so.message_ids)

        # Debe haber al menos 1 mensaje nuevo
        self.assertGreater(messages_after, messages_before)

    def test_invoice_origin_field(self):
        """Test que las facturas tienen el origen correcto"""
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 50.0,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 500.0,
            })],
        })

        so.action_confirm()
        invoices = so._create_invoices()

        # Ambas facturas deben tener el origen = nombre del pedido
        for invoice in invoices:
            self.assertEqual(invoice.invoice_origin, so.name)

    def test_currency_field_in_fsm(self):
        """Test que el campo currency_id existe en FSM"""
        fsm_order = self.env['fsm.order'].create({
            'partner_id': self.customer.id,
            'description': 'Test',
            'stage_id': self.stage.id,
        })

        # Debe tener la moneda de la compañía por defecto
        self.assertEqual(fsm_order.currency_id, self.company.currency_id)

