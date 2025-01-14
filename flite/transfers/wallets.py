from django.db.models import Sum
from django.db.models import Value as V
from django.db.models.functions import Coalesce

from flite.constants import TRANSACTION_STATUS, TRANSACTION_TYPE
from flite.transfers.models import BankTransfer, P2PTransfer
from flite.utils import unique_reference


class UserWallet:
    @classmethod
    def balance(cls, user):
        bank_deposits = BankTransfer.objects.filter(
            owner=user,
            status=TRANSACTION_STATUS["SUCCESS"],
            transaction_type=TRANSACTION_TYPE["CREDIT"],
        ).aggregate(payment=Coalesce(Sum("amount"), V(0.0)))["payment"]

        bank_withdraws = BankTransfer.objects.filter(
            owner=user,
            status=TRANSACTION_STATUS["SUCCESS"],
            transaction_type=TRANSACTION_TYPE["DEBIT"],
        ).aggregate(payment=Coalesce(Sum("amount"), V(0.0)))["payment"]

        received_funds = P2PTransfer.objects.filter(
            recipient=user, status=TRANSACTION_STATUS["SUCCESS"]
        ).aggregate(payment=Coalesce(Sum("amount"), V(0.0)))["payment"]

        sent_funds = P2PTransfer.objects.filter(
            sender=user, status=TRANSACTION_STATUS["SUCCESS"]
        ).aggregate(payment=Coalesce(Sum("amount"), V(0.0)))["payment"]

        p2p_transfers = received_funds - sent_funds
        bank_tansactions = bank_deposits - bank_withdraws

        return bank_tansactions + p2p_transfers

    @classmethod
    def has_enough_funds(cls, user, amount):
        return bool(cls.balance(user) >= amount)

    @classmethod
    def update_balance(cls, user, amount):
        return cls.balance(user)

    @classmethod
    def receive_bank_deposit(cls, user, amount, bank):
        reference = unique_reference(BankTransfer)
        deposit = BankTransfer.objects.create(
            owner=user,
            reference=reference,
            status=TRANSACTION_STATUS["SUCCESS"],
            transaction_type=TRANSACTION_TYPE["CREDIT"],
            amount=amount,
            bank=bank,
            new_balance=cls.update_balance(user, amount),
        )
        deposit.new_balance = cls.update_balance(user, amount)
        deposit.save()
        return deposit

    @classmethod
    def p2p_transfer(cls, sender, recipient, amount):
        reference = unique_reference(P2PTransfer)
        status = (
            TRANSACTION_STATUS["SUCCESS"]
            if cls.has_enough_funds(sender, amount)
            else TRANSACTION_STATUS["FAILED"]
        )
        transfer = P2PTransfer.objects.create(
            owner=sender,
            sender=sender,
            reference=reference,
            recipient=recipient,
            status=status,
            amount=amount,
        )
        transfer.new_balance = cls.update_balance(sender, amount)
        transfer.save()
        return transfer

    @classmethod
    def withdraw_to_bank(cls, user, amount, bank):
        reference = unique_reference(BankTransfer)
        status = (
            TRANSACTION_STATUS["SUCCESS"]
            if cls.has_enough_funds(user, amount)
            else TRANSACTION_STATUS["FAILED"]
        )
        withdrawal = BankTransfer.objects.create(
            owner=user,
            reference=reference,
            status=status,
            transaction_type=TRANSACTION_TYPE["DEBIT"],
            amount=amount,
            bank=bank,
        )
        withdrawal.new_balance = cls.update_balance(user, amount)
        withdrawal.save()
        return withdrawal
