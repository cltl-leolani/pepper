from time import sleep

from unittest import TestCase


def await(predicate, msg="predicate", max=100, sleep_interval = 0.01):
    cnt = 0
    while not predicate() and cnt < max:
        sleep(sleep_interval)
        cnt += 1

    if cnt == max:
        raise TestCase.failureException("Test timed out waiting for " + msg)