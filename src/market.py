from typing import Set

from src.resource import Resource, Transaction, ResourceHaver
from src.player import Player
from src.board import Board
from src import error


class Trade:
    def __init__(self, seller_proposal: Transaction):
        self.seller_proposal = seller_proposal

    def execute(self, seller: ResourceHaver, buyer: ResourceHaver):
        if not seller.can_transact(self.seller_proposal):
            raise error.InvalidAction("Seller too poor")
        if not buyer.can_transact(self.seller_proposal.inverse()):
            raise error.InvalidAction("Buyer too poor")

        seller.transact(self.seller_proposal)
        buyer.transact(self.seller_proposal.inverse())


class Bank(ResourceHaver):
    def __init__(self, inventory: int = 19):
        super().__init__()
        self.transact(Transaction({resource: inventory for resource in Resource}))

        self.four_to_ones = set()
        for resource1 in Resource:
            for resource2 in Resource:
                if resource1 == resource2:
                    continue

                transaction = Transaction({
                    resource1: -4,
                    resource2: 1,
                })
                if not self.can_transact(transaction.inverse()):
                    continue
                self.four_to_ones.add(transaction)

    def available_transactions(self, board: Board, player: Player) -> Set[Transaction]:
        return self.four_to_ones
