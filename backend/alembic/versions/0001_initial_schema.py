"""Початкова схема: users, orders, order_status_history.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-21
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Типи-перелічення створюються один раз явно. Далі колонки посилаються на них
# із create_type=False, інакше PostgreSQL отримав би CREATE TYPE двічі.
user_role = postgresql.ENUM(
    "ADMIN",
    "DISPATCHER",
    "COURIER",
    "CUSTOMER",
    name="user_role",
)
package_size = postgresql.ENUM("SMALL", "MEDIUM", "LARGE", name="package_size")
delivery_type = postgresql.ENUM("STANDARD", "EXPRESS", name="delivery_type")
order_status = postgresql.ENUM(
    # Використовуються в частині 1
    "CREATED",
    "CONFIRMED",
    "WAITING_FOR_COURIER",
    "CANCELLED",
    # Зарезервовано для частини 2
    "COURIER_ASSIGNED",
    "PICKED_UP",
    "IN_TRANSIT",
    "DELIVERED",
    "DELIVERY_FAILED",
    name="order_status",
)

_user_role = postgresql.ENUM(name="user_role", create_type=False)
_package_size = postgresql.ENUM(name="package_size", create_type=False)
_delivery_type = postgresql.ENUM(name="delivery_type", create_type=False)
_order_status = postgresql.ENUM(name="order_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    package_size.create(bind, checkfirst=True)
    delivery_type.create(bind, checkfirst=True)
    order_status.create(bind, checkfirst=True)

    # --- Лічильник номерів відстеження ---
    op.create_table(
        "order_tracking_counters",
        sa.Column("year", sa.Integer(), nullable=False, autoincrement=False),
        sa.Column("last_number", sa.BigInteger(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("year", name=op.f("pk_order_tracking_counters")),
    )

    # --- Користувачі ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=False),
        sa.Column("last_name", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", _user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)
    op.create_index(
        "ix_users_last_name_first_name", "users", ["last_name", "first_name"], unique=False
    )
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    # --- Замовлення ---
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tracking_number", sa.String(length=32), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("sender_name", sa.String(length=160), nullable=False),
        sa.Column("sender_phone", sa.String(length=32), nullable=False),
        sa.Column("pickup_address", sa.String(length=300), nullable=False),
        sa.Column("recipient_name", sa.String(length=160), nullable=False),
        sa.Column("recipient_phone", sa.String(length=32), nullable=False),
        sa.Column("delivery_address", sa.String(length=300), nullable=False),
        sa.Column("package_description", sa.String(length=500), nullable=False),
        sa.Column("package_weight", sa.Numeric(precision=7, scale=3), nullable=False),
        sa.Column("package_size", _package_size, nullable=False),
        sa.Column("delivery_type", _delivery_type, nullable=False),
        sa.Column("desired_delivery_date", sa.Date(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", _order_status, nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("package_weight > 0", name=op.f("ck_orders_package_weight_positive")),
        sa.CheckConstraint(
            "pickup_address <> delivery_address", name=op.f("ck_orders_addresses_must_differ")
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["users.id"],
            name=op.f("fk_orders_customer_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
    )
    op.create_index(op.f("ix_orders_customer_id"), "orders", ["customer_id"], unique=False)
    op.create_index(
        "ix_orders_customer_id_status", "orders", ["customer_id", "status"], unique=False
    )
    op.create_index(op.f("ix_orders_delivery_type"), "orders", ["delivery_type"], unique=False)
    op.create_index(
        op.f("ix_orders_desired_delivery_date"), "orders", ["desired_delivery_date"], unique=False
    )
    op.create_index(op.f("ix_orders_recipient_phone"), "orders", ["recipient_phone"], unique=False)
    op.create_index(op.f("ix_orders_sender_phone"), "orders", ["sender_phone"], unique=False)
    op.create_index(op.f("ix_orders_status"), "orders", ["status"], unique=False)
    op.create_index("ix_orders_status_created_at", "orders", ["status", "created_at"], unique=False)
    op.create_index(op.f("ix_orders_tracking_number"), "orders", ["tracking_number"], unique=True)

    # --- Історія статусів ---
    op.create_table(
        "order_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("previous_status", _order_status, nullable=True),
        sa.Column("new_status", _order_status, nullable=False),
        sa.Column("changed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["users.id"],
            name=op.f("fk_order_status_history_changed_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_order_status_history_order_id_orders"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_status_history")),
    )
    op.create_index(
        op.f("ix_order_status_history_changed_by_user_id"),
        "order_status_history",
        ["changed_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_order_status_history_order_id"),
        "order_status_history",
        ["order_id"],
        unique=False,
    )
    op.create_index(
        "ix_order_status_history_order_id_created_at",
        "order_status_history",
        ["order_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_order_status_history_order_id_created_at", table_name="order_status_history"
    )
    op.drop_index(op.f("ix_order_status_history_order_id"), table_name="order_status_history")
    op.drop_index(
        op.f("ix_order_status_history_changed_by_user_id"), table_name="order_status_history"
    )
    op.drop_table("order_status_history")

    op.drop_index(op.f("ix_orders_tracking_number"), table_name="orders")
    op.drop_index("ix_orders_status_created_at", table_name="orders")
    op.drop_index(op.f("ix_orders_status"), table_name="orders")
    op.drop_index(op.f("ix_orders_sender_phone"), table_name="orders")
    op.drop_index(op.f("ix_orders_recipient_phone"), table_name="orders")
    op.drop_index(op.f("ix_orders_desired_delivery_date"), table_name="orders")
    op.drop_index(op.f("ix_orders_delivery_type"), table_name="orders")
    op.drop_index("ix_orders_customer_id_status", table_name="orders")
    op.drop_index(op.f("ix_orders_customer_id"), table_name="orders")
    op.drop_table("orders")

    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.drop_index("ix_users_last_name_first_name", table_name="users")
    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_table("order_tracking_counters")

    bind = op.get_bind()
    order_status.drop(bind, checkfirst=True)
    delivery_type.drop(bind, checkfirst=True)
    package_size.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
