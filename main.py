#!/usr/bin/env python3

import json
import logging
import sys

import badsec.api

USAGE = """Usage: main.py [--help|-h]

Retrieves a list of VIP users from the Bureau of Adversarial Dossiers and
Securely Encrypted Code. Prints the list in JSON format to stdout."""

if __name__ == "__main__":

    if sys.argv[-1] in ["--help", "-h"]:
        print(USAGE)
        exit(0)

    try:
        with badsec.api.Session() as session:
            users = session.users()
            print(json.dumps(users))
    except Exception as ex:
        logging.error(ex)
        exit(1)

    exit(0)
