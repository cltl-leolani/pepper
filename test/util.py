from time import sleep

from unittest import TestCase

from pepper.framework.infra.config.api import Configuration


class TestConfiguration(Configuration):
    def __init__(self, configuration_dict):
        self._dict = configuration_dict

    def get(self, key, multi=False):
        return self._dict.get(key)

    def get_int(self, key):
        return self.get(key)

    def get_float(self, key):
        return self.get(key)

    def get_boolean(self, key):
        return self.get(key)

    def get_enum(self, key, type, multi=False):
        return self.get(key)


def await_predicate(predicate, msg="predicate", max=100, sleep_interval = 0.01):
    cnt = 0
    while not predicate() and cnt < max:
        sleep(sleep_interval)
        cnt += 1

    if cnt == max:
        raise TestCase.failureException("Test timed out waiting for " + msg)