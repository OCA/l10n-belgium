# Copyright 2024 ACSONE SA/NV


def migrate(cr, version):
    cr.execute(
        "UPDATE account_move SET reference_type='structured' "
        "WHERE reference_type='bba'"
    )
    cr.execute(
        "UPDATE account_payment_line SET communication_type='structured' "
        "WHERE communication_type='bba'"
    )
