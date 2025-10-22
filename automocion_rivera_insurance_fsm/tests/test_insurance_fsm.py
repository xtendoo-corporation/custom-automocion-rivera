# Copyright 2025 Xtendoo Software SLU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestInsuranceFSM(TransactionCase):
    """Tests básicos del módulo automocion_rivera_insurance_fsm"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.currency = cls.company.currency_id

        # Crear contactos
        cls.customer = cls.env['res.partner'].create({
            'name': 'Cliente Test',
            'is_insurance': False,
        })

        cls.insurance = cls.env['res.partner'].create({
            'name': 'Aseguradora Test',
            'is_insurance': True,
        })

        # Crear etapa FSM
        cls.stage = cls.env['fsm.stage'].search([], limit=1)
        if not cls.stage:
            cls.stage = cls.env['fsm.stage'].create({
                'name': 'Nueva',
                'code': 'new',
            })

        # Obtener producto de franquicia
        cls.franchise_product = cls.env.ref(
            'automocion_rivera_insurance_fsm.product_franchise'
        )

        # Crear producto de servicio para pruebas
        cls.service_product = cls.env['product.product'].create({
            'name': 'Servicio Test',
            'type': 'service',
            'list_price': 100.0,
            'invoice_policy': 'order',
        })

        # Obtener impuesto por defecto
        cls.tax = cls.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', cls.company.id),
        ], limit=1)

        if not cls.tax:
            cls.tax = cls.env['account.tax'].create({
                'name': 'IVA 21% Test',
                'amount': 21.0,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'company_id': cls.company.id,
            })

        cls.service_product.taxes_id = [(6, 0, [cls.tax.id])]

    def test_01_partner_is_insurance(self):
        """Test que el campo is_insurance funciona correctamente"""
        self.assertTrue(self.insurance.is_insurance)
        self.assertFalse(self.customer.is_insurance)

    def test_02_fsm_order_insurance_fields(self):
        """Test campos de seguro en orden FSM"""
        fsm_order = self.env['fsm.order'].create({
            'partner_id': self.customer.id,
            'description': 'Reparación test',
            'stage_id': self.stage.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 50.0,
        })

        self.assertEqual(fsm_order.insurance_partner_id, self.insurance)
        self.assertEqual(fsm_order.franchise_amount, 50.0)
        self.assertTrue(fsm_order.currency_id)

    def test_03_fsm_franchise_negative_constraint(self):
        """Test que no se puede poner franquicia negativa en FSM"""
        with self.assertRaises(ValidationError):
            self.env['fsm.order'].create({
                'partner_id': self.customer.id,
                'description': 'Reparación test',
                'stage_id': self.stage.id,
                'insurance_partner_id': self.insurance.id,
                'franchise_amount': -10.0,
            })

    def test_04_sale_order_has_insurance_split(self):
        """Test cálculo de has_insurance_split"""
        # Sin seguro ni franquicia
        so1 = self.env['sale.order'].create({
            'partner_id': self.customer.id,
        })
        self.assertFalse(so1.has_insurance_split)

        # Con seguro pero sin franquicia
        so2 = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 0.0,
        })
        self.assertFalse(so2.has_insurance_split)

        # Con seguro y franquicia
        so3 = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 50.0,
        })
        self.assertTrue(so3.has_insurance_split)

    def test_05_franchise_amount_constraints(self):
        """Test validaciones de franchise_amount en pedido"""
        # Franquicia negativa
        with self.assertRaises(ValidationError):
            self.env['sale.order'].create({
                'partner_id': self.customer.id,
                'insurance_partner_id': self.insurance.id,
                'franchise_amount': -10.0,
            })

    def test_06_invoice_split_basic(self):
        """Test básico de split de facturación"""
        # Crear pedido con línea
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'insurance_partner_id': self.insurance.id,
            'franchise_amount': 50.0,
            'order_line': [(0, 0, {
                'product_id': self.service_product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
                'tax_id': [(6, 0, [self.tax.id])],
            })],
        })

        sale_order.action_confirm()

        # Crear facturas
        invoices = sale_order._create_invoices()

        # Debe haber 2 facturas
        self.assertEqual(len(invoices), 2)

        # Una para el cliente, otra para la aseguradora
        customer_invoice = invoices.filtered(
            lambda i: i.partner_id == self.customer
        )
        insurance_invoice = invoices.filtered(
            lambda i: i.partner_id == self.insurance
        )

        self.assertEqual(len(customer_invoice), 1)
        self.assertEqual(len(insurance_invoice), 1)

        # Validar totales (aproximadamente)
        total_so = sale_order.amount_total
        total_customer = customer_invoice.amount_total
        total_insurance = insurance_invoice.amount_total

        # La suma debe ser aproximadamente igual al total
        self.assertAlmostEqual(
            total_customer + total_insurance,
            total_so,
            places=2,
            msg="La suma de las facturas debe coincidir con el total del pedido"
        )

    def test_07_invoice_without_insurance(self):
        """Test que pedidos sin seguro se facturan normalmente"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.service_product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
                'tax_id': [(6, 0, [self.tax.id])],
            })],
        })

        sale_order.action_confirm()
        invoices = sale_order._create_invoices()

        # Solo debe haber 1 factura
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices.partner_id, self.customer)

