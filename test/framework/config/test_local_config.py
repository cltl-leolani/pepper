import os
import unittest

import importlib_resources
from enum import Enum

from pepper.framework.config.local import LocalConfigurationContainer


class TestEnum(Enum):
    VALUE = 1
    OTHER_VALUE = 2


class SynchronousEventBusTestCase(unittest.TestCase):
    def setUp(self):
        with importlib_resources.path(__package__, "test.config") as test_config:
            LocalConfigurationContainer.load_configuration(str(test_config), [])
        self.configuration_manager = LocalConfigurationContainer().config_manager

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
        self.assertEqual(TestEnum.VALUE, default_config.get_enum("enum", TestEnum))

    def test_section(self):
        default_config = self.configuration_manager.get_config("section")

        self.assertIsNotNone(default_config)
        self.assertEqual("test section", default_config.get("name"))
        self.assertEqual(["val_1", "val_2"], default_config.get("values", multi=True))
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
        self.assertEqual(TestEnum.VALUE, default_config.get_enum("enum", TestEnum))
        self.assertEqual([TestEnum.VALUE, TestEnum.OTHER_VALUE], default_config.get_enum("enums", TestEnum, multi=True))
        self.assertEqual("default/test section/True", default_config.get("interpolated"))

    def test_environment(self):
        self.assertEqual("test environment variable", os.environ['UNIT_TEST_VAR'])
