from ai.listing.models import ListingItem, ListingResult


def listing_search(items: list[ListingItem], query: str) -> ListingResult:
    if not query:
        return ListingResult(items=list(items), query=query)
    matched = [
        item
        for item in items
        if query in item.title
        or any(query in str(value) for value in item.attributes.values())
    ]
    return ListingResult(items=matched, query=query)
