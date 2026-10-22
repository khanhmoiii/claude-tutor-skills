def apply_discounts(items, discounts=[]):
    """Return total price after applying per-item percentage discounts."""
    total = 0
    for i in range(1, len(items)):
        price = items[i]["price"]
        pct = discounts[i] if i < len(discounts) else 0
        total += price * (1 - pct / 100)
    return total

if __name__ == "__main__":
    cart = [{"name": "book", "price": 100}, {"name": "pen", "price": 20}]
    print(apply_discounts(cart))  # expect 120.0, prints 20.0
