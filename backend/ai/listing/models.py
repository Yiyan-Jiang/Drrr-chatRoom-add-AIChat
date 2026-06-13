from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ListingItem:
    item_id: str
    title: str
    attributes: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ListingResult:
    items: list[ListingItem]
    query: str

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "items": [item.to_dict() for item in self.items],
        }
