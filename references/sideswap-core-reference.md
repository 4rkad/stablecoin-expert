# SideSwap — Core Reference (Presentation, Markets, API, Fees, Tools)

## Instant Swap vs Swap Market (Orderbook)

SideSwap tiene DOS interfaces para el mismo orderbook:

- **Instant Swap**: Toma automaticamente las mejores ordenes del orderbook. El usuario ve "Send X / Receive Y / Price Z" en la app. Fee 0.2% como taker. Rapido, sin interaccion manual con el libro.
- **Swap Market (Orderbook)**: Muestra las ordenes individuales. Puedes ser taker (ejecutar contra ordenes existentes, fee 0.2%) o maker (publicar tu propia orden, fee 0%).

**Ambos usan el mismo orderbook y la misma fee 0.2% como taker.** El Instant Swap simplemente automatiza la ejecucion.

**NOTA**: El script inline de este skill consulta el orderbook publico. Los resultados deben coincidir con lo que muestra el Instant Swap en la app. Si hay diferencias menores, es por variacion temporal del orderbook entre la consulta y la ejecucion.

## How to Present Results

After running the orderbook script, present a clean summary to the user:

1. **Orders taken**: Table showing each order hit (price, BTC, USDt, FULL/PARTIAL, spread)
2. **Cost breakdown**:
   - Spread: maker price vs index price (%)  and approximate dollar amount
   - Taker fee: 0.2% on BTC received and approximate dollar amount
   - Total cost: combined percentage vs index
3. **Result**: Net BTC received and effective price per BTC
4. **Nota**: El resultado debe coincidir con el Instant Swap de la app (mismo orderbook, misma fee 0.2%)

## Supported Markets

Query `list_markets` for the full list. Common pairs:
- **L-BTC / USDt** (Stablecoin) — most liquid
- **L-BTC / EURx** (Stablecoin)
- **EURx / USDt** (Stablecoin)
- **L-BTC / DEPIX** (Stablecoin — Brazilian Real)
- **AMP assets / L-BTC** (Amp tokens)

### Asset IDs

```
LBTC:  6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d
USDT:  ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2
EURX:  18729918ab4bca843656f08d4dd877bed6641fbd596a0a963abbf199cfeb3cec
DEPIX: 02f22f8d9c76ab41661a2729e4752e2c5d1a263012141b86ea98af5472df5189
```

## WebSocket API

- **Endpoint**: `wss://api.sideswap.io/json-rpc-ws` (JSON-RPC 2.0)
- **Testnet**: `wss://api-testnet.sideswap.io/json-rpc-ws`
- **Docs**: https://sideswap.io/docs/

### Key Methods (all use `method: "market"`)

| Action | Params key |
|--------|-----------|
| List markets | `list_markets: {}` |
| Subscribe orderbook | `subscribe: {asset_pair: {base, quote}}` |
| Unsubscribe | `unsubscribe: {asset_pair: {base, quote}}` |
| Chart data (OHLCV) | `chart_sub: {asset_pair: {base, quote}}` |
| Start quotes (taker) | `start_quotes: {asset_pair, asset_type, amount, trade_dir, utxos, receive_address, change_address}` |

### Notifications after subscribe

| Event | Description |
|-------|-------------|
| `subscribe.orders` | Initial snapshot — full order list |
| `public_order_created` | New order added |
| `public_order_removed` | Order removed (filled/cancelled) |
| `market_price` | Index price + last trade price update |

### Order Fields

| Field | Description |
|-------|-------------|
| `order_id` | Unique ID |
| `price` | Price in quote asset per 1 BTC |
| `amount` | Amount in satoshis of base asset |
| `trade_dir` | `"Buy"` or `"Sell"` |
| `online` | `true` = maker online, `false` = offline (signed SIGHASH_SINGLE) |

## Fee Structure

- **Makers**: 0% fee
- **Takers**: 0.2% fee on matched amount + fixed network fee for asset/asset swaps
- **Peg-In** (BTC -> L-BTC): 0.1% fee, min 10,000 sats
- **Peg-Out** (L-BTC -> BTC): 0.1% fee, min 25,000 sats
- For asset/asset swaps (e.g., USDt/EURx), the server includes its own L-BTC inputs to cover the network fee

## sideswap_tools.py — CLI Multi-Tool

Located at `{baseDir}/sideswap_tools.py`. Run with: `/tmp/swvenv/bin/python {baseDir}/sideswap_tools.py <command>`

If venv doesn't exist: `python3 -m venv /tmp/swvenv && /tmp/swvenv/bin/pip install -q websockets`

### Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `history` | Export OHLCV history to CSV | `history [BASE] [QUOTE] [file.csv]` |
| `spread` | Real-time spread monitor | `spread [threshold_%]` — alerts when spread < threshold |
| `whales` | Monitor large orders entering/leaving | `whales [min_btc]` — default 0.1 BTC |
| `calc` | Inverse calculator (exact BTC amount) | `calc buy 0.5` or `calc sell 1.0` |
| `limit` | Limit order simulator | `limit sell 0.5 68000` — where would my order sit |
| `alert` | Price alerts | `alert ask_below 65000` or `alert both 65000 67000` |
| `peg` | Peg-in/out status and fees | `peg` or `peg -v` for all assets |
| `arb` | Arbitrage detector vs index | `arb [threshold_%]` — default 1% |
| `federation` | BTC reserves vs L-BTC supply | `federation` — ratio, addresses, monthly trend |
| `peglist` | Recent peg-in/peg-out transactions | `peglist [count]` — default 25, max 100 |
| `audit` | Federation security audit | `audit` — UTXOs, timelocks, expired, emergency-spent |
| `activity` | Liquid network activity | `activity` — blocks, mempool, fees, tx stats |
| `assets` | Liquid asset explorer | `assets` (overview) or `assets <TICKER>` (detail) |

### When to use each tool

- User asks "cuanto BTC por X USDt" → Use inline script (buy simulation) or `calc buy`
- User asks "cuanto necesito para comprar X BTC" → `calc buy <btc>`
- User asks "donde quedaria mi orden" → `limit <buy|sell> <btc> <price>`
- User asks "historico de precios" → `history`
- User asks "monitoreame el spread/precio" → `spread` or `alert` (these run indefinitely)
- User asks "que pasa con peg-in/peg-out" → `peg` (fees SideSwap) or `peglist` (txs recientes)
- User asks "hay oportunidad de arbitraje" → `arb`
- User asks "cuanto BTC tiene la federacion" / "ratio reservas" / "esta saludable liquid" → `federation`
- User asks "ultimos pegins/pegouts" / "flujo de BTC a liquid" → `peglist`
- User asks "seguridad federacion" / "UTXOs expiran" / "emergency spent" → `audit`
- User asks "actividad liquid" / "bloques" / "mempool liquid" → `activity`
- User asks "supply USDt en liquid" / "assets liquid" / "cuanto USDt hay" → `assets` or `assets usdt`
