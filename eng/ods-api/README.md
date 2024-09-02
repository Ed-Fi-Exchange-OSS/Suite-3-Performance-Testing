# ODS-API Startup Scripts for Docker

This directory contains startup scripts for the ODS/API running in Docker, using
versions 5.3, 5.4, 6.1, and 6.2; and another that supports versions 7.1, 7.2,
Docker Compose for orchestration. There are two scripts: one that supports
and 7.3 (prerelease).

> [!WARNING]
> These are poorly secured environments and should not be exposed over the open
> Internet: using default passwords available in open source code, and does not
> use TLS encryption.

In each respective directory, copy the `.env.example` file to `.env`. Review the
`TAG` variable to determine which version you wish to run. Then run `start.ps1`
to startup the containers and run a bootstrap SQL script that will inject the
sample `client_id` and `client_secret` into the database. Note that the
`client_id` is given access to education organization id 255901.

To stop the services, run `start.ps1 -d` (for "down") or `start.ps1 -d -v` to
stop and remove volumes.
