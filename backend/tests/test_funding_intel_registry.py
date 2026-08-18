import importlib
import unittest

from app.funding_intel.core import registry


class FundingIntelRegistryTests(unittest.TestCase):
    def test_package_import_registers_providers(self):
        import app.funding_intel as funding_intel

        importlib.reload(funding_intel)

        providers = registry.known_providers()
        self.assertIn("nih", providers)
        self.assertIn("grants_gov", providers)
        self.assertIn("nsf", providers)


if __name__ == "__main__":
    unittest.main()
