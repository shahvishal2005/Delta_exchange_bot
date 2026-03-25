from delta_rest_client import DeltaRestClient, OrderType
import time
import os

# ==============================
# CONFIG
# ==============================
PRODUCT_ID = 84
SIZE = 1
COOLDOWN_SECONDS = 5

# GLOBAL STATE
last_signal = None
last_trade_time = 0

# ==============================
# INIT CLIENT
# ==============================
delta_client = DeltaRestClient(
    base_url='https://cdn-ind.testnet.deltaex.org',
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# ==============================
# GET POSITION
# ==============================
def get_position():
    try:
        res = delta_client.get_position(product_id=PRODUCT_ID)
        print("📡 Raw position response:", res)

        if not res:
            return None

        size = float(res.get("size", 0))

        if size == 0:
            return None

        side = "buy" if size > 0 else "sell"

        return {
            "side": side,
            "size": size
        }

    except Exception as e:
        print("❌ Error fetching position:", e)
        return None


# ==============================
# PLACE ORDERS
# ==============================
def place_buy():
    print("🟢 Placing BUY order...")
    try:
        res = delta_client.place_order(
            product_id=PRODUCT_ID,
            size=SIZE,
            side='buy',
            order_type=OrderType.MARKET
        )
        print("✅ BUY response:", res)
        time.sleep(2)
    except Exception as e:
        print("❌ BUY order failed:", e)


def place_sell():
    print("🔴 Placing SELL order...")
    try:
        res = delta_client.place_order(
            product_id=PRODUCT_ID,
            size=SIZE,
            side='sell',
            order_type=OrderType.MARKET
        )
        print("✅ SELL response:", res)
        time.sleep(2)
    except Exception as e:
        print("❌ SELL order failed:", e)


# ==============================
# CLOSE POSITION
# ==============================
def close_position(position):
    if not position:
        return

    side = position['side']
    size = abs(float(position['size']))

    print(f"⚡ Closing {side} position of size {size}")

    opposite_side = 'sell' if side == 'buy' else 'buy'

    try:
        delta_client.place_order(
            product_id=PRODUCT_ID,
            size=size,
            side=opposite_side,
            order_type=OrderType.MARKET
        )
        print("✅ Position closed")
        time.sleep(2)
    except Exception as e:
        print("❌ Error closing position:", e)


# ==============================
# MAIN SIGNAL HANDLER
# ==============================
def handle_signal(signal):
    global last_signal, last_trade_time

    print("\n==============================")
    print(f"📊 Incoming Signal: {signal}")
    print("==============================")

    current_time = time.time()

    # Duplicate protection
    if signal == last_signal:
        print("⚠️ Duplicate signal ignored")
        return

    # Cooldown protection
    if current_time - last_trade_time < COOLDOWN_SECONDS:
        print("⏳ Cooldown active, skipping")
        return

    position = get_position()

    if position:
        print(f"📌 Current Position → Side: {position['side']}, Size: {position['size']}")
    else:
        print("📌 No open position")

    # ==============================
    # BUY SIGNAL
    # ==============================
    if signal == "BUY":

        if position is None:
            print("🟢 No position → opening BUY")
            place_buy()

        elif position['side'] == 'sell':
            print("🔄 Reversing SELL → BUY")
            close_position(position)
            place_buy()

        else:
            print("✅ Already in BUY, skipping...")

    # ==============================
    # SELL SIGNAL
    # ==============================
    elif signal == "SELL":

        if position is None:
            print("🔴 No position → opening SELL")
            place_sell()

        elif position['side'] == 'buy':
            print("🔄 Reversing BUY → SELL")
            close_position(position)
            place_sell()

        else:
            print("✅ Already in SELL, skipping...")

    # ==============================
    # UPDATE TRACKERS
    # ==============================
    last_signal = signal
    last_trade_time = current_time

    print("🧠 Updated last_signal:", last_signal)
    print("⏱ Updated last_trade_time:", last_trade_time)
