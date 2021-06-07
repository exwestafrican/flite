from django.db.models import Sum
from django.db.models import Value as V
from django.db.models.functions import Coalesce
from flite.banks.models import BankTransfer, P2PTransfer
from flite.constants import TRANSACTION_STATUS


class UserWallet:
    @classmethod
    def balance(cls, user):
        bank_transfers = BankTransfer.objects.filter(
            owner=user, status=TRANSACTION_STATUS["SUCCESS"]
        ).aggregate(payment=Coalesce(Sum("amount"), V(0.0)))["payment"]

        p2p_transfers = P2PTransfer.objects.filter(
            recipient=user, status=TRANSACTION_STATUS["SUCCESS"]
        ).aggregate(payment=Coalesce(Sum("amount"), V(0.0)))["payment"]

        return bank_transfers + p2p_transfers

    @classmethod
    def has_enough_funds(cls, user, amount):
        return bool(cls.balance(user) >= amount)

    @classmethod
    def update_balance(cls, amount):
        return cls.balance(user) + amount

    @classmethod
    def receive_bank_deposit(cls, user, amount):
        old_balance = cls.balance(user)
        return BankTransfer.objects.create(
            owner=user,
            reference="",
            status=TRANSACTION_STATUS["SUCCESS"],
            amount=amount,
            new_balance=update_balance(amount),
        )

    @classmethod
    def p2p_transfer(cls, sender, recipient, amount):
        status = (
            TRANSACTION_STATUS["SUCCESS"]
            if cls.has_enough_funds(sender, amount)
            else TRANSACTION_STATUS["FAILED"]
        )
        return P2PTransfer.objects.create(
            owner=sender,
            sender=sender,
            status=TRANSACTION_STATUS["SUCCESS"],
            amount=amount,
            new_balance=update_balance(amount),
            recipient=recipient,
        )
