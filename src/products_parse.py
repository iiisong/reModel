import re

def parse_price(price_str):
    """Parse price and convert to float (handle all formats)"""
    price_str = price_str.replace(",", "")
    match = re.search(r"(\d+(\.\d+)?)", price_str)
    if match:
        return float(match.group(1))
    return 0.0

def get_best_links_within_budget(results, budget, class_names):
    """Select one link per piece of furniture and maximize the budget without exceeding."""
    budget = float(budget)
    
    total_price = 0
    selected = []
    class_matches = []
    
    for i, furniture_results in enumerate(results):
        selected_item = None
        for item in furniture_results:
            price = parse_price(item["price"])
            if total_price + price <= budget:
                selected_item = item
                total_price += price
                class_matches.append(class_names[i])
                break
        
        if selected_item:
            selected.append(selected_item)
    
    return selected, total_price, class_matches