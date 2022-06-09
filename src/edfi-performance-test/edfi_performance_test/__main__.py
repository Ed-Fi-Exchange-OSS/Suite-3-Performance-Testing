# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.
import asyncio

from dotenv import load_dotenv
from edfi_performance_test.helpers.argparser import parse_main_arguments


async def main() -> None:

    load_dotenv()
    configuration = parse_main_arguments()

    print(configuration.baseUrl)
    print(configuration.failDeliberately)
    print(configuration.ignoreCertificateErrors)


if __name__ == "__main__":
    asyncio.run(main())
