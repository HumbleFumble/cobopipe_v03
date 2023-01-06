import unittest
from sys import modules
from Log.CoboLoggers import getLogger, setConsoleLevel
from Log.Strategies import COMP_CONTACT_SHEET, DEFAULT, ASSET_BROWSER


class TestCoboLoggers(unittest.TestCase):

    def setUp(self):
        self.logger = None

    def tearDown(self):
        print("\n")
        del modules["logging"]
        with open(self.logger.handlers[1].file_name, "w+") as f:
            f.flush()

    def test_getLogger_setConsoleLevel_debug(self):
        self.logger = getLogger()
        self.assertEqual(30, self.logger.handlers[0].level)
        self.assertEqual(10, self.logger.handlers[1].level)
        setConsoleLevel(self.logger, 10)
        self.assertEqual(10, self.logger.handlers[0].level)
        self.assertEqual(10, self.logger.handlers[1].level)

        self.logger.debug("THIS IS A DEBUG")
        self.logger.warning("THIS IS A WARNING")

        with open(self.logger.handlers[1].file_name, "r") as f:
            act = f.read()
            print(act)
            self.assertIn("test_CoboLoggers.test_getLogger_setConsoleLevel_debug - DEBUG: <THIS IS A DEBUG>", act)
            self.assertIn("test_CoboLoggers.test_getLogger_setConsoleLevel_debug - WARNING: <THIS IS A WARNING>", act)
            f.flush()

    def test_getLogger_setConsoleLevel_warning(self):
        self.logger = getLogger()
        self.assertEqual(30, self.logger.handlers[0].level)
        self.assertEqual(10, self.logger.handlers[1].level)

        self.logger.debug("THIS IS A DEBUG")
        self.logger.warning("THIS IS A WARNING")

        with open(self.logger.handlers[1].file_name, "r") as f:
            act = f.read()
            print(act)
            self.assertIn("test_CoboLoggers.test_getLogger_setConsoleLevel_warning - DEBUG: <THIS IS A DEBUG>", act)
            self.assertIn("test_CoboLoggers.test_getLogger_setConsoleLevel_warning - WARNING: <THIS IS A WARNING>", act)
            f.flush()

    def test_getLogger_inheritance_basic(self):
        self.logger = getLogger()
        child_logger1 = getLogger(name="child1")
        child_logger2 = getLogger(name="child2")

        self.logger.debug("This is the main log!")
        child_logger1.debug("This is the child1 log!")
        child_logger2.debug("This is the child2 log!")

        # Check that the objects are in fact different
        self.assertNotEqual(child_logger1, child_logger2)
        self.assertNotEqual(self.logger, child_logger2)
        self.assertNotEqual(child_logger1, self.logger)

    def test_getLogger_inheritance_sameness(self):
        main = getLogger()
        child_logger1 = getLogger(name="child")
        child_logger2 = getLogger(name="child")

        child_logger1.debug("This is the child log!")
        child_logger2.debug("This is the same log!")

        # Check that the objects are in fact identical
        self.assertEqual(child_logger1, child_logger2)
        self.assertNotEqual(main, child_logger2)
        self.assertEqual("MainLogger.child", child_logger1.name)

    def test_getLogger_main_after_inheritance(self):
        # If a child is attempted created before the main object is created, -
        # the main object will be created beside the child.
        child_logger = getLogger(name="child")
        main = getLogger()

        child_logger.debug("This IS child log! :D")
        main.debug("This IS the main log! :D")

        # Check that the objects are in fact NOT identical
        self.assertNotEqual(main, child_logger)
        self.assertEqual("MainLogger.child", child_logger.name)
        self.assertEqual("MainLogger", main.name)

    def test_no_main_logger(self):
        # If a child is attempted created before the main object is created, -
        # the main object will be created beside the child, EVEN if the main object is never called.
        logger = getLogger(name="child")

        logger.debug("This IS the child log! :D")

        self.assertEqual(logger.name, "MainLogger.child")

    def test_reject_symbols_in_name(self):
        # If a logger is named with any of the following symbols \/:*?"<>| it should fail in creation
        # and result in a NameError exception.
        with self.assertRaises(NameError):
            getLogger(name="\\")
        with self.assertRaises(NameError):
            getLogger(name="/")
        with self.assertRaises(NameError):
            getLogger(name=":")
        with self.assertRaises(NameError):
            getLogger(name="*")
        with self.assertRaises(NameError):
            getLogger(name="?")
        with self.assertRaises(NameError):
            getLogger(name="\"")
        with self.assertRaises(NameError):
            getLogger(name="<")
        with self.assertRaises(NameError):
            getLogger(name=">")
        with self.assertRaises(NameError):
            getLogger(name="|")

    def test_logger_child_override(self):
        getLogger()
        child = getLogger(name="child", log_strategy=COMP_CONTACT_SHEET)
        self.assertEqual("COMP_CONTACT_SHEET", child.strategy.__name__)

        # THIS CAUSES PROBLEMS!!! DUPLICATE?
        child = getLogger(name="child", log_strategy=DEFAULT)
        self.assertEqual("DEFAULT", child.strategy.__name__)

        child.debug("This is the child logger.")

    def test_logger_override_child_strategy(self):
        # If the main logger has a specific logging strategy (from the strategies module) and the child logger has -
        # a different strategy, the child logger will keep its own strategy setting
        main_logger = getLogger(log_strategy=COMP_CONTACT_SHEET)
        child_logger = getLogger(name="child", log_strategy=DEFAULT)

        main_logger.debug("Hello World")
        child_logger.debug("Hello World")

        self.assertEqual("COMP_CONTACT_SHEET", main_logger.strategy.__name__)
        self.assertEqual("DEFAULT", child_logger.strategy.__name__)

    def test_logger_strategy_inheritance(self):
        # If the main logger has a specific logging strategy (from the strategies module) child loggers will inherit -
        # the strategy of the main logger
        main_logger = getLogger(log_strategy=COMP_CONTACT_SHEET)
        child_logger = getLogger("child")

        main_logger.debug("This is the main logger")
        child_logger.debug("This is the child logger")

        self.assertEqual("COMP_CONTACT_SHEET", main_logger.strategy.__name__)
        self.assertEqual("COMP_CONTACT_SHEET", child_logger.strategy.__name__)

    def test_strategy_comp_contact_sheet(self):
        main_logger = getLogger(log_strategy=COMP_CONTACT_SHEET)
        child_logger = getLogger("child")
        for i in range(100):
            main_logger.info("Hello World" + str(i))
            child_logger.info("Hello World" + str(i))
