#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed Machine Operator for the Patroni Raft Controller."""

import logging

import ops
from charms.operator_libs_linux.v2 import snap

logger = logging.getLogger(__name__)


class PatroniRaftControllerOperatorCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.install, self._on_install)
        framework.observe(self.on.start, self._on_start)

    def _on_install(self, _) -> None:
        """Handle install event."""
        self.unit.status = ops.MaintenanceStatus("Installing Patroni Raft Controller")
        try:
            cache = snap.SnapCache()
            patroni_raft_controller = cache["neppel-charmed-patroni-raft-controller"]

            if not patroni_raft_controller.present:
                patroni_raft_controller.ensure(snap.SnapState.Latest, channel="edge")
        except snap.SnapError as e:
            logger.error(
                "An exception occurred when installing Patroni Raft Controller. Reason: %s",
                e.message,
            )
            self.unit.status = ops.BlockedStatus("Failed to install Patroni Raft Controller")
        else:
            logger.info("Patroni Raft Controller installed.")
            self.unit.status = ops.WaitingStatus("Waiting for charm initialisation")

    def _on_start(self, _) -> None:
        """Handle start event."""
        if not isinstance(self.unit.status, ops.BlockedStatus):
            self.unit.status = ops.ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(PatroniRaftControllerOperatorCharm)
