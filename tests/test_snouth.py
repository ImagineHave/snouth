# -*- coding: utf-8 -*-
"""
    Snouth Tests
    ~~~~~~~~~~~~
    Tests the Snouth application.
    :copyright: (c) 2018 by Imagine-have.
    :license: BSD, see LICENSE for more details.
"""

import os
import tempfile
import pytest
from snouth_package import snouth_module

@pytest.fixture
def client():
    db_fd, snouth_module.snouth_instance.config['DATABASE'] = tempfile.mkstemp()
    snouth_module.snouth_instance.config['TESTING'] = True
    client = snouth_module.snouth_instance.test_client()

    with snouth_module.snouth_instance.app_context():
        snouth_module.init_db()

    yield client

    os.close(db_fd)
    os.unlink(snouth_module.snouth_instance.config['DATABASE'])