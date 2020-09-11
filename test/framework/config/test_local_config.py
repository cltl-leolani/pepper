import unittest

from pepper.framework.config.local import LocalConfigurationContainer


class SynchronousEventBusTestCase(unittest.TestCase):
    def setUp(self):
        container = LocalConfigurationContainer()
        container.load_configuration("./test.config")
        self.configuration_manager = container.config_manager

    def test_defaults(self):
        default_config = self.configuration_manager.get_config("DEFAULT")

        self.assertIsNotNone(default_config)
        self.assertEqual("test default", default_config.get("name"))
        self.assertEqual(2, default_config.get_int("int"))
        self.assertEqual(1.5, default_config.get_float("float"))
        self.assertEqual(True, default_config.get_boolean("bool"))
        self.assertEqual(True, default_config.get_boolean("bool_one"))
        self.assertEqual(True, default_config.get_boolean("bool_true"))
        self.assertEqual(True, default_config.get_boolean("bool_yes"))
        self.assertEqual(True, default_config.get_boolean("bool_on"))
        self.assertEqual(False, default_config.get_boolean("bool_zero"))
        self.assertEqual(False, default_config.get_boolean("bool_false"))
        self.assertEqual(False, default_config.get_boolean("bool_no"))
        self.assertEqual(False, default_config.get_boolean("bool_off"))

    def test_section(self):
        default_config = self.configuration_manager.get_config("section")

        self.assertIsNotNone(default_config)
        self.assertEqual("test section", default_config.get("name"))
        self.assertEqual(3, default_config.get_int("int"))
        self.assertEqual(2.5, default_config.get_float("float"))
        self.assertEqual(True, default_config.get_boolean("bool"))
        self.assertEqual(True, default_config.get_boolean("bool_one"))
        self.assertEqual(True, default_config.get_boolean("bool_true"))
        self.assertEqual(True, default_config.get_boolean("bool_yes"))
        self.assertEqual(True, default_config.get_boolean("bool_on"))
        self.assertEqual(False, default_config.get_boolean("bool_zero"))
        self.assertEqual(False, default_config.get_boolean("bool_false"))
        self.assertEqual(False, default_config.get_boolean("bool_no"))
        self.assertEqual(False, default_config.get_boolean("bool_off"))
        self.assertEqual("default/test section/True", default_config.get("interpolated"))
