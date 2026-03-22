from delta_rest_client import DeltaRestClient, OrderType
import time
import os

# ==============================
# CONFIG
# ==============================
PRODUCT_ID = 84
SIZE = 1
COOLDOWN_SECONDS = 5

last_signal = None
last_trade_time = 0

# ==============================
# INIT CLIENT
# ==============================
delta_client = DeltaRestClient(
    base_url='https://cdn-ind.testnet.deltaex.org',
    api_key=os.getenv("API_KEY"),    #api keys in envr variable
    api_secret=os.getenv("API_SECRET") # secret keys in envr variable
)

# ==============================
# GET POSITION
# ==============================
def get_position():
    try:
        response = delta_client.get_product_position(PRODUCT_ID)

        if not response:
            return None

        size = float(response.get("size", 0))

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
    res = delta_client.place_order(
        product_id=PRODUCT_ID,
        size=SIZE,
        side='buy',
        order_type=OrderType.MARKET
    )
    print("✅ BUY response:", res)


def place_sell():
    print("🔴 Placing SELL order...")
    res = delta_client.place_order(
        product_id=PRODUCT_ID,
        size=SIZE,
        side='sell',
        order_type=OrderType.MARKET
    )
    print("✅ SELL response:", res)


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

    delta_client.place_order(
        product_id=PRODUCT_ID,
        size=size,
        side=opposite_side,
        order_type=OrderType.MARKET
    )


# ==============================
# MAIN SIGNAL HANDLER (CLOSE ONLY)
# ==============================
def handle_signal(signal):
    global last_signal, last_trade_time

    print("\n==============================")
    print(f"📊 Incoming Signal: {signal}")
    print("==============================")

    current_time = time.time()

    # 🔹 Duplicate protection
    if signal == last_signal:
        print("⚠️ Duplicate signal ignored")
        return

    # 🔹 Cooldown protection
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
            # ✅ No position → open BUY
            place_buy()

        elif position['side'] == 'sell':
            # ✅ Opposite → CLOSE ONLY
            close_position(position)
            print("🚫 No new BUY (close-only mode)")

        else:
            print("✅ Already in BUY, skipping...")

    # ==============================
    # SELL SIGNAL
    # ==============================
    elif signal == "SELL":

        if position is None:
            # ✅ No position → open SELL
            place_sell()

        elif position['side'] == 'buy':
            # ✅ Opposite → CLOSE ONLY
            close_position(position)
            print("🚫 No new SELL (close-only mode)")

        else:
            print("✅ Already in SELL, skipping...")

    # Update trackers
    last_signal = signal
    last_trade_time = current_time