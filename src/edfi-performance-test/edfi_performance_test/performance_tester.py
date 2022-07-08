# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import time
import gevent
from os import makedirs

# from locust.debug import run_single_user # for running tests in a debugger
from locust.env import Environment
from locust.stats import stats_history, StatsCSVFileWriter, PERCENTILES_TO_REPORT

from edfi_performance_test.helpers.main_arguments import MainArguments
from edfi_performance_test.helpers.config import set_config_values
from edfi_performance_test.tasks.pipeclean.pipeclean_tests import DummyUser

logger = logging.getLogger(__name__)


def prepare_for_output(args: MainArguments) -> str:
    makedirs(args.output, exist_ok=True)
    output_base_path = f"{args.output}/pipeclean"
    return output_base_path


async def run(args: MainArguments) -> None:

    try:
        logger.info("Starting performance test...")
        start = time.time()

        set_config_values(args)

        # setup Environment and Runner
        env = Environment(user_classes=[DummyUser], host=args.baseUrl)
        env.create_local_runner()

        # start a WebUI instance
        env.create_web_ui("127.0.0.1", 8089)

        # start a greenlet that periodically outputs the current stats

        stats_writer = StatsCSVFileWriter(
            env, PERCENTILES_TO_REPORT, prepare_for_output(args), full_history=True
        )
        gevent.spawn(stats_writer)

        # start a greenlet that save current stats to history
        gevent.spawn(stats_history, env.runner)

        # start the test
        if not env.runner:
            raise RuntimeError("Locust runner not configured correctly")
        runner = env.runner

        runner.start(args.clientCount, spawn_rate=args.spawnRate)

        # Manually stop locust, which otherwise would run continuously
        gevent.spawn_later(args.runTimeInMinutes * 60, lambda: runner.quit())

        # wait for the greenlets
        env.runner.greenlet.join()

        # stop the web server for good measures
        if env.web_ui:
            env.web_ui.stop()

        # for running tests in a debugger
        # run_single_user(DummyUser)

        logger.info(
            f"Finished running performance tests in {time.time() - start} seconds."
        )
    except BaseException as err:
        logger.error(err)
