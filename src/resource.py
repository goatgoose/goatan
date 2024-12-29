from enum import Enum
from typing import Dict, Self
from abc import ABC, abstractmethod


class Resource(Enum):
    BRICK = "brick"
    STONE = "stone"
    WHEAT = "wheat"
    SHEEP = "sheep"
    WOOD = "wood"


class Transaction:
    def __init__(self, resources: Dict[Resource, int]):
        self.resources = resources

    def inverse(self) -> Self:
        resources = self.resources.copy()
        for resource in resources:
            resources[resource] *= -1
        return Transaction(resources)


class ResourceHaver:
    def __init__(self):
        self.resources = {resource_type: 0 for resource_type in Resource}

    def transact(self, transaction: Transaction):
        assert self.can_transact(transaction)
        for resource in transaction.resources:
            self.resources[resource] += transaction.resources[resource]

    def can_transact(self, transaction: Transaction) -> bool:
        for resource in transaction.resources:
            if self.resources[resource] + transaction.resources[resource] < 0:
                return False
        return True
