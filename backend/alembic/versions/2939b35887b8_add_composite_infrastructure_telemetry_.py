
"""Add composite infrastructure telemetry index."""

from alembic import op


# Revision identifiers.
revision = "2939b35887b8"
down_revision = "18a857e480e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create an index for bridge-specific chronological queries."""

    op.create_index(
        "idx_infra_node_recorded",
        "infrastructure_telemetry",
        ["node_id", "recorded_at"],
        unique=False,
        postgresql_ops={"recorded_at": "DESC"},
    )


def downgrade() -> None:
    """Remove the composite index."""

    op.drop_index(
        "idx_infra_node_recorded",
        table_name="infrastructure_telemetry",
    )