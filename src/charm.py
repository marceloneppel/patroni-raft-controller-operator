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
        # patroni_raft_controller_relation_joined
        framework.observe(self.on.patroni_raft_controller_relation_joined, self._on_patroni_raft_controller_relation_joined)
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

    def _on_patroni_raft_controller_relation_joined(self, event: ops.RelationJoinedEvent) -> None:
        """Handle Patroni Raft Controller relation joined event."""
        if isinstance(self.unit.status, ops.ActiveStatus):
            self._set_address_in_application_relation_databag(event.relation)
        elif isinstance(self.unit.status, ops.BlockedStatus):
            logger.warning("Unit is blocked, not setting address in application relation databag on join event.")
        else:
            logger.debug("Unit is not in an expected status, not setting address in application relation databag on join event.")
            event.defer()

    def _on_start(self, _) -> None:
        """Handle start event."""
        if not isinstance(self.unit.status, ops.BlockedStatus):
            self.unit.status = ops.ActiveStatus()

    def _set_address_in_application_relation_databag(self, relation: ops.Relation) -> None:
        """Set the address in the application relation databag."""
        address = self.model.get_binding(relation).network.bind_address
        if address:
            relation.data[self.app]["address"] = str(address)
            logger.info("Set address in application relation databag: %s", address)
        else:
            logger.warning("No address found to set in application relation databag.")


if __name__ == "__main__":  # pragma: nocover
    ops.main(PatroniRaftControllerOperatorCharm)
