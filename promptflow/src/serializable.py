from abc import ABC, abstractmethod
from typing import Any


class Serializable(ABC):
    """
    Base class for serializable objects. Provides an interface and default
    implementations for serializing and deserializing objects.
    """

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def deserialize(self, *args, **kwargs) -> "Serializable":
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.serialize()})"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.serialize() == other.serialize()
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.serialize())
