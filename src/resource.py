from enum import Enum
from typing import Dict, Self
from abc import ABC, abstractmethod
import json


class Resource(Enum):
    BRICK = "brick"
    STONE = "stone"
    WHEAT = "wheat"
    SHEEP = "sheep"
    WOOD = "wood"


class Transaction:
    def __init__(self, resources: Dict[Resource, int]):
        self.resources = resources

        for resource in Resource:
            if resource not in resources:
                self.resources[resource] = 0

    def inverse(self) -> Self:
        resources = self.resources.copy()
        for resource in resources:
            resources[resource] *= -1
        return Transaction(resources)

    def __hash__(self):
        return hash(json.dumps(self.serialize(), sort_keys=True))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def serialize(self) -> Dict[str, int]:
        return {
            resource.value: amount
            for resource, amount in self.resources.items()
        }


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
