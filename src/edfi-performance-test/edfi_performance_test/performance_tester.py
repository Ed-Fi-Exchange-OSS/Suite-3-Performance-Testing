# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import sys
import time
import gevent
from os import makedirs
from typing import Type

from locust.debug import run_single_user, User
from locust.env import Environment
from locust.stats import stats_history, StatsCSVFileWriter, PERCENTILES_TO_REPORT
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, Runner

from edfi_performance_test.helpers.main_arguments import MainArguments
from edfi_performance_test.helpers.config import set_config_values
from edfi_performance_test.tasks.pipeclean.pipeclean_tests import PipeCleanTestUser
from edfi_performance_test.tasks.volume.volume_tests import VolumeTestUser
from edfi_performance_test.helpers.test_type import TestType


logger = logging.getLogger(__name__)


def prepare_for_output(args: MainArguments) -> str:
    makedirs(args.output, exist_ok=True)
    output_base_path = f"{args.output}/{args.testType}"
    return output_base_path


def monitor_fail_ratio(runner: Runner):
    while runner.state not in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(1)
        if runner.stats.total.fail_ratio > 0.5:
            runner.quit()
            raise RuntimeError(f"fail ratio was {runner.stats.total.fail_ratio}, quitting")


def spawn_pref_tests(args: MainArguments, user_class: Type[User]) -> None:
    # setup Environment and Runner
    env = Environment(user_classes=[user_class], host=args.baseUrl)
    env.create_local_runner()

    # start a greenlet that periodically outputs the current stats

    stats_writer = StatsCSVFileWriter(
        env, PERCENTILES_TO_REPORT, prepare_for_output(args), full_history=True
    )
    gevent.spawn(stats_writer)

    # start a greenlet that saves current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the test
    if not env.runner:
        raise RuntimeError("Locust runner not configured correctly")
    runner = env.runner

    # start a greenlet that monitors fail ratio
    gevent.spawn(monitor_fail_ratio, env.runner)

    runner.start(args.clientCount, spawn_rate=args.spawnRate)

    # Manually stop locust, which otherwise would run continuously
    gevent.spawn_later(args.runTimeInMinutes * 60, lambda: runner.quit())

    # wait for the greenlets
    env.runner.greenlet.join()


def run_pipe_clean_tests(args: MainArguments) -> None:
    if(args.runInDebugMode):
        # for running tests in a debugger
        PipeCleanTestUser.host = args.baseUrl
        sys.argv = sys.argv[:1]
        run_single_user(PipeCleanTestUser)
    else:
        spawn_pref_tests(args, PipeCleanTestUser)


def run_volume_tests(args: MainArguments) -> None:
    if(args.runInDebugMode):
        # for running tests in a debugger
        VolumeTestUser.host = args.baseUrl
        sys.argv = sys.argv[:1]
        run_single_user(VolumeTestUser)
    else:
        spawn_pref_tests(args, VolumeTestUser)


def run_change_query_tests(args: MainArguments) -> None:
    pass  # TODO: implement change query tests


async def run(args: MainArguments) -> None:

    try:
        logger.info("Starting performance test...")
        start = time.time()

        set_config_values(args)

        if(args.testType == TestType.VOLUME):
            run_volume_tests(args)
        elif(args.testType == TestType.PIPECLEAN):
            run_pipe_clean_tests(args)
        elif(args.testType == TestType.CHANGE_QUERY):
            run_change_query_tests(args)

        logger.info(
            f"Finished running performance tests in {time.time() - start} seconds."
        )
    except BaseException as err:
        logger.error(err)
