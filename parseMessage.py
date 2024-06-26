import re

# Function to parse the message
def parse_message(message):
    details = {}

    details['pair'] = re.search(r"Pair: \$(.*) \(", message).group(1).replace("/", "")
    details['direction'] = 'BUY' if '⬆️LONG' in message else 'SELL'
    details['position_size'] = [float(x) for x in re.search(r"Position Size: (\d+) - (\d+)%", message).groups()]
    details['leverage'] = [int(x) for x in re.search(r"Leverage : (\d+) -(\d+)X", message).groups()]
    entry = re.search(r"ENTRY : ([\d.]+) - ([\d.]+)", message).groups()
    details['entry_min'] = float(entry[0])
    details['entry_max'] = float(entry[1])
    details['stop_loss'] = float(re.search(r"STOP LOSS: (\d+)", message).group(1))
    details['targets'] = [float(x) for x in re.findall(r"🔘Target \d+ - ([\d.]+)", message)]

    return details

# Example usage
if __name__ == "__main__":
    message = """
    Pair: $WAVES/USDT (Binance, ByBit)
    Direction: ⬆️LONG
    --
    Position Size: 2 - 4%
    Leverage : 3 -5X
    Trade Type: SWING
    --
    ENTRY : 2.2 - 2.39
    (OTE: 2.29)

    🔘Target 1 - 2.42
    🔘Target 2 - 2.46
    🔘Target 3 - 2.50
    🔘Target 4 - 2.55
    🔘Target 5 - 2.75
    🔘Target 6 - 2.95
    🔘Target 7 - 3.15
    🔘Target 8 - 3.30
    🔘Target 9 - 3.60

    🚫STOP LOSS: 2

    """
    details = parse_message(message)
    print(details)
