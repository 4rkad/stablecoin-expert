# SideSwap API Reference

## Connection

- **Mainnet**: `wss://api.sideswap.io/json-rpc-ws`
- **Testnet**: `wss://api-testnet.sideswap.io/json-rpc-ws`
- **Protocol**: JSON-RPC 2.0 over WebSocket
- **Batch requests**: NOT supported
- **Docs**: https://sideswap.io/docs/

## Liquid Asset IDs

### Mainnet

| Asset | ID |
|-------|-----|
| L-BTC | `6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d` |
| USDt (Tether) | `ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2` |
| EURx (Stasis Euro) | `18729918ab4bca843656f08d4dd877bed6641fbd596a0a963abbf199cfeb3cec` |
| DEPIX (BRL stablecoin) | `02f22f8d9c76ab41661a2729e4752e2c5d1a263012141b86ea98af5472df5189` |
| SSWP (SideSwap token) | `06d1085d6a3a1328fb8189d106c7a8afbef3d327e34504828c4cac2c74ac0802` |

### Testnet

| Asset | ID |
|-------|-----|
| L-BTC | `144c654344aa716d6f3abcc1ca90e5641e4e2a7f633bc09fe3baf64585819a49` |
| USDt | `b612eb46313a2cd6ebabd8b7a8eed5696e29898b87a43bff41c94f51acef9d73` |

## Methods

### List all assets

```json
{"id": 4, "method": "assets", "params": {"all_assets": true}}
```

### List markets

```json
{"id": 1, "method": "market", "params": {"list_markets": {}}}
```

Response includes array of markets with `asset_pair` (base/quote), `fee_asset`, and `type` (Stablecoin/Amp/Token).

### Subscribe to orderbook

```json
{
  "id": 1, "method": "market",
  "params": {
    "subscribe": {
      "asset_pair": {
        "base": "<base_asset_id>",
        "quote": "<quote_asset_id>"
      }
    }
  }
}
```

Returns initial snapshot with all orders, then streams `public_order_created`, `public_order_removed`, and `market_price` updates.

### Unsubscribe from orderbook

```json
{
  "id": 1, "method": "market",
  "params": {
    "unsubscribe": {
      "asset_pair": {"base": "...", "quote": "..."}
    }
  }
}
```

### Subscribe to chart data (OHLCV)

```json
{
  "id": 2, "method": "market",
  "params": {
    "chart_sub": {
      "asset_pair": {"base": "...", "quote": "..."}
    }
  }
}
```

Returns daily OHLCV data (open, high, low, close, volume, time) and streams `chart_update` notifications.

### Start quotes (taker flow)

```json
{
  "id": 3, "method": "market",
  "params": {
    "start_quotes": {
      "asset_pair": {"base": "...", "quote": "..."},
      "asset_type": "Base",
      "amount": 100000,
      "trade_dir": "Sell",
      "utxos": [...],
      "receive_address": "...",
      "change_address": "..."
    }
  }
}
```

- `asset_type`: "Base" or "Quote" — which asset the `amount` refers to
- `trade_dir`: "Buy" or "Sell" from the taker's perspective relative to the base asset
- `utxos`: list of UTXO objects. Can be empty to just get expected amounts.
- Server constructs PSET and sends quote notifications every ~5 seconds
- Taker has ~30 seconds to accept a quote

### Peg-in / Peg-out

```json
{"id": 1, "method": "peg", "params": {"peg_in": true, "recv_addr": "..."}}
```

## Order Structure

```json
{
  "order_id": 1760719504874,
  "price": 66287.78,
  "amount": 33330000,
  "trade_dir": "Sell",
  "online": false,
  "asset_pair": {"base": "...", "quote": "..."}
}
```

- `amount`: in satoshis of the base asset
- `price`: in quote asset units per 1 whole unit of base asset
- `online`: true = maker connected and will sign live; false = pre-signed offline order (SIGHASH_SINGLE|ANYONECANPAY)
- Online orders can be partially matched; offline orders must be fully matched

## Fee Structure

- **Makers**: 0% fee
- **Takers**: 0.2% fee on the matched BTC amount
- Plus a fixed fee to cover the Liquid network transaction fee
- For asset/asset swaps, the server includes its own L-BTC inputs to cover the network fee

## Market Maker

To run your own dealer: https://github.com/sideswap-io/sideswapclient/tree/master/rust/sideswap_dealer_elements
