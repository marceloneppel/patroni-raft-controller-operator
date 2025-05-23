# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

from ops import testing

from charm import PatroniRaftControllerOperatorCharm


def test_start():
    # Arrange:
    ctx = testing.Context(PatroniRaftControllerOperatorCharm)
    # Act:
    state_out = ctx.run(ctx.on.start(), testing.State())
    # Assert:
    assert state_out.unit_status == testing.ActiveStatus()
