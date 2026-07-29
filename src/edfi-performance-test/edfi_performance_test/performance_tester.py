# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import os
import socket
import subprocess
import sys
import time
import gevent
from os import makedirs
from typing import List, Type

from locust import FastHttpUser
from locust.debug import run_single_user
from locust.env import Environment
from locust.log import greenlet_exception_logger
from locust.stats import stats_history, StatsCSVFileWriter, PERCENTILES_TO_REPORT
from locust.runners import (
    STATE_STOPPING,
    STATE_STOPPED,
    STATE_CLEANUP,
    MasterRunner,
    Runner,
)

from edfi_performance_test.helpers.main_arguments import MainArguments
from edfi_performance_test.helpers.config import set_config_values
from edfi_performance_test.tasks.pipeclean.pipeclean_tests import PipeCleanTestUser
from edfi_performance_test.tasks.volume.volume_tests import VolumeTestUser
from edfi_performance_test.tasks.change_query.change_query_tests import (
    ChangeQueryTestUser,
)
from edfi_performance_test.helpers.test_type import TestType


logger = logging.getLogger(__name__)


# Seconds to wait for worker processes to connect to the master before starting.
WORKER_CONNECT_TIMEOUT_SECONDS = 60
# Distributed workers always run on the same machine as the master.
_MASTER_HOST = "127.0.0.1"
# Internal coordinator-to-worker communication; not an application setting.
_MASTER_PORT_ENV = "PERF_MASTER_PORT"


def prepare_for_output(args: MainArguments) -> str:
    makedirs(args.output, exist_ok=True)
    output_base_path = f"{args.output}/{args.testType}"
    return output_base_path


def monitor_fail_ratio(runner: Runner):
    while runner.state not in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(1)
        if runner.stats.total.fail_ratio > 0.5:
            runner.quit()
            raise RuntimeError(
                f"fail ratio was {runner.stats.total.fail_ratio}, quitting"
            )


def _resolve_process_count(args: MainArguments) -> int:
    # Only the volume suite benefits from spreading load across cores.
    # Pipeclean and change-query end themselves by quitting the runner from
    # inside a user task, which does not propagate from a worker to the
    # master, so they must stay single-process.
    if args.testType != TestType.VOLUME:
        return 1
    # 0 = auto (CPU cores - 1); 1 = single-process; N > 1 = distributed.
    # Never more processes than simulated users. Full explanation in the
    # --processCount help text (helpers/argparser.py).
    requested = args.processCount
    if requested <= 0:
        requested = max(1, (os.cpu_count() or 2) - 1)
    return max(1, min(requested, args.clientCount))


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((_MASTER_HOST, 0))
        return sock.getsockname()[1]


def _start_stats_and_monitors(env: Environment, args: MainArguments) -> None:
    # Periodically write current stats to CSV (master aggregates worker stats).
    stats_writer = StatsCSVFileWriter(
        env, PERCENTILES_TO_REPORT, prepare_for_output(args), full_history=True
    )
    gevent.spawn(stats_writer)

    # Save current stats to history.
    gevent.spawn(stats_history, env.runner)

    # Stop the run early if too many requests fail.
    gevent.spawn(monitor_fail_ratio, env.runner)


def _build_worker_command(args: MainArguments) -> List[str]:
    """
    Build the command line for a worker subprocess. Arguments are passed as an
    argv list (no shell), so values with special characters are safe without
    any quoting. The API key and secret are deliberately NOT included here:
    workers inherit them through the environment (set_config_values exports
    them before workers are spawned) so they never appear in process listings.
    """
    command = [
        sys.executable,
        "-m",
        "edfi_performance_test",
        "--baseUrl", args.baseUrl,
        "--testType", str(args.testType),
        "--clientCount", str(args.clientCount),
        "--spawnRate", str(args.spawnRate),
        "--runTimeInMinutes", str(args.runTimeInMinutes),
        "--output", args.output,
        "--logLevel", str(args.log_level),
        "--apiPrefix", args.api_prefix,
        "--oauthEndpoint", args.oauth_endpoint,
        "--localEducationOrganizationId", str(args.localEducationOrganizationId),
        "--disableComposites", str(args.disableComposites),
        "--workerMode",
    ]
    if args.ignoreCertificateErrors:
        command.append("--ignoreCertificateErrors")
    if args.deleteResources:
        command.append("--deleteResources")
    if args.failDeliberately:
        command.append("--failDeliberately")
    if args.testList:
        command.append("--testList")
        command.extend(args.testList)
    return command


def _spawn_workers(
    args: MainArguments, count: int, master_port: int
) -> List[subprocess.Popen]:
    command = _build_worker_command(args)
    worker_environment = os.environ.copy()
    worker_environment[_MASTER_PORT_ENV] = str(master_port)
    processes: List[subprocess.Popen] = []
    try:
        for index in range(count):
            logger.info(f"Launching load-generator worker {index + 1}/{count}")
            processes.append(subprocess.Popen(command, env=worker_environment))
    except BaseException:
        logger.error(
            "Failed to launch all load-generator workers; "
            "terminating the ones already started."
        )
        _terminate_workers(processes)
        raise
    return processes


def _await_workers(runner: MasterRunner, expected: int) -> None:
    deadline = time.time() + WORKER_CONNECT_TIMEOUT_SECONDS
    while runner.worker_count < expected:
        if time.time() > deadline:
            raise RuntimeError(
                f"Only {runner.worker_count}/{expected} load-generator "
                f"workers connected within {WORKER_CONNECT_TIMEOUT_SECONDS} "
                "seconds; aborting. Check worker logs for startup errors."
            )
        gevent.sleep(0.5)
    logger.info(f"All {expected} load-generator workers connected.")


def _monitor_workers(
    runner: MasterRunner, processes: List[subprocess.Popen]
) -> None:
    # A worker exiting mid-run is always a crash (volume workers only exit
    # when the master tells them to), and Locust would rebalance its users
    # onto the survivors — exactly the single-core saturation distributed
    # mode exists to avoid. Fail fast instead: the ERROR log makes the run
    # exit non-zero via the ErrorHandler in __main__. Polling the child
    # processes (not runner.worker_count) avoids false positives from
    # missed heartbeats when a busy worker is slow to report in.
    while runner.state not in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        gevent.sleep(1)
        if runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
            return
        exited = [p for p in processes if p.poll() is not None]
        if exited:
            codes = ", ".join(str(p.returncode) for p in exited)
            logger.error(
                f"{len(exited)}/{len(processes)} load-generator workers "
                f"exited mid-run (exit codes: {codes}); stopping the test."
            )
            runner.quit()
            return


def _terminate_workers(processes: List[subprocess.Popen]) -> None:
    # A worker reports its own failures through its exit code: its
    # ErrorHandler (see __main__) makes it exit 1 if anything logged an error
    # during the run. Workers exit on their own shortly after the master
    # quits, so give them a grace period to harvest that signal before
    # terminating stragglers.
    grace = time.time() + 10
    failed = 0
    for process in processes:
        try:
            process.wait(timeout=max(0.0, grace - time.time()))
            if process.returncode != 0:
                failed += 1
        except subprocess.TimeoutExpired:
            process.terminate()

    # Exit codes of terminated stragglers reflect our terminate(), not test
    # failures, so they are not counted. One shared deadline keeps teardown
    # bounded regardless of worker count.
    deadline = time.time() + 10
    for process in processes:
        try:
            process.wait(timeout=max(0.0, deadline - time.time()))
        except subprocess.TimeoutExpired:
            process.kill()

    if failed:
        logger.error(
            f"{failed} of {len(processes)} load-generator workers exited "
            "with a non-zero status; check the worker errors in the log above."
        )


def _run_worker(args: MainArguments, user_class: Type[FastHttpUser]) -> None:
    """Run this process as a distributed Locust worker connected to the master."""
    try:
        master_port = int(os.environ[_MASTER_PORT_ENV])
    except KeyError as err:
        raise RuntimeError(
            f"Worker process is missing the internal {_MASTER_PORT_ENV} setting."
        ) from err
    except ValueError as err:
        raise RuntimeError(
            f"Worker process received an invalid {_MASTER_PORT_ENV} setting."
        ) from err

    logger.info(
        f"Starting load-generator worker, connecting to master at "
        f"{_MASTER_HOST}:{master_port}"
    )
    env = Environment(user_classes=[user_class], host=args.baseUrl)
    runner = env.create_worker_runner(_MASTER_HOST, master_port)
    # Workers run until the master tells them to quit.
    runner.greenlet.join()


def _run_local(args: MainArguments, user_class: Type[FastHttpUser]) -> None:
    """Single-process local runner (legacy behavior, one CPU core)."""
    env = Environment(user_classes=[user_class], host=args.baseUrl)
    env.create_local_runner()
    if not env.runner:
        raise RuntimeError("Locust runner not configured correctly")
    runner = env.runner

    _start_stats_and_monitors(env, args)

    runner.start(args.clientCount, spawn_rate=args.spawnRate)

    # Manually stop locust, which otherwise would run continuously.
    gevent.spawn_later(args.runTimeInMinutes * 60, lambda: runner.quit())

    runner.greenlet.join()


def _run_master(
    args: MainArguments, user_class: Type[FastHttpUser], process_count: int
) -> None:
    """
    Distributed runner: this process is the master, and `process_count` worker
    subprocesses generate the load so it is spread across CPU cores.
    """
    master_port = _find_free_port()

    env = Environment(user_classes=[user_class], host=args.baseUrl)
    runner = env.create_master_runner(
        master_bind_host=_MASTER_HOST, master_bind_port=master_port
    )

    worker_processes = _spawn_workers(args, process_count, master_port)
    try:
        _await_workers(runner, process_count)

        # End the run early (and fail) if any worker dies mid-run.
        gevent.spawn(_monitor_workers, runner, worker_processes)

        _start_stats_and_monitors(env, args)

        # In distributed mode clientCount and spawnRate are totals; Locust
        # distributes them across the connected workers.
        #
        # MasterRunner.start() blocks until ramp-up completes, so run it in a
        # greenlet (as locust's own headless mode does) and start the quit
        # timer now: the configured run time includes ramp-up, matching
        # single-process mode.
        gevent.spawn(
            runner.start, args.clientCount, spawn_rate=args.spawnRate
        ).link_exception(greenlet_exception_logger(logger))

        # Manually stop locust, which propagates the quit to the workers.
        gevent.spawn_later(args.runTimeInMinutes * 60, lambda: runner.quit())

        runner.greenlet.join()
    finally:
        _terminate_workers(worker_processes)


def spawn_perf_tests(args: MainArguments, user_class: Type[FastHttpUser]) -> None:
    # setup Environment and Runner

    # These tests expect that the base URL does NOT end with a slash
    if args.baseUrl.endswith("/"):
        args.baseUrl = args.baseUrl[0:(len(args.baseUrl) - 1)]

    # A process launched as a worker just connects to the master and runs.
    if args.workerMode:
        _run_worker(args, user_class)
        return

    process_count = _resolve_process_count(args)
    if process_count <= 1:
        logger.info("Running load generator in single-process mode (1 CPU core).")
        _run_local(args, user_class)
    else:
        logger.info(
            f"Running load generator across {process_count} worker processes "
            "(distributed mode)."
        )
        _run_master(args, user_class, process_count)


def run_pipe_clean_tests(args: MainArguments) -> None:
    PipeCleanTestUser.test_list = args.testList

    if args.runInDebugMode:
        # for running tests in a debugger
        PipeCleanTestUser.host = args.baseUrl
        sys.argv = sys.argv[:1]
        run_single_user(PipeCleanTestUser)
    else:
        spawn_perf_tests(args, PipeCleanTestUser)


def run_volume_tests(args: MainArguments) -> None:
    VolumeTestUser.test_list = args.testList

    if args.runInDebugMode:
        # for running tests in a debugger
        VolumeTestUser.host = args.baseUrl
        sys.argv = sys.argv[:1]
        run_single_user(VolumeTestUser)
    else:
        spawn_perf_tests(args, VolumeTestUser)


def run_change_query_tests(args: MainArguments) -> None:
    ChangeQueryTestUser.test_list = args.testList

    if args.runInDebugMode:
        # for running tests in a debugger
        ChangeQueryTestUser.host = args.baseUrl
        sys.argv = sys.argv[:1]
        run_single_user(ChangeQueryTestUser)
    else:
        spawn_perf_tests(args, ChangeQueryTestUser)


async def run(args: MainArguments) -> None:
    try:
        logger.info("Starting performance test...")
        start = time.time()

        set_config_values(args)

        if args.testType == TestType.VOLUME:
            run_volume_tests(args)
        elif args.testType == TestType.PIPECLEAN:
            run_pipe_clean_tests(args)
        elif args.testType == TestType.CHANGE_QUERY:
            run_change_query_tests(args)

        logger.info(
            f"Finished running performance tests in {time.time() - start} seconds."
        )
    except BaseException as err:
        logger.error(err)
