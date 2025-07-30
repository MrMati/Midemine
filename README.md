# Midemine

This project aims to create a full DRM ecosystem inspired by real world solutions.

It consists of:
- media packaging tools
- license server
- CDM

Sample player and content platform are provided too.

## Setup

Currently using single virtual environment for all parties.
Separation will happen when codebase stabilizes.

Currently, the only secrets in use are for JWT authentication.
These secrets are stored in .env files, which can be generated using theh `gen_secrets.py` script.
This script is intended to run automatically after uv sync, but this functionality is not yet supported [#9645](https://github.com/astral-sh/uv/issues/9645).