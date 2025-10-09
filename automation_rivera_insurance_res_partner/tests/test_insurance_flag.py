# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestInsuranceFlag(TransactionCase):
    """Tests para el campo is_insurance_company en res.partner"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_create_partner_as_insurance(self):
        """Test: Crear un partner marcado como aseguradora"""
        partner = self.Partner.create(
            {
                "name": "Test Insurance Company",
                "is_company": True,
                "is_insurance_company": True,
            }
        )
        self.assertTrue(
            partner.is_insurance_company,
            "El partner debería estar marcado como aseguradora",
        )

    def test_create_partner_not_insurance(self):
        """Test: Crear un partner NO marcado como aseguradora"""
        partner = self.Partner.create(
            {
                "name": "Test Regular Company",
                "is_company": True,
                "is_insurance_company": False,
            }
        )
        self.assertFalse(
            partner.is_insurance_company,
            "El partner NO debería estar marcado como aseguradora",
        )

    def test_default_value_is_false(self):
        """Test: El valor por defecto de is_insurance_company es False"""
        partner = self.Partner.create(
            {
                "name": "Test Company Without Flag",
                "is_company": True,
            }
        )
        self.assertFalse(
            partner.is_insurance_company,
            "Por defecto, un partner NO debe ser aseguradora",
        )

    def test_search_insurance_companies(self):
        """Test: Buscar partners que son aseguradoras"""
        # Crear aseguradoras
        insurance1 = self.Partner.create(
            {
                "name": "Insurance 1",
                "is_company": True,
                "is_insurance_company": True,
            }
        )
        insurance2 = self.Partner.create(
            {
                "name": "Insurance 2",
                "is_company": True,
                "is_insurance_company": True,
            }
        )
        # Crear empresa regular
        regular = self.Partner.create(
            {
                "name": "Regular Company",
                "is_company": True,
                "is_insurance_company": False,
            }
        )

        # Buscar aseguradoras
        insurances = self.Partner.search([("is_insurance_company", "=", True)])

        self.assertIn(insurance1, insurances, "Insurance 1 debería estar en resultados")
        self.assertIn(insurance2, insurances, "Insurance 2 debería estar en resultados")
        self.assertNotIn(
            regular, insurances, "Regular Company NO debería estar en resultados"
        )

    def test_update_insurance_flag(self):
        """Test: Actualizar el flag de aseguradora"""
        partner = self.Partner.create(
            {
                "name": "Test Company",
                "is_company": True,
                "is_insurance_company": False,
            }
        )

        # Verificar valor inicial
        self.assertFalse(partner.is_insurance_company)

        # Actualizar a True
        partner.write({"is_insurance_company": True})
        self.assertTrue(
            partner.is_insurance_company, "El flag debería actualizarse a True"
        )

        # Actualizar de vuelta a False
        partner.write({"is_insurance_company": False})
        self.assertFalse(
            partner.is_insurance_company, "El flag debería actualizarse a False"
        )

    def test_filter_only_insurances(self):
        """Test: Filtro que devuelve solo aseguradoras"""
        # Crear múltiples partners
        for i in range(3):
            self.Partner.create(
                {
                    "name": f"Insurance Company {i}",
                    "is_company": True,
                    "is_insurance_company": True,
                }
            )

        for i in range(5):
            self.Partner.create(
                {
                    "name": f"Regular Company {i}",
                    "is_company": True,
                    "is_insurance_company": False,
                }
            )

        # Contar aseguradoras
        insurance_count = self.Partner.search_count(
            [("is_insurance_company", "=", True)]
        )

        self.assertGreaterEqual(
            insurance_count,
            3,
            "Debería haber al menos 3 aseguradoras (las que creamos)",
        )

    def test_field_exists_in_model(self):
        """Test: El campo is_insurance_company existe en el modelo"""
        self.assertIn(
            "is_insurance_company",
            self.Partner._fields,
            "El campo is_insurance_company debería existir en res.partner",
        )

    def test_field_is_boolean(self):
        """Test: El campo is_insurance_company es de tipo Boolean"""
        field = self.Partner._fields["is_insurance_company"]
        self.assertEqual(
            field.type,
            "boolean",
            "El campo is_insurance_company debería ser de tipo boolean",
        )
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import models

