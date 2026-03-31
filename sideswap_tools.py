#!/usr/bin/env python3
"""SideSwap multi-tool: historico, monitor spread, whales, calculadora, alertas, peg, arbitraje, federacion."""

import json
import asyncio
import sys
import os
import csv
import urllib.request
from datetime import datetime, timezone

try:
    import websockets
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])
    import websockets

# === Asset IDs ===
ASSETS = {
    "LBTC": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",
    "USDT": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
    "EURX": "18729918ab4bca843656f08d4dd877bed6641fbd596a0a963abbf199cfeb3cec",
    "DEPIX": "02f22f8d9c76ab41661a2729e4752e2c5d1a263012141b86ea98af5472df5189",
    "SSWP": "06d1085d6a3a1328fb8189d106c7a8afbef3d327e34504828c4cac2c74ac0802",
}
WS = "wss://api.sideswap.io/json-rpc-ws"

ASSET_NAMES = {v: k for k, v in ASSETS.items()}


def asset_name(aid):
    return ASSET_NAMES.get(aid, aid[:8] + "...")


async def get_snapshot(base=None, quote=None):
    """Connect, subscribe, return (orders_dict, ind_price, last_price)."""
    base = base or ASSETS["LBTC"]
    quote = quote or ASSETS["USDT"]
    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "market",
            "params": {"subscribe": {"asset_pair": {"base": base, "quote": quote}}}
        }))
        orders = {}
        ind_price = last_price = 0
        for _ in range(5):
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=8))
            except asyncio.TimeoutError:
                break
            if "result" in msg and "subscribe" in msg.get("result", {}):
                for o in msg["result"]["subscribe"]["orders"]:
                    orders[o["order_id"]] = o
            p = msg.get("params", {})
            if "market_price" in p:
                ind_price = p["market_price"].get("ind_price", 0)
                last_price = p["market_price"].get("last_price", 0)
                break
        return orders, ind_price, last_price


# ============================================================
# 1. HISTORICO OHLCV
# ============================================================
async def cmd_history(args):
    """Export OHLCV history to CSV."""
    base = ASSETS.get(args[0].upper(), ASSETS["LBTC"]) if args else ASSETS["LBTC"]
    quote = ASSETS.get(args[1].upper(), ASSETS["USDT"]) if len(args) > 1 else ASSETS["USDT"]
    outfile = args[2] if len(args) > 2 else f"sideswap_{asset_name(base)}_{asset_name(quote)}_ohlcv.csv"

    print(f"Descargando historico {asset_name(base)}/{asset_name(quote)}...")

    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "market",
            "params": {"chart_sub": {"asset_pair": {"base": base, "quote": quote}}}
        }))
        data = []
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=15))
        if "result" in msg and "chart_sub" in msg["result"]:
            data = msg["result"]["chart_sub"]["data"]

    if not data:
        print("No hay datos historicos para este par.")
        return

    with open(outfile, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for d in data:
            w.writerow([d["time"], d["open"], d["high"], d["low"], d["close"], d["volume"]])

    print(f"Exportados {len(data)} dias a {outfile}")
    print(f"Desde {data[0]['time']} hasta {data[-1]['time']}")
    print(f"Ultimo cierre: ${data[-1]['close']:,.2f}  |  Vol: {data[-1]['volume']:.8f} BTC")

    # Show last 10 days
    print(f"\nUltimos 10 dias:")
    print(f"{'Fecha':>12}  {'Open':>12}  {'High':>12}  {'Low':>12}  {'Close':>12}  {'Vol BTC':>12}")
    print("-" * 80)
    for d in data[-10:]:
        print(f"{d['time']:>12}  ${d['open']:>11,.2f}  ${d['high']:>11,.2f}  ${d['low']:>11,.2f}  ${d['close']:>11,.2f}  {d['volume']:>12.8f}")


# ============================================================
# 2. MONITOR DE SPREAD
# ============================================================
async def cmd_spread(args):
    """Real-time spread monitor with optional alert threshold."""
    threshold = float(args[0]) if args else 0.0
    base = ASSETS["LBTC"]
    quote = ASSETS["USDT"]

    print(f"Monitor de spread L-BTC/USDt en vivo")
    if threshold > 0:
        print(f"Alerta cuando spread < {threshold}%")
    print(f"{'Hora':>10}  {'Best Ask':>12}  {'Best Bid':>12}  {'Spread $':>10}  {'Spread %':>9}  {'Indice':>12}  {'Estado'}")
    print("-" * 90)

    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "market",
            "params": {"subscribe": {"asset_pair": {"base": base, "quote": quote}}}
        }))

        orderbook = {}
        ind_price = 0

        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            except asyncio.TimeoutError:
                continue

            changed = False
            if "result" in msg and "subscribe" in msg.get("result", {}):
                orderbook.clear()
                for o in msg["result"]["subscribe"]["orders"]:
                    orderbook[o["order_id"]] = o
                changed = True

            p = msg.get("params", {})
            if "market_price" in p:
                ind_price = p["market_price"].get("ind_price", ind_price)
                changed = True
            if "public_order_created" in p:
                o = p["public_order_created"]["order"]
                orderbook[o["order_id"]] = o
                changed = True
            if "public_order_removed" in p:
                orderbook.pop(p["public_order_removed"]["order_id"], None)
                changed = True

            if not changed:
                continue

            asks = [o for o in orderbook.values() if o["trade_dir"] == "Sell"]
            bids = [o for o in orderbook.values() if o["trade_dir"] == "Buy"]
            if not asks or not bids:
                continue

            best_ask = min(o["price"] for o in asks)
            best_bid = max(o["price"] for o in bids)

            # Deduplicate
            price_key = (round(best_ask, 2), round(best_bid, 2))
            if hasattr(cmd_spread, '_last_key') and cmd_spread._last_key == price_key:
                continue
            cmd_spread._last_key = price_key

            spread = best_ask - best_bid
            spread_pct = (spread / best_ask * 100) if best_ask else 0
            now = datetime.now().strftime("%H:%M:%S")

            alert = ""
            if threshold > 0 and spread_pct < threshold:
                alert = " << ALERTA! Spread bajo"

            print(
                f"{now:>10}  ${best_ask:>11,.2f}  ${best_bid:>11,.2f}"
                f"  ${spread:>9,.2f}  {spread_pct:>8.3f}%"
                f"  ${ind_price:>11,.2f}{alert}"
            )


# ============================================================
# 4. MONITOR DE WHALES
# ============================================================
async def cmd_whales(args):
    """Monitor large orders entering/leaving the orderbook."""
    min_btc = float(args[0]) if args else 0.1
    base = ASSETS["LBTC"]
    quote = ASSETS["USDT"]

    print(f"Monitor de whales L-BTC/USDt (ordenes >= {min_btc} BTC)")
    print(f"{'Hora':>10}  {'Evento':>8}  {'Dir':>5}  {'Precio':>12}  {'BTC':>14}  {'USDt':>14}  {'Tipo':>8}")
    print("-" * 90)

    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "market",
            "params": {"subscribe": {"asset_pair": {"base": base, "quote": quote}}}
        }))

        known = {}

        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            except asyncio.TimeoutError:
                continue

            if "result" in msg and "subscribe" in msg.get("result", {}):
                for o in msg["result"]["subscribe"]["orders"]:
                    known[o["order_id"]] = o
                    btc = o["amount"] / 1e8
                    if btc >= min_btc:
                        usdt = btc * o["price"]
                        on = "ONLINE" if o["online"] else "OFFLINE"
                        print(
                            f"{'INIT':>10}  {'EXISTE':>8}  {o['trade_dir']:>5}"
                            f"  ${o['price']:>11,.2f}  {btc:>14.8f}  ${usdt:>13,.2f}  {on:>8}"
                        )
                continue

            p = msg.get("params", {})

            if "public_order_created" in p:
                o = p["public_order_created"]["order"]
                btc = o["amount"] / 1e8
                known[o["order_id"]] = o
                if btc >= min_btc:
                    usdt = btc * o["price"]
                    on = "ONLINE" if o["online"] else "OFFLINE"
                    now = datetime.now().strftime("%H:%M:%S")
                    print(
                        f"\033[32m{now:>10}  {'NUEVA':>8}  {o['trade_dir']:>5}"
                        f"  ${o['price']:>11,.2f}  {btc:>14.8f}  ${usdt:>13,.2f}  {on:>8}\033[0m"
                    )

            if "public_order_removed" in p:
                oid = p["public_order_removed"]["order_id"]
                o = known.pop(oid, None)
                if o:
                    btc = o["amount"] / 1e8
                    if btc >= min_btc:
                        usdt = btc * o["price"]
                        on = "ONLINE" if o["online"] else "OFFLINE"
                        now = datetime.now().strftime("%H:%M:%S")
                        print(
                            f"\033[31m{now:>10}  {'ELIMINADA':>8}  {o['trade_dir']:>5}"
                            f"  ${o['price']:>11,.2f}  {btc:>14.8f}  ${usdt:>13,.2f}  {on:>8}\033[0m"
                        )


# ============================================================
# 6. CALCULADORA INVERSA
# ============================================================
async def cmd_calc(args):
    """Calculate how much USDt needed to buy exactly X BTC, or USDt received for selling X BTC."""
    if len(args) < 2:
        print("Uso: calc <buy|sell> <btc_amount>")
        print("  calc buy 0.5    — cuanto USDt necesito para comprar 0.5 BTC")
        print("  calc sell 0.5   — cuanto USDt recibo por vender 0.5 BTC")
        return

    direction = args[0].lower()
    target_btc = float(args[1])

    orders, ind_price, last_price = await get_snapshot()

    if direction == "buy":
        side = sorted([o for o in orders.values() if o["trade_dir"] == "Sell"], key=lambda x: x["price"])
        label = "COMPRAR"
    else:
        side = sorted([o for o in orders.values() if o["trade_dir"] == "Buy"], key=lambda x: -x["price"])
        label = "VENDER"

    print(f"Indice: ${ind_price:,.2f}")
    print(f"{label} exactamente {target_btc:.8f} BTC")
    print()

    remaining_btc = target_btc
    total_usdt = 0.0
    fills = []

    for i, o in enumerate(side, 1):
        if remaining_btc <= 0:
            break
        avail = o["amount"] / 1e8
        on = "ONLINE" if o["online"] else "OFFLINE"
        sp = ((o["price"] / ind_price) - 1) * 100 if ind_price else 0
        if direction == "sell":
            sp = -sp

        if avail <= remaining_btc:
            usdt = avail * o["price"]
            total_usdt += usdt
            remaining_btc -= avail
            fills.append((i, o["price"], avail, usdt, "COMPLETA", on, sp))
        else:
            usdt = remaining_btc * o["price"]
            total_usdt += usdt
            fills.append((i, o["price"], remaining_btc, usdt, "PARCIAL", on, sp))
            remaining_btc = 0

    filled_btc = target_btc - remaining_btc
    avg = total_usdt / filled_btc if filled_btc else 0
    fee_btc = filled_btc * 0.002
    fee_usdt = fee_btc * avg

    print(f"{'#':>2}  {'Precio':>14}  {'BTC':>14}  {'USDt':>14}  {'Tipo':>10}  {'Maker':>8}  {'Spread':>8}")
    print("-" * 90)
    for i, price, btc, usdt, tipo, on, sp in fills:
        print(f"{i:>2}  ${price:>13,.2f}  {btc:>14.8f}  ${usdt:>13,.2f}  {tipo:>10}  {on:>8}  {sp:>+7.2f}%")
    print("-" * 90)

    if direction == "buy":
        total_cost = total_usdt + fee_usdt
        net_btc = filled_btc - fee_btc
        eff = total_usdt / net_btc if net_btc else 0
        spread_pct = ((avg / ind_price) - 1) * 100 if ind_price else 0
        total_pct = ((eff / ind_price) - 1) * 100 if ind_price else 0
        print()
        print(f"  Para comprar {target_btc:.8f} BTC necesitas:")
        print(f"  USDt a enviar:       ${total_usdt:>12,.2f}")
        print(f"  Precio promedio:     ${avg:>12,.2f}  (spread {spread_pct:+.3f}%)")
        print(f"  Taker fee (0.2%):    -{fee_btc:.8f} BTC  (~${fee_usdt:,.2f})")
        print(f"  BTC neto recibido:   {net_btc:.8f} BTC")
        print(f"  Costo total USDt:    ${total_usdt:>12,.2f}  (por {net_btc:.8f} BTC neto)")
        print(f"  Precio efectivo:     ${eff:>12,.2f}  ({total_pct:+.3f}% vs indice)")
    else:
        net_usdt = total_usdt - fee_usdt
        eff = net_usdt / filled_btc if filled_btc else 0
        spread_pct = ((ind_price - avg) / ind_price) * 100 if ind_price else 0
        total_pct = ((ind_price - eff) / ind_price) * 100 if ind_price else 0
        print()
        print(f"  Por vender {target_btc:.8f} BTC recibes:")
        print(f"  USDt bruto:          ${total_usdt:>12,.2f}")
        print(f"  Precio promedio:     ${avg:>12,.2f}  (spread {spread_pct:+.3f}%)")
        print(f"  Taker fee (0.2%):    -${fee_usdt:>11,.2f}")
        print(f"  USDt neto:           ${net_usdt:>12,.2f}")
        print(f"  Precio efectivo:     ${eff:>12,.2f}  ({total_pct:+.3f}% vs indice)")

    if remaining_btc > 0:
        print(f"\n  !! Solo hay liquidez para {filled_btc:.8f} BTC de {target_btc:.8f}")
        print(f"     Faltan {remaining_btc:.8f} BTC por llenar")


# ============================================================
# 7. SIMULADOR DE LIMIT ORDER
# ============================================================
async def cmd_limit(args):
    """Simulate where a limit order would sit in the book."""
    if len(args) < 3:
        print("Uso: limit <buy|sell> <btc_amount> <price>")
        print("  limit buy 0.5 64000   — orden de compra de 0.5 BTC a $64,000")
        print("  limit sell 0.5 68000  — orden de venta de 0.5 BTC a $68,000")
        return

    direction = args[0].lower()
    btc_amount = float(args[1])
    my_price = float(args[2])

    orders, ind_price, last_price = await get_snapshot()

    if direction == "buy":
        # My buy order competes with other bids
        bids = sorted([o for o in orders.values() if o["trade_dir"] == "Buy"], key=lambda x: -x["price"])
        best_ask = min((o["price"] for o in orders.values() if o["trade_dir"] == "Sell"), default=0)

        print(f"Indice: ${ind_price:,.2f}  |  Best ask: ${best_ask:,.2f}  |  Best bid: ${bids[0]['price']:,.2f}" if bids else "")
        print(f"\nTu orden: COMPRAR {btc_amount:.8f} BTC @ ${my_price:,.2f}")
        print(f"Valor: ${btc_amount * my_price:,.2f} USDt")
        print()

        if best_ask and my_price >= best_ask:
            print(f"!! Tu precio (${my_price:,.2f}) >= best ask (${best_ask:,.2f})")
            print(f"   Se ejecutaria como MARKET ORDER inmediatamente")
            return

        # Find position
        position = 0
        btc_ahead = 0
        usdt_ahead = 0
        for o in bids:
            if o["price"] >= my_price:
                position += 1
                b = o["amount"] / 1e8
                btc_ahead += b
                usdt_ahead += b * o["price"]
            else:
                break

        spread_vs_index = ((ind_price - my_price) / ind_price) * 100 if ind_price else 0
        spread_vs_ask = ((best_ask - my_price) / best_ask) * 100 if best_ask else 0

        print(f"  Posicion en el book:    #{position + 1}")
        print(f"  Ordenes por delante:    {position}")
        print(f"  BTC por delante:        {btc_ahead:.8f} (${usdt_ahead:,.2f} USDt)")
        print(f"  Spread vs indice:       {spread_vs_index:+.2f}%")
        print(f"  Distancia al best ask:  {spread_vs_ask:.2f}% (${best_ask - my_price:,.2f})")
        print()

        # Show nearby orders
        print("  Ordenes cercanas:")
        print(f"  {'#':>4}  {'Precio':>12}  {'BTC':>14}  {'USDt':>12}  {'Tipo':>8}")
        print(f"  {'-'*60}")
        shown = False
        for i, o in enumerate(bids):
            if not shown and o["price"] < my_price:
                print(f"  \033[33m >>> TU ORDEN: ${my_price:>11,.2f}  {btc_amount:>14.8f}  ${btc_amount*my_price:>11,.2f}\033[0m")
                shown = True
            b = o["amount"] / 1e8
            on = "ONLINE" if o["online"] else "OFFLINE"
            print(f"  {i+1:>4}  ${o['price']:>11,.2f}  {b:>14.8f}  ${b*o['price']:>11,.2f}  {on:>8}")
            if i > position + 3:
                break
        if not shown:
            print(f"  \033[33m >>> TU ORDEN: ${my_price:>11,.2f}  {btc_amount:>14.8f}  ${btc_amount*my_price:>11,.2f}\033[0m")

    else:
        # My sell order competes with other asks
        asks = sorted([o for o in orders.values() if o["trade_dir"] == "Sell"], key=lambda x: x["price"])
        best_bid = max((o["price"] for o in orders.values() if o["trade_dir"] == "Buy"), default=0)

        print(f"Indice: ${ind_price:,.2f}  |  Best ask: ${asks[0]['price']:,.2f}  |  Best bid: ${best_bid:,.2f}" if asks else "")
        print(f"\nTu orden: VENDER {btc_amount:.8f} BTC @ ${my_price:,.2f}")
        print(f"Valor: ${btc_amount * my_price:,.2f} USDt")
        print()

        if best_bid and my_price <= best_bid:
            print(f"!! Tu precio (${my_price:,.2f}) <= best bid (${best_bid:,.2f})")
            print(f"   Se ejecutaria como MARKET ORDER inmediatamente")
            return

        position = 0
        btc_ahead = 0
        usdt_ahead = 0
        for o in asks:
            if o["price"] <= my_price:
                position += 1
                b = o["amount"] / 1e8
                btc_ahead += b
                usdt_ahead += b * o["price"]
            else:
                break

        spread_vs_index = ((my_price - ind_price) / ind_price) * 100 if ind_price else 0
        spread_vs_bid = ((my_price - best_bid) / best_bid) * 100 if best_bid else 0

        print(f"  Posicion en el book:    #{position + 1}")
        print(f"  Ordenes por delante:    {position}")
        print(f"  BTC por delante:        {btc_ahead:.8f} (${usdt_ahead:,.2f} USDt)")
        print(f"  Spread vs indice:       {spread_vs_index:+.2f}%")
        print(f"  Distancia al best bid:  {spread_vs_bid:.2f}% (${my_price - best_bid:,.2f})")
        print()

        print("  Ordenes cercanas:")
        print(f"  {'#':>4}  {'Precio':>12}  {'BTC':>14}  {'USDt':>12}  {'Tipo':>8}")
        print(f"  {'-'*60}")
        shown = False
        for i, o in enumerate(asks):
            if not shown and o["price"] > my_price:
                print(f"  \033[33m >>> TU ORDEN: ${my_price:>11,.2f}  {btc_amount:>14.8f}  ${btc_amount*my_price:>11,.2f}\033[0m")
                shown = True
            b = o["amount"] / 1e8
            on = "ONLINE" if o["online"] else "OFFLINE"
            print(f"  {i+1:>4}  ${o['price']:>11,.2f}  {b:>14.8f}  ${b*o['price']:>11,.2f}  {on:>8}")
            if shown and i > position + 3:
                break
        if not shown:
            print(f"  \033[33m >>> TU ORDEN: ${my_price:>11,.2f}  {btc_amount:>14.8f}  ${btc_amount*my_price:>11,.2f}\033[0m")


# ============================================================
# 8. ALERTA DE PRECIO
# ============================================================
async def cmd_alert(args):
    """Alert when best ask drops below or best bid rises above a threshold."""
    if len(args) < 2:
        print("Uso: alert <ask_below|bid_above> <price>")
        print("  alert ask_below 65000  — alerta si el best ask baja de $65,000")
        print("  alert bid_above 67000  — alerta si el best bid sube de $67,000")
        print("  alert both 65000 67000 — ambas alertas")
        return

    ask_target = bid_target = None
    if args[0] == "ask_below":
        ask_target = float(args[1])
        print(f"Alerta: best ask < ${ask_target:,.2f}")
    elif args[0] == "bid_above":
        bid_target = float(args[1])
        print(f"Alerta: best bid > ${bid_target:,.2f}")
    elif args[0] == "both":
        ask_target = float(args[1])
        bid_target = float(args[2]) if len(args) > 2 else None
        print(f"Alertas: ask < ${ask_target:,.2f}" + (f", bid > ${bid_target:,.2f}" if bid_target else ""))

    print(f"Monitoreando... (Ctrl+C para salir)")
    print(f"{'Hora':>10}  {'Best Ask':>12}  {'Best Bid':>12}  {'Indice':>12}  {'Alerta'}")
    print("-" * 70)

    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "market",
            "params": {"subscribe": {"asset_pair": {"base": ASSETS["LBTC"], "quote": ASSETS["USDT"]}}}
        }))

        orderbook = {}
        ind_price = 0
        alerted_ask = alerted_bid = False

        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            except asyncio.TimeoutError:
                continue

            changed = False
            if "result" in msg and "subscribe" in msg.get("result", {}):
                orderbook.clear()
                for o in msg["result"]["subscribe"]["orders"]:
                    orderbook[o["order_id"]] = o
                changed = True
            p = msg.get("params", {})
            if "market_price" in p:
                ind_price = p["market_price"].get("ind_price", ind_price)
            if "public_order_created" in p:
                o = p["public_order_created"]["order"]
                orderbook[o["order_id"]] = o
                changed = True
            if "public_order_removed" in p:
                orderbook.pop(p["public_order_removed"]["order_id"], None)
                changed = True

            if not changed:
                continue

            asks = [o for o in orderbook.values() if o["trade_dir"] == "Sell"]
            bids = [o for o in orderbook.values() if o["trade_dir"] == "Buy"]
            if not asks or not bids:
                continue

            best_ask = min(o["price"] for o in asks)
            best_bid = max(o["price"] for o in bids)
            now = datetime.now().strftime("%H:%M:%S")

            alerts = []
            if ask_target and best_ask < ask_target and not alerted_ask:
                alerts.append(f"\033[32m<< ASK ${best_ask:,.2f} < ${ask_target:,.2f}!\033[0m")
                alerted_ask = True
            elif ask_target and best_ask >= ask_target:
                alerted_ask = False

            if bid_target and best_bid > bid_target and not alerted_bid:
                alerts.append(f"\033[32m<< BID ${best_bid:,.2f} > ${bid_target:,.2f}!\033[0m")
                alerted_bid = True
            elif bid_target and best_bid <= bid_target:
                alerted_bid = False

            alert_str = "  ".join(alerts) if alerts else ""
            if alerts:
                print(f"\033[1m{now:>10}  ${best_ask:>11,.2f}  ${best_bid:>11,.2f}  ${ind_price:>11,.2f}  {alert_str}\033[0m")
                # Bell
                print("\a", end="", flush=True)
            else:
                print(f"{now:>10}  ${best_ask:>11,.2f}  ${best_bid:>11,.2f}  ${ind_price:>11,.2f}")


# ============================================================
# 9. PEG-IN / PEG-OUT MONITOR
# ============================================================
async def cmd_peg(args):
    """Show peg-in/peg-out server status and fees."""
    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({"id": 1, "method": "server_status", "params": None}))
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))

        print("ESTADO DEL SERVIDOR SIDESWAP")
        print("=" * 60)

        if "result" in msg:
            r = msg["result"]
            peg_in_fee = r.get("server_fee_percent_peg_in", "?")
            peg_out_fee = r.get("server_fee_percent_peg_out", "?")
            min_in = r.get("min_peg_in_amount", 0)
            min_out = r.get("min_peg_out_amount", 0)

            print(f"\n  Peg-In (BTC -> L-BTC):")
            print(f"    Fee:           {peg_in_fee}%")
            if min_in:
                print(f"    Min amount:    {min_in} sats ({min_in/1e8:.8f} BTC)")

            print(f"\n  Peg-Out (L-BTC -> BTC):")
            print(f"    Fee:           {peg_out_fee}%")
            if min_out:
                print(f"    Min amount:    {min_out} sats ({min_out/1e8:.8f} BTC)")

            # Print all other fields
            skip = {"min_peg_in_amount", "min_peg_out_amount",
                    "server_fee_percent_peg_in", "server_fee_percent_peg_out"}
            other = {k: v for k, v in r.items() if k not in skip}
            if other:
                print(f"\n  Otros datos del servidor:")
                for k, v in other.items():
                    print(f"    {k}: {v}")
        elif "error" in msg:
            # Fallback: try without params at all
            print(f"  Error: {msg['error']}")
            print(f"  Respuesta completa: {json.dumps(msg, indent=2)}")

        # Get assets list
        await ws.send(json.dumps({"id": 2, "method": "assets", "params": {"all_assets": True}}))
        try:
            msg2 = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            if "result" in msg2 and "assets" in msg2["result"]:
                assets = msg2["result"]["assets"]
                stablecoins = [a for a in assets if a.get("market_type") == "Stablecoin"]
                amps = [a for a in assets if a.get("market_type") == "Amp"]
                tokens = [a for a in assets if a.get("market_type") == "Token"]

                print(f"\n  Assets disponibles: {len(assets)} total")
                print(f"    Stablecoins ({len(stablecoins)}): {', '.join(a.get('ticker','?') for a in stablecoins)}")
                print(f"    AMP ({len(amps)}): {', '.join(a.get('ticker','?') for a in amps)}")
                print(f"    Tokens ({len(tokens)}): {', '.join(a.get('ticker','?') for a in tokens)}")

                if args and args[0] == "-v":
                    print(f"\n  {'Ticker':>8}  {'Nombre':<25}  {'Tipo':<12}  {'Instant':>8}  Asset ID")
                    print(f"  {'-'*100}")
                    for a in assets:
                        ticker = a.get("ticker", "?")
                        name = a.get("name", "?")
                        mtype = a.get("market_type") or "-"
                        instant = a.get("instant_swaps")
                        aid = a.get("asset_id", "?")
                        print(f"  {ticker:>8}  {name:<25}  {mtype:<12}  {str(instant):>8}  {aid}")
        except asyncio.TimeoutError:
            pass


# ============================================================
# 10. DETECTOR DE ARBITRAJE
# ============================================================
async def cmd_arb(args):
    """Monitor price divergence from index — potential arbitrage opportunities."""
    threshold = float(args[0]) if args else 1.0

    print(f"Detector de arbitraje L-BTC/USDt")
    print(f"Alerta cuando spread vs indice > {threshold}%")
    print(f"{'Hora':>10}  {'Indice':>12}  {'Best Ask':>12}  {'Ask Sp':>8}  {'Best Bid':>12}  {'Bid Sp':>8}  {'Senal'}")
    print("-" * 95)

    async with websockets.connect(WS, ping_interval=30) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "market",
            "params": {"subscribe": {"asset_pair": {"base": ASSETS["LBTC"], "quote": ASSETS["USDT"]}}}
        }))

        orderbook = {}
        ind_price = 0

        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            except asyncio.TimeoutError:
                continue

            changed = False
            if "result" in msg and "subscribe" in msg.get("result", {}):
                orderbook.clear()
                for o in msg["result"]["subscribe"]["orders"]:
                    orderbook[o["order_id"]] = o
                changed = True
            p = msg.get("params", {})
            if "market_price" in p:
                ind_price = p["market_price"].get("ind_price", ind_price)
                changed = True
            if "public_order_created" in p:
                o = p["public_order_created"]["order"]
                orderbook[o["order_id"]] = o
                changed = True
            if "public_order_removed" in p:
                orderbook.pop(p["public_order_removed"]["order_id"], None)
                changed = True

            if not changed or ind_price == 0:
                continue

            asks = [o for o in orderbook.values() if o["trade_dir"] == "Sell"]
            bids = [o for o in orderbook.values() if o["trade_dir"] == "Buy"]
            if not asks or not bids:
                continue

            best_ask = min(o["price"] for o in asks)
            best_bid = max(o["price"] for o in bids)

            # Deduplicate: only print when prices actually change
            price_key = (round(best_ask, 2), round(best_bid, 2), round(ind_price, 2))
            if hasattr(cmd_arb, '_last_key') and cmd_arb._last_key == price_key:
                continue
            cmd_arb._last_key = price_key

            ask_spread = ((best_ask / ind_price) - 1) * 100
            bid_spread = ((ind_price - best_bid) / ind_price) * 100

            now = datetime.now().strftime("%H:%M:%S")
            signal = ""

            # Ask below index = buy cheap on SideSwap
            if ask_spread < 0:
                signal = f"\033[32mCOMPRAR! Ask ${abs(best_ask - ind_price):,.0f} bajo indice\033[0m"
            # Bid above index = sell expensive on SideSwap
            elif bid_spread < 0:
                signal = f"\033[32mVENDER! Bid ${abs(best_bid - ind_price):,.0f} sobre indice\033[0m"
            # Large spread = opportunity
            elif ask_spread > threshold:
                signal = f"\033[33mAsk caro ({ask_spread:.2f}%)\033[0m"
            elif bid_spread > threshold:
                signal = f"\033[33mBid barato ({bid_spread:.2f}%)\033[0m"

            print(
                f"{now:>10}  ${ind_price:>11,.2f}"
                f"  ${best_ask:>11,.2f}  {ask_spread:>+7.2f}%"
                f"  ${best_bid:>11,.2f}  {bid_spread:>+7.2f}%"
                f"  {signal}"
            )


# ============================================================
# 11. FEDERATION — BTC reserves vs L-BTC supply
# ============================================================
LIQUID_API = "https://liquid.network/api/v1"
LIQUID_ESPLORA = "https://liquid.network/api"
ASSET_REGISTRY = "https://assets.blockstream.info"

UA = {"User-Agent": "sideswap-tools/1.0"}


def _fetch_json(path):
    """Fetch JSON from liquid.network API v1."""
    url = f"{LIQUID_API}{path}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _fetch_esplora(path):
    """Fetch JSON from liquid.network esplora API."""
    url = f"{LIQUID_ESPLORA}{path}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _fetch_registry(asset_id):
    """Fetch asset info from Blockstream registry."""
    url = f"{ASSET_REGISTRY}/{asset_id}"
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


async def cmd_federation(args):
    """Show federation BTC reserves vs L-BTC supply and addresses."""
    reserves = _fetch_json("/liquid/reserves")
    supply = _fetch_json("/liquid/pegs")
    status = _fetch_json("/liquid/reserves/status")
    addresses = _fetch_json("/liquid/reserves/addresses")
    addr_total = _fetch_json("/liquid/reserves/addresses/total")
    utxo_total = _fetch_json("/liquid/reserves/utxos/total")

    btc_locked = int(reserves["amount"])  # sats
    lbtc_supply = int(supply["amount"])   # sats
    diff = btc_locked - lbtc_supply
    ratio = btc_locked / lbtc_supply if lbtc_supply else 0

    print("FEDERACION LIQUID — BTC vs L-BTC")
    print("=" * 65)
    print(f"\n  BTC locked (mainchain):   {btc_locked / 1e8:>14,.8f} BTC")
    print(f"  L-BTC supply (sidechain): {lbtc_supply / 1e8:>14,.8f} BTC")
    print(f"  Diferencia:               {diff / 1e8:>+14,.8f} BTC")
    print(f"  Ratio reservas/supply:    {ratio:>14.6f}x", end="")
    if ratio >= 1.0:
        print(f"  \033[32m(saludable)\033[0m")
    else:
        print(f"  \033[31m(deficit!)\033[0m")

    print(f"\n  Ultimo bloque auditado:   {status.get('lastBlockAudit', '?')}")
    print(f"  Sincronizado:             {'Si' if status.get('isAuditSynced') else 'No'}")
    print(f"  Direcciones federacion:   {addr_total.get('address_count', '?')}")
    print(f"  UTXOs federacion:         {utxo_total.get('utxo_count', '?')}")

    print(f"\n  Top direcciones:")
    print(f"  {'#':>3}  {'BTC':>16}  {'Direccion'}")
    print(f"  {'-' * 75}")
    sorted_addrs = sorted(addresses, key=lambda a: int(a["balance"]), reverse=True)
    for i, a in enumerate(sorted_addrs[:10], 1):
        bal = int(a["balance"])
        print(f"  {i:>3}  {bal / 1e8:>16,.8f}  {a['bitcoinaddress']}")

    # Monthly trend (last 6 months)
    try:
        months = _fetch_json("/liquid/reserves/month")
        if months:
            recent = months[-6:]
            print(f"\n  Reservas ultimos {len(recent)} meses:")
            print(f"  {'Mes':>10}  {'BTC':>16}  {'Cambio':>12}")
            print(f"  {'-' * 45}")
            prev = None
            for m in recent:
                btc = int(m["amount"]) / 1e8
                change = ""
                if prev is not None:
                    d = btc - prev
                    change = f"{d:>+12,.4f}"
                print(f"  {m['date'][:7]:>10}  {btc:>16,.8f}  {change}")
                prev = btc
    except Exception:
        pass

    print(f"\n  Fuente: liquid.network (mempool.space)")


# ============================================================
# 12. PEGLIST — Recent peg-in/peg-out transactions
# ============================================================
async def cmd_peglist(args):
    """List recent peg-in transactions from liquid.network."""
    count = int(args[0]) if args else 25
    if count > 100:
        count = 100

    pegs = _fetch_json(f"/liquid/pegs/list/{count}")
    volume = _fetch_json("/liquid/pegs/volume")
    peg_count = _fetch_json("/liquid/pegs/count")

    # volume: [{"volume": pos, "number": N}, {"volume": neg, "number": N}]
    peg_in_vol = peg_out_vol = 0
    peg_in_n = peg_out_n = 0
    for v in volume:
        vol = int(v["volume"])
        if vol >= 0:
            peg_in_vol = vol
            peg_in_n = v["number"]
        else:
            peg_out_vol = abs(vol)
            peg_out_n = v["number"]

    print("PEG-INS Y PEG-OUTS — LIQUID NETWORK")
    print("=" * 65)
    print(f"\n  Total historico de pegs:  {peg_count.get('pegs_count', '?'):,}")
    print(f"\n  Volumen ultimas 24h:")
    print(f"    Peg-in  (BTC->L-BTC):  {peg_in_vol / 1e8:>12,.8f} BTC  ({peg_in_n} txs)")
    print(f"    Peg-out (L-BTC->BTC):  {peg_out_vol / 1e8:>12,.8f} BTC  ({peg_out_n} txs)")
    net = (peg_in_vol - peg_out_vol) / 1e8
    print(f"    Flujo neto:             {net:>+12,.8f} BTC  ({'entrada' if net >= 0 else 'salida'})")

    print(f"\n  Ultimos {len(pegs)} pegs (de liquid.network):")
    print(f"  {'#':>3}  {'Fecha':>20}  {'BTC':>16}  {'Tipo':>8}  {'TX (Liquid)'}")
    print(f"  {'-' * 95}")
    for i, p in enumerate(pegs, 1):
        amt = int(p["amount"])
        ts = p.get("blocktime", 0)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if ts else "?"
        txid = p.get("txid", "?")[:16] + "..."
        # Negative amount = peg-out (L-BTC leaving), positive = peg-in (BTC entering)
        tipo = "PEG-OUT" if amt < 0 else "PEG-IN"
        color = "\033[31m" if amt < 0 else "\033[32m"
        reset = "\033[0m"
        print(f"  {i:>3}  {dt:>20}  {abs(amt) / 1e8:>16,.8f}  {color}{tipo:>8}{reset}  {txid}")

    # Monthly pegs trend (last 6 months)
    try:
        months = _fetch_json("/liquid/pegs/month")
        if months:
            recent = months[-6:]
            print(f"\n  Flujo neto ultimos {len(recent)} meses:")
            print(f"  {'Mes':>10}  {'BTC neto':>16}  {'Direccion':>10}")
            print(f"  {'-' * 42}")
            for m in recent:
                net_m = int(m["amount"]) / 1e8
                direction = "entrada" if net_m >= 0 else "salida"
                print(f"  {m['date'][:7]:>10}  {net_m:>+16,.8f}  {direction:>10}")
    except Exception:
        pass

    print(f"\n  Fuente: liquid.network (mempool.space)")


# ============================================================
# 13. AUDIT — Federation security: UTXOs, timelocks, expired
# ============================================================
async def cmd_audit(args):
    """Federation security audit: UTXOs, timelocks, emergency-spent."""
    status = _fetch_json("/liquid/reserves/status")
    utxos = _fetch_json("/liquid/reserves/utxos")
    utxo_total = _fetch_json("/liquid/reserves/utxos/total")
    expired = _fetch_json("/liquid/reserves/utxos/expired")
    emergency = _fetch_json("/liquid/reserves/utxos/emergency-spent")
    emergency_stats = _fetch_json("/liquid/reserves/utxos/emergency-spent/stats")

    print("AUDITORIA DE SEGURIDAD — FEDERACION LIQUID")
    print("=" * 70)

    synced = status.get("isAuditSynced", False)
    print(f"\n  Estado de auditoria:")
    print(f"    Bitcoin blocks:         {status.get('bitcoinBlocks', '?')}")
    print(f"    Bitcoin headers:        {status.get('bitcoinHeaders', '?')}")
    print(f"    Ultimo bloque auditado: {status.get('lastBlockAudit', '?')}")
    color = "\033[32m" if synced else "\033[31m"
    print(f"    Sincronizado:           {color}{'Si' if synced else 'NO'}\033[0m")

    total_utxos = utxo_total.get("utxo_count", 0)
    print(f"\n  UTXOs de la federacion:   {total_utxos}")

    # Analyze timelocks
    current_height = status.get("bitcoinBlocks", 0)
    expiring_soon = []  # within 1000 blocks (~1 week)
    total_amount = 0
    timelocks = {}
    for u in utxos:
        amt = int(u.get("amount", 0))
        total_amount += amt
        tl = u.get("timelock", 0)
        timelocks[tl] = timelocks.get(tl, 0) + 1
        block_created = u.get("blocknumber", 0)
        expires_at = block_created + tl
        blocks_left = expires_at - current_height
        if 0 < blocks_left <= 1000:
            expiring_soon.append({**u, "blocks_left": blocks_left, "expires_at": expires_at})

    print(f"  BTC total en UTXOs:       {total_amount / 1e8:,.8f} BTC")

    print(f"\n  Timelocks configurados:")
    for tl, count in sorted(timelocks.items()):
        days = tl * 10 / 60 / 24  # ~10 min per block
        print(f"    {tl:>6} bloques (~{days:.0f} dias):  {count} UTXOs")

    # Expiring soon
    if expiring_soon:
        print(f"\n  \033[33m!! {len(expiring_soon)} UTXOs expiran en <1000 bloques (~1 semana):\033[0m")
        for u in sorted(expiring_soon, key=lambda x: x["blocks_left"]):
            print(f"    {u['blocks_left']:>5} bloques restantes  {int(u['amount'])/1e8:>14,.8f} BTC  tx:{u['txid'][:16]}...")
    else:
        print(f"\n  \033[32mNingun UTXO expira en los proximos ~1000 bloques\033[0m")

    # Expired UTXOs
    print(f"\n  UTXOs expirados:          {len(expired)}", end="")
    if len(expired) == 0:
        print(f"  \033[32m(ninguno — OK)\033[0m")
    else:
        print(f"  \033[31m(ALERTA)\033[0m")
        for u in expired[:5]:
            print(f"    {int(u.get('amount',0))/1e8:>14,.8f} BTC  bloque:{u.get('blocknumber','?')}  tx:{u.get('txid','?')[:16]}...")

    # Emergency spent
    em_count = emergency_stats.get("utxo_count", 0)
    em_amount = emergency_stats.get("total_amount") or 0
    print(f"\n  UTXOs emergency-spent:    {em_count}", end="")
    if em_count == 0:
        print(f"  \033[32m(ninguno — OK)\033[0m")
    else:
        print(f"  \033[31m(ALERTA — {int(em_amount)/1e8:,.8f} BTC)\033[0m")
        for u in emergency[:5]:
            print(f"    {int(u.get('amount',0))/1e8:>14,.8f} BTC  tx:{u.get('txid','?')[:16]}...")

    # Top UTXOs by size
    sorted_utxos = sorted(utxos, key=lambda u: int(u.get("amount", 0)), reverse=True)
    print(f"\n  Top 5 UTXOs por tamaño:")
    print(f"  {'#':>3}  {'BTC':>16}  {'Bloque':>8}  {'Timelock':>8}  {'TX'}")
    print(f"  {'-' * 75}")
    for i, u in enumerate(sorted_utxos[:5], 1):
        amt = int(u.get("amount", 0))
        print(f"  {i:>3}  {amt/1e8:>16,.8f}  {u.get('blocknumber','?'):>8}  {u.get('timelock','?'):>8}  {u.get('txid','?')[:20]}...")

    print(f"\n  Fuente: liquid.network (mempool.space)")


# ============================================================
# 14. ACTIVITY — Liquid network stats: blocks, mempool, fees
# ============================================================
async def cmd_activity(args):
    """Liquid network activity: recent blocks, mempool, fees."""
    blocks = _fetch_esplora("/blocks")
    mempool = _fetch_esplora("/mempool")
    fees = _fetch_json("/fees/recommended")
    tip = _fetch_esplora("/blocks/tip/height")

    print("ACTIVIDAD RED LIQUID")
    print("=" * 70)

    print(f"\n  Altura actual:            {tip}")
    print(f"  Fee recomendado:          {fees.get('fastestFee', '?')} sat/vB")

    # Mempool
    mp_count = mempool.get("count", 0)
    mp_vsize = mempool.get("vsize", 0)
    mp_fee = mempool.get("total_fee", 0)
    print(f"\n  Mempool:")
    print(f"    Transacciones:          {mp_count}")
    print(f"    Tamaño:                 {mp_vsize:,} vB ({mp_vsize/1000:.1f} kvB)")
    print(f"    Fees totales:           {mp_fee:,} sats")

    # Recent blocks analysis
    print(f"\n  Ultimos {min(10, len(blocks))} bloques:")
    print(f"  {'#':>3}  {'Altura':>8}  {'Hora':>8}  {'TXs':>5}  {'Tamaño':>10}  {'Intervalo'}")
    print(f"  {'-' * 60}")

    intervals = []
    for i, b in enumerate(blocks[:10]):
        ts = b.get("timestamp", 0)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M:%S")
        txs = b.get("tx_count", 0)
        size = b.get("size", 0)
        interval = ""
        if i < len(blocks) - 1:
            next_ts = blocks[i + 1].get("timestamp", 0)
            diff = ts - next_ts
            intervals.append(diff)
            interval = f"{diff}s"
        print(f"  {i+1:>3}  {b.get('height','?'):>8}  {dt:>8}  {txs:>5}  {size:>8,} B  {interval:>10}")

    if intervals:
        avg_int = sum(intervals) / len(intervals)
        print(f"\n  Intervalo promedio:       {avg_int:.0f}s (~{avg_int/60:.1f} min)")
        print(f"  Intervalo esperado:       60s (1 min)")

    # Tx count stats
    tx_counts = [b.get("tx_count", 0) for b in blocks[:10]]
    if tx_counts:
        print(f"\n  TXs por bloque:")
        print(f"    Promedio:               {sum(tx_counts)/len(tx_counts):.1f}")
        print(f"    Max:                    {max(tx_counts)}")
        print(f"    Min:                    {min(tx_counts)}")

    print(f"\n  Fuente: liquid.network (mempool.space)")


# ============================================================
# 15. ASSETS — Liquid asset explorer with supply info
# ============================================================

# Known featured assets with precision (from Blockstream registry)
FEATURED_ASSETS = [
    ("6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d", "L-BTC", "Liquid Bitcoin", 8, "blockstream.com"),
    ("ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2", "USDt", "Tether USD", 8, "tether.to"),
    ("18729918ab4bca843656f08d4dd877bed6641fbd596a0a963abbf199cfeb3cec", "EURx", "PEGx EUR", 8, "pegx.io"),
    ("02f22f8d9c76ab41661a2729e4752e2c5d1a263012141b86ea98af5472df5189", "DePix", "Decentralized Pix", 8, "depix.info"),
    ("26ac924263ba547b706251635550a8649545ee5c074fe5db8d7140557baaf32e", "MEX", "Mexas", 8, "mexas.xyz"),
    ("0dea022a8a25abb128b42b0f8e98532bc8bd74f8a77dc81251afcc13168acef7", "FUSD", "Fuji USD", 8, "fuji.money"),
    ("79b6b75e951a9c723e215cc0492f08ad6d7b95fcef1826265e8e9ea1e58cc69c", "USTBL", "USTBL", 8, "bitfinex.com"),
]


async def cmd_assets(args):
    """Liquid asset explorer: supply, issuances, tx count."""
    # If a specific asset is requested
    target = args[0].upper() if args else None

    if target and target not in ("ALL", "LIST"):
        # Find the asset
        found = None
        for aid, ticker, name, prec, domain in FEATURED_ASSETS:
            if ticker.upper() == target:
                found = (aid, ticker, name, prec, domain)
                break

        if not found:
            # Try as asset ID
            if len(target) == 64:
                found = (target.lower(), "?", "?", 8, "?")
            else:
                print(f"Asset '{target}' no encontrado. Assets conocidos:")
                for _, ticker, name, _, _ in FEATURED_ASSETS:
                    print(f"  {ticker:>6}  {name}")
                return

        aid, ticker, name, precision, domain = found
        await _show_asset_detail(aid, ticker, name, precision, domain)
        return

    # Show overview of all featured assets
    print("ASSETS LIQUID NETWORK")
    print("=" * 90)
    print(f"\n  {'Ticker':>6}  {'Nombre':<25}  {'Supply':>20}  {'Emitido':>20}  {'TXs':>8}  {'Emisor'}")
    print(f"  {'-' * 90}")

    for aid, ticker, name, precision, domain in FEATURED_ASSETS:
        try:
            if ticker == "L-BTC":
                # L-BTC uses different stats
                data = _fetch_esplora(f"/asset/{aid}")
                cs = data.get("chain_stats", {})
                peg_in = cs.get("peg_in_amount", 0)
                peg_out = cs.get("peg_out_amount", 0)
                burned = cs.get("burned_amount", 0)
                supply = (peg_in - peg_out - burned) / 10**precision
                issued = peg_in / 10**precision
                txs = cs.get("tx_count", 0)
                print(f"  {ticker:>6}  {name:<25}  {supply:>20,.2f}  {issued:>20,.2f}  {txs:>8,}  {domain}")
            else:
                data = _fetch_esplora(f"/asset/{aid}")
                cs = data.get("chain_stats", {})
                issued = cs.get("issued_amount", 0)
                burned = cs.get("burned_amount", 0)
                supply = (issued - burned) / 10**precision
                issued_fmt = issued / 10**precision
                txs = cs.get("tx_count", 0)
                # For stablecoins, show as currency
                print(f"  {ticker:>6}  {name:<25}  {supply:>20,.2f}  {issued_fmt:>20,.2f}  {txs:>8,}  {domain}")
        except Exception as e:
            print(f"  {ticker:>6}  {name:<25}  {'error':>20}  {str(e)[:30]}")

    print(f"\n  Detalle: sideswap_tools.py assets <TICKER>")
    print(f"  Fuente: liquid.network + assets.blockstream.info")


async def _show_asset_detail(aid, ticker, name, precision, domain):
    """Show detailed info for a single asset."""
    data = _fetch_esplora(f"/asset/{aid}")
    cs = data.get("chain_stats", {})
    ms = data.get("mempool_stats", {})

    # Try to get registry info
    reg = _fetch_registry(aid)
    if reg:
        name = reg.get("name", name)
        ticker = reg.get("ticker", ticker)
        precision = reg.get("precision", precision)
        domain = reg.get("entity", {}).get("domain", domain)

    print(f"ASSET: {name} ({ticker})")
    print("=" * 70)

    print(f"\n  Asset ID:    {aid}")
    print(f"  Emisor:      {domain}")
    print(f"  Precision:   {precision} decimales")

    if ticker == "L-BTC":
        peg_in = cs.get("peg_in_amount", 0)
        peg_out = cs.get("peg_out_amount", 0)
        burned = cs.get("burned_amount", 0)
        supply = peg_in - peg_out - burned

        print(f"\n  Estadisticas on-chain:")
        print(f"    Peg-ins:         {cs.get('peg_in_count', 0):>10,}  ({peg_in / 1e8:>14,.8f} BTC)")
        print(f"    Peg-outs:        {cs.get('peg_out_count', 0):>10,}  ({peg_out / 1e8:>14,.8f} BTC)")
        print(f"    Quemados:        {cs.get('burn_count', 0):>10,}  ({burned / 1e8:>14,.8f} BTC)")
        print(f"    Supply actual:            {supply / 1e8:>14,.8f} BTC")
        print(f"    Total TXs:       {cs.get('tx_count', 0):>10,}")
    else:
        issued = cs.get("issued_amount", 0)
        burned = cs.get("burned_amount", 0)
        supply = issued - burned
        div = 10 ** precision

        print(f"\n  Estadisticas on-chain:")
        print(f"    Emitido total:   {issued / div:>20,.2f} {ticker}")
        print(f"    Quemado:         {burned / div:>20,.2f} {ticker}")
        print(f"    Supply actual:   {supply / div:>20,.2f} {ticker}")
        print(f"    Emisiones:       {cs.get('issuance_count', 0):>10,}")
        print(f"    Total TXs:       {cs.get('tx_count', 0):>10,}")

        if cs.get("has_blinded_issuances"):
            print(f"    \033[33m!! Tiene emisiones confidenciales — supply real puede diferir\033[0m")

    # Mempool
    mp_txs = ms.get("tx_count", 0)
    if mp_txs:
        print(f"\n  En mempool:        {mp_txs} txs pendientes")

    # Issuance info
    status = data.get("status", {})
    if status.get("confirmed"):
        ts = status.get("block_time", 0)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else "?"
        print(f"\n  Primera emision:   {dt} (bloque {status.get('block_height', '?')})")

    # Reissuance token
    if data.get("reissuance_token"):
        print(f"  Reissuance token:  {data['reissuance_token'][:20]}...")
        rt = cs.get("reissuance_tokens", 0)
        brt = cs.get("burned_reissuance_tokens", 0)
        print(f"  Tokens reemision:  {rt} activos, {brt} quemados")

    # For USDt specifically, show supply context
    if ticker == "USDt" and supply > 0:
        div = 10 ** precision
        supply_m = supply / div / 1e6
        print(f"\n  Contexto USDt en Liquid:")
        print(f"    Supply:          ${supply / div:>20,.2f}")
        print(f"                     ~${supply_m:,.1f}M")

    print(f"\n  Fuente: liquid.network + assets.blockstream.info")


# ============================================================
# MAIN
# ============================================================
COMMANDS = {
    "history": ("Exportar historico OHLCV a CSV", "history [BASE] [QUOTE] [archivo.csv]", cmd_history),
    "spread": ("Monitor de spread en vivo", "spread [threshold_%]", cmd_spread),
    "whales": ("Monitor de ordenes grandes", "whales [min_btc]", cmd_whales),
    "calc": ("Calculadora inversa (BTC exacto)", "calc <buy|sell> <btc>", cmd_calc),
    "limit": ("Simulador de limit order", "limit <buy|sell> <btc> <price>", cmd_limit),
    "alert": ("Alertas de precio", "alert <ask_below|bid_above|both> <price> [price2]", cmd_alert),
    "peg": ("Estado peg-in/peg-out y fees", "peg", cmd_peg),
    "arb": ("Detector de arbitraje vs indice", "arb [threshold_%]", cmd_arb),
    "federation": ("BTC reserves vs L-BTC supply", "federation", cmd_federation),
    "peglist": ("Lista reciente de peg-ins/outs", "peglist [count]", cmd_peglist),
    "audit": ("Auditoria seguridad federacion", "audit", cmd_audit),
    "activity": ("Actividad red Liquid", "activity", cmd_activity),
    "assets": ("Explorer de assets Liquid", "assets [TICKER|all]", cmd_assets),
}


def print_help():
    print("SideSwap Tools")
    print("=" * 70)
    print(f"\nUso: {sys.argv[0]} <comando> [args...]\n")
    print(f"{'Comando':<10}  {'Descripcion':<35}  {'Uso'}")
    print("-" * 70)
    for cmd, (desc, usage, _) in COMMANDS.items():
        print(f"{cmd:<10}  {desc:<35}  {usage}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    if cmd not in COMMANDS:
        print(f"Comando desconocido: {cmd}")
        print_help()
        sys.exit(1)

    try:
        asyncio.run(COMMANDS[cmd][2](sys.argv[2:]))
    except KeyboardInterrupt:
        print("\nBye!")
