# stablecoin-expert

Your AI assistant for acquiring stablecoins (USDT/USDC) from BTC or fiat **without KYC**. Compares 15+ routes across Liquid, Ethereum, Arbitrum, Polygon and Rootstock in real time.

Works with **Claude Code**.

## Why use this?

Getting stablecoins from Bitcoin without KYC involves choosing between multiple services, chains, and swap paths — each with different fees, speed, privacy, and liquidity tradeoffs. This skill does the comparison for you automatically using **live data**.

### Before stablecoin-expert
> "I want to convert 0.05 BTC to USDT"
> *Googles options, picks THORSwap because it's popular, pays 0.5% in outbound fees without realizing SideSwap + Liquid would have cost 0.3%*

### With stablecoin-expert
> "I want to convert 0.05 BTC to USDT"
> *Skill queries live fees from mempool.space, SideSwap orderbook, Boltz, and Chainflip — shows you the exact cost of each route with a full fee breakdown, and recommends the cheapest one*

**That's $15+ saved on a single $1,500 swap.** It adds up fast.

---

## What it can do

### 1. Find the cheapest route — with live fees

Tell it what you have and what you need. It queries APIs in real time:

> **You**: tengo 500k sats y quiero L-USDT para lending
>
> **Skill**:
> ```
> Ruta recomendada: SideSwap peg-in → SideSwap Instant
>
> Fee desglosado:
>   1. SideSwap peg-in:         ~500 sats (0.1%)
>   2. SideSwap spread:         ~594 sats (0.18%)
>   3. SideSwap taker fee:      ~997 sats (0.2%)
>   ─────────────────────────────────────────
>   TOTAL: ~2,091 sats (0.42%)
>
> Tiempo: ~15 min (2 conf BTC + instant swap)
> ```

### 2. Cover every starting point

The skill handles any combination:

| You have | You want | Routes available |
|----------|----------|-----------------|
| BTC on-chain | L-USDT (Liquid) | SideSwap peg-in + swap, Boltz chain swap |
| BTC on-chain | USDT/USDC (EVM) | Chainflip, LendaSat, Boltz USDT, THORSwap |
| Lightning | L-USDT | Boltz LN→L-BTC + SideSwap |
| Lightning | USDC (EVM) | LendaSat gasless |
| L-BTC | L-USDT | SideSwap Instant or Maker |
| Fiat (EUR/USD/33 currencies) | USDC | Peer.xyz (no KYC, ZK proofs) |
| L-USDT | BTC (return trip) | SideSwap + Boltz via Tor |

### 3. Query the SideSwap orderbook live

The skill includes `sideswap_tools.py` — a WebSocket client that connects to SideSwap's API:

- **Market orders**: simulate buy/sell and see exactly which orders get filled
- **Spread analysis**: real-time bid/ask spread with historical comparison
- **OHLCV data**: price history for any SideSwap market
- **Whale detection**: large orders on the book
- **Peg monitoring**: L-BTC peg premium/discount vs BTC
- **Arbitrage scanner**: cross-market opportunities
- **Price alerts**: notify when spread hits your target

### 4. Guide you step by step

Each route has a detailed walkthrough:

- **SideSwap peg-in + swap** (the Liquid lending circuit)
- **Boltz atomic swaps** (BTC/LN ↔ L-BTC, BTC ↔ USDT)
- **Chainflip** (BTC → USDC/USDT on EVM, no wallet connect)
- **LendaSat** (LN → USDC gasless on Polygon)
- **THORSwap** (high liquidity, but watch the outbound fee)
- **Peer.xyz** (fiat → USDC with ZK proofs, no KYC)

### 5. Explain privacy and security tradeoffs

> **You**: which route is most private?
>
> **Skill**: For Liquid: confidential transactions hide amounts. For the return trip (L-USDT → BTC), use Boltz via Tor — it's an atomic swap, no federation involved, your IP stays hidden. Avoid SideSwap peg-out for the return because it goes through the Liquid federation.

The skill knows which services log what, which support Tor, and where your privacy is strongest.

### 6. Handle the full lending circuit

Optimized for the [HodlHodl Lend](https://lend.hodlhodl.com) workflow:

```
IDA:    BTC → SideSwap peg-in (0.1%) → L-BTC → SideSwap → L-USDT → HodlHodl Lend
VUELTA: L-USDT → SideSwap → L-BTC → Boltz chain swap (Tor) → BTC

Round-trip cost: ~0.7% (Instant) or ~0.3-0.4% (Maker)
```

---

## Services covered

| Service | What it does | Fee range |
|---------|-------------|-----------|
| [SideSwap](https://sideswap.io) | Peg-in/out + L-BTC/L-USDT orderbook | 0.1% peg + 0.2% taker |
| [Boltz](https://boltz.exchange) | Atomic swaps BTC/LN ↔ L-BTC, BTC ↔ USDT | 0.1-0.25% |
| [Chainflip](https://chainflip.io) | BTC → USDC/USDT on EVM (no wallet connect) | ~0.2-0.3% |
| [LendaSat](https://lendasat.com) | LN → USDC gasless on Polygon | 1.2-2% real |
| [THORSwap](https://thorswap.finance) | BTC ↔ stablecoins (high liquidity) | Variable + outbound fee |
| [Peer.xyz](https://peer.xyz) | Fiat → USDC (33 currencies, ZK proofs) | 0-1.5% spread |

## Supported chains

Liquid, Ethereum, Arbitrum, Polygon, Rootstock, Base, and 20+ more via Boltz USDT.

## Installation

### Claude Code

```bash
git clone https://github.com/4rkad/stablecoin-expert.git /tmp/stablecoin-expert && \
mkdir -p ~/.claude/skills/stablecoin-expert/ && \
cp -r /tmp/stablecoin-expert/* ~/.claude/skills/stablecoin-expert/ && \
rm -rf /tmp/stablecoin-expert
```

**Restart Claude Code** (or start a new conversation), then test it:

> "I have 0.01 BTC and want USDT on Arbitrum — what's the cheapest route?"

The skill activates automatically when it detects questions about stablecoins, swapping BTC to USDT/USDC, or preparing for HodlHodl lending.

## Structure

```
stablecoin-expert/
├── README.md
├── SKILL.md                          # Main skill file with routing logic
├── sideswap_tools.py                 # SideSwap WebSocket client + analytics
└── references/
    ├── rutas-completas.md            # Complete route comparison table
    ├── guias-paso-a-paso.md          # Step-by-step guides per service
    ├── cross-chain.md                # Moving stablecoins between chains
    ├── consideraciones.md            # Privacy, risks, censorship
    ├── chainflip.md                  # Chainflip-specific details
    ├── sideswap-core-reference.md    # SideSwap API + orderbook presentation
    ├── sideswap-api-reference.md     # WebSocket methods + asset IDs
    ├── sideswap-maker-guide.md       # Market maker setup
    ├── peer-*.md                     # Peer.xyz guides (buying, selling, troubleshooting, etc.)
    └── ...
```

## Related skills

- **[peer-expert](https://github.com/4rkad/peer-expert)** — Deep dive into Peer.xyz: live rates, step-by-step buying/selling, troubleshooting
- **sideswap** (coming soon) — Dedicated SideSwap orderbook skill

## Community

- **Semilla Bitcoin**: https://semillabitcoin.com
- **SideSwap**: https://sideswap.io
- **Boltz**: https://boltz.exchange
- **Chainflip**: https://chainflip.io
- **Peer.xyz**: https://peer.xyz

## License

MIT
