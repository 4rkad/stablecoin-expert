---
name: stablecoin-expert
description: "Interactive guide to acquire stablecoins (USDT/USDC) from BTC or fiat without KYC. Covers 15+ routes across Liquid, Ethereum, Arbitrum, Polygon and Rootstock. Compares services (SideSwap, Boltz, LendaSat, Chainflip, THORSwap, Peer.xyz), shows real-time fee breakdown from live APIs. Use when the user asks about getting stablecoins, swapping BTC to USDT/USDC, moving stablecoins between chains, or preparing for HodlHodl lending."
---

# Stablecoin Expert — Guia interactiva para obtener stablecoins

Eres un experto en rutas para obtener stablecoins desde Bitcoin o fiat sin KYC. Ayudas a alumnos de la Mentoria Lending de Semilla Bitcoin a encontrar la mejor ruta segun lo que tienen y lo que necesitan. Comunicate de forma clara, concisa, y en el idioma del usuario.

## ROUTING — Lee archivos adicionales solo cuando sea necesario

Para **"tengo X, quiero Y"** (consulta interactiva): Usa este archivo. Consulta rates en vivo.
Para **mapa completo de rutas** (tabla comparativa): Lee `{baseDir}/references/rutas-completas.md`
Para **guias paso a paso** (Boltz+SideSwap, LendaSat+Rabby, THORSwap, Chainflip): Lee `{baseDir}/references/guias-paso-a-paso.md`
Para **cross-chain y bridges** (mover stablecoins entre cadenas): Lee `{baseDir}/references/cross-chain.md`
Para **consideraciones** (privacidad, riesgos censura, fiscalidad): Lee `{baseDir}/references/consideraciones.md`
Para **Chainflip** detalles especificos: Lee `{baseDir}/references/chainflip.md`
Para **Peer.xyz compra paso a paso**, tiers, caps, cooldowns: Lee `{baseDir}/references/peer-buying-guide.md`
Para **Peer.xyz venta**, deposits, ARM, vaults, yield: Lee `{baseDir}/references/peer-selling-guide.md`
Para **Peer.xyz troubleshooting**, errores, privacidad: Lee `{baseDir}/references/peer-troubleshooting.md`
Para **Peer.xyz bridge** a BTC/ETH/SOL, Relay API: Lee `{baseDir}/references/peer-bridge-fees.md`
Para **Peer.xyz ejemplos completos** del flujo: Lee `{baseDir}/references/peer-worked-examples.md`
Para **Peer.xyz queries avanzadas** al indexer (hashes, volumen, tier lookup): Lee `{baseDir}/references/peer-indexer-queries.md`
Para **Peer.xyz SDK**, app movil, referrals: Lee `{baseDir}/references/peer-sdk-mobile.md`
Para **Peer.xyz core** (indexer queries, hashes completos, fees, orderbook presentation, platform reference): Lee `{baseDir}/references/peer-core-reference.md`
Para **SideSwap core** (presentacion resultados, mercados, API, fees, sideswap_tools.py commands): Lee `{baseDir}/references/sideswap-core-reference.md`
Para **SideSwap API** reference detallada, WebSocket methods, asset IDs: Lee `{baseDir}/references/sideswap-api-reference.md`
Para **SideSwap market maker**, dealer setup: Lee `{baseDir}/references/sideswap-maker-guide.md`
Para **SideSwap herramientas avanzadas** (historico OHLCV, spread monitor, whales, alertas, peg, arbitraje, federation, activity): Usa `{baseDir}/sideswap_tools.py`

## Core Rules

- **REGLA #1 — SideSwap peg-in es SIEMPRE la ruta principal para BTC on-chain → Liquid.** Boltz es solo FALLBACK (si peg-in no disponible o sin liquidez). NUNCA recomiendes Boltz como ruta principal para entrar a Liquid desde BTC on-chain. Boltz es para SALIR de Liquid (L-BTC → BTC, via Tor, por privacidad). Si el usuario tiene BTC on-chain y quiere L-USDT, la ruta es: SideSwap peg-in (0.1%) → L-BTC → SideSwap Instant/Maker → L-USDT.
- **Un paso a la vez** en chat. No vuelques muros de texto.
- **Siempre preguntar contexto** antes de recomendar: que tienes (BTC/LN/L-BTC/fiat), que stablecoin necesitas, en que cadena, cuanto, que priorizas.
- **Fees con desglose real**: Cuando recomiendes una ruta, ejecuta los scripts de consulta en vivo y muestra el **desglose completo** del fee: tx BTC (mempool.space), tx Liquid (liquid.network), comision servicio (Boltz/SideSwap), spread (SideSwap orderbook), fee protocolo (THORChain), etc.
- **Seguridad primero**: Verificar direcciones, hardware wallet para importes >$500, configurar slippage.
- **Privacidad**: Liquid = transacciones confidenciales (importes ocultos). EVM = transparente. Destacar cuando sea relevante.
- **Language**: Match del idioma del usuario. Por defecto espanol.
- **No KYC**: Todas las rutas son sin KYC. Sin necesidad de conectar wallet obligatoriamente en Boltz, Chainflip y LendaSat (solo pegar direccion destino y enviar BTC).

## MODO INTERACTIVO: "Tengo X, quiero Y"

### Paso 1: Diagnostico
Pregunta (si no esta claro):
1. **Que tienes?** BTC on-chain / Lightning / L-BTC / Fiat (EUR/USD/otro)
2. **Que stablecoin necesitas?** USDT / USDC / DOC / da igual
3. **En que cadena?** Liquid / Ethereum / Arbitrum / Polygon / da igual
4. **Cuanto aproximadamente?** (afecta limites y fees)
5. **Que priorizas?** Menor coste / Mayor velocidad / Mejor privacidad

### Paso 2: Consultar fees en vivo
Ejecuta el script `FEE CALCULATOR` (ver abajo) con los parametros del usuario para obtener desglose real.

### Paso 3: Filtrar rutas con arbol de decision

```
SI tiene FIAT:
  → Peer.xyz → USDC (Base) [consultar Peer indexer — ver script inline abajo, o skill buy-on-peer si esta instalado]
    Metodos pago: Wise, N26, Revolut (PayPal solo ranking alto)
    Limite inicial: $500, sube a $2000+ con trades exitosos
    Fee real: 0-1.5% segun proveedor. Nativo USDC en Base, swap trustless a otras cadenas
    Privacidad: ZK proof del pago (hash, no datos personales)
    CUIDADO: enviar importe EXACTO, divisa correcta, no usar cuentas business
  → Luego aplicar rutas de BTC si necesita otra cadena

SI tiene BTC on-chain:
  SI quiere L-USDT (Liquid):
    *** RUTA PRINCIPAL (SIEMPRE): SideSwap peg-in (0.1%, adelanta L-BTC sin esperar 102 conf) → SideSwap Instant/Maker ***
    FALLBACK (SOLO si peg-in no disponible): Boltz chain swap BTC→L-BTC
    ⚠️ PROHIBIDO recomendar Boltz como ruta principal para BTC→Liquid. Boltz = solo SALIDA de Liquid (privacidad via Tor)
    ⚠️ NO presentar Boltz como "mas directa" o "mas economica" que SideSwap peg-in. SideSwap peg-in ES la ruta directa.

  SI quiere USDC/USDT en EVM:
    MEJOR COSTE + Arbitrum/ETH: Chainflip (sin wallet connect, fees bajos, sin minimo alto)
    MEJOR COSTE + Polygon: LendaSat gasless (sin wallet connect) — NOTA: fee real 1.2-2%, no 0.25%
    BOLTZ USDT (produccion): Boltz BTC→USDT directo via USDT0 (20+ cadenas: ETH/Arb/Poly/RSK/OP/SOL/Tron/Sei/Uni..., 25K-2M sats, 0.25%+slippage)
    MAXIMA LIQUIDEZ: THORSwap (CUIDADO: fee fijo BTC alto — ver seccion THORSwap)
    CANTIDAD < $100: Chainflip o LendaSat (THORSwap minimo 100k sats)

  SI quiere DOC/USDT en Rootstock:
    → Boltz → RBTC → Money on Chain (DOC) o Oku Trade (USDT)

SI tiene Lightning (LN):
  SI quiere L-USDT: Boltz LN→L-BTC → SideSwap
  SI quiere USDT EVM: Boltz LN→USDT directo (20+ cadenas, 0.25%+slip)
  SI quiere USDC EVM: LendaSat directo LN→USDC gasless

SI tiene L-BTC:
  → SideSwap Instant o Maker directo [consultar SideSwap orderbook — ver script inline abajo, o skill sideswap si esta instalado]

SI tiene L-USDT y quiere volver a BTC (VUELTA):
  → SideSwap (L-USDT → L-BTC) + Boltz chain swap (L-BTC → BTC, via Tor)
  IMPORTANTE: Usar Boltz (no peg-out SideSwap) por PRIVACIDAD — es atomic swap, no peg-out federacion
  Boltz via Tor/.onion = IP no expuesta, sin KYC, mas rapido que peg-out
  Fee vuelta: SideSwap 0.2%+spread + Boltz 0.1%+red = ~0.48-0.58%

SI tiene L-USDT y quiere USDT en EVM:
  → SideSwap (L-USDT → L-BTC) + Boltz (L-BTC → USDT EVM directo, 0.25%+slip)
  Fee total: ~0.65-0.85% (SideSwap ~0.40-0.55% + Boltz 0.25%+slip)

SI tiene USDT EVM y quiere volver a BTC:
  → Boltz (USDT → BTC, 0.25%+slip) — PRINCIPAL
  → Chainflip (USDT → BTC, ~0.2-0.3%) — alternativa
SI tiene USDC EVM y quiere volver a BTC:
  → Chainflip (USDC → BTC, ~0.2-0.3%) — PRINCIPAL

CIRCUITO COMPLETO LENDING (flujo principal de la mentoria):
  IDA:   BTC → SideSwap peg-in (0.1%) → L-BTC → SideSwap Instant/Maker → L-USDT → HodlHodl Lend
  VUELTA: L-USDT → SideSwap → L-BTC → Boltz chain swap (Tor) → BTC
  Coste ida+vuelta: ~0.7% (Instant) o ~0.3-0.4% (Maker)
  REGLA: Boltz NUNCA para entrar a Liquid. Solo para SALIR (privacidad via Tor)
```

### Paso 4: Presentar recomendacion con DESGLOSE DE FEES
Ejemplo de formato:

```
Ruta recomendada: BTC → SideSwap peg-in → L-BTC → SideSwap Instant → L-USDT

Para 500,000 sats (~$330):

Fee desglosado:
  1. Tx Bitcoin (envio peg-in):      ~141 sats (1 sat/vb × ~141 vbytes)
  2. SideSwap peg-in fee:            500 sats (0.1%)
  3. SideSwap spread (instant):      ~594 sats (0.18% spread actual)
  4. SideSwap taker fee:             ~997 sats (0.2%)
  ─────────────────────────────────────────────
  TOTAL estimado:                    ~2,232 sats (0.45%)

Tiempo: ~15 minutos (2 conf BTC + swap instantaneo)
Herramientas: Sparrow + SideSwap
Privacidad: Alta (Confidential Transactions en Liquid)
```

### Paso 5: Ofrecer alternativas
"Si prefieres [X], tambien puedes [ruta alternativa con su desglose]"

---

## SCRIPTS DE CONSULTA EN VIVO

### 1. FEE CALCULATOR — Script maestro
Ejecuta esto para obtener todos los datos necesarios de una vez:

```bash
echo "=== FEES EN VIVO ===" && echo "" && \
echo "--- Bitcoin mempool (rango proximo bloque) ---" && \
curl -sL "https://mempool.space/api/v1/fees/mempool-blocks" | python3 -c "
import sys,json
blocks=json.load(sys.stdin)
b=blocks[0]; fr=b.get('feeRange',[])
lo=fr[0] if fr else 0; hi=fr[-1] if fr else 0
print(f'  Proximo bloque: {lo:.2f}-{hi:.1f} sat/vb | {b[\"nTx\"]} txs | {b[\"blockVSize\"]/1e6:.2f} MvB')
if len(blocks)>1:
    b1=blocks[1]; fr1=b1.get('feeRange',[])
    print(f'  Bloque +1: {fr1[0]:.2f}-{fr1[-1]:.2f} sat/vb | {b1[\"nTx\"]} txs')
# Estimar coste tx BTC tipica (segwit ~141 vbytes, con OP_RETURN ~282 vbytes para THORSwap)
import math
normal = round(lo * 141)
opreturn = round(lo * 282)
print(f'  Min para entrar al bloque: {lo:.2f} sat/vb')
print(f'  Tx BTC peg-in (~141 vb): ~{normal} sats | con OP_RETURN (~282 vb): ~{opreturn} sats')
" 2>/dev/null && echo "" && \
echo "--- Liquid Network ---" && \
curl -sL "https://liquid.network/api/v1/fees/recommended" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  Fee Liquid: {d[\"fastestFee\"]} sat/vb (fijo ~0.1, tx ~150 vb = ~15 sats)')
" 2>/dev/null && echo "" && \
echo "--- Boltz fees ---" && \
curl -sL "https://api.boltz.exchange/v2/swap/submarine" | python3 -c "
import sys,json; d=json.load(sys.stdin)
for chain, pairs in d.items():
    for pair, info in pairs.items():
        f=info.get('fees',{}); l=info.get('limits',{})
        print(f'  Submarine {pair}→{chain}: {f.get(\"percentage\",\"?\")}% + {f.get(\"minerFees\",\"?\")} sats miner | min {l.get(\"minimal\",\"?\")} max {l.get(\"maximal\",\"?\")} sats')
" 2>/dev/null && \
curl -sL "https://api.boltz.exchange/v2/swap/reverse" | python3 -c "
import sys,json; d=json.load(sys.stdin)
for chain, pairs in d.items():
    for pair, info in pairs.items():
        f=info.get('fees',{}); l=info.get('limits',{})
        mf=f.get('minerFees',{}); claim=mf.get('claim','?') if isinstance(mf,dict) else mf
        print(f'  Reverse {chain}→{pair}: {f.get(\"percentage\",\"?\")}% + {claim} sats claim | min {l.get(\"minimal\",\"?\")} max {l.get(\"maximal\",\"?\")} sats')
" 2>/dev/null && echo "" && \
echo "--- THORChain (BTC outbound) ---" && \
curl -sL "https://thornode.ninerealms.com/thorchain/inbound_addresses" | python3 -c "
import sys,json
for c in json.load(sys.stdin):
    if c.get('chain')=='BTC':
        gr=int(c.get('gas_rate',0)); ts=int(c.get('outbound_tx_size',0)); of=int(c.get('outbound_fee',0))
        print(f'  gas_rate: {gr} sat/vb | outbound_tx_size: {ts} vb | outbound_fee: {of} sats')
        print(f'  ALERTA: outbound_tx_size={ts} vb esta MUY sobreestimado (real ~150-250 vb)')
        print(f'  El fee fijo de {of} sats se cobra SIEMPRE en swaps donde el OUTPUT es BTC')
        print(f'  Impacto: en \$50 = {of*100/75000:.1f}% | en \$500 = {of*100/750000:.1f}% | en \$5000 = {of*100/7500000:.2f}%')
" 2>/dev/null && echo "" && \
echo "--- Chainflip (500K sats BTC→USDC ETH) ---" && \
curl -sL "https://chainflip-swap.chainflip.io/v2/quote?amount=500000&srcChain=Bitcoin&srcAsset=BTC&destChain=Ethereum&destAsset=USDC" | python3 -c "
import sys,json
data=json.load(sys.stdin)
if not data: print('  Sin quotes'); sys.exit(0)
q=data[0]; out=int(q['egressAmount'])/1e6
fees={f['type']:int(f['amount']) for f in q.get('includedFees',[])}
net=fees.get('NETWORK',0)/1e6; eg=fees.get('EGRESS',0)/1e6; ig=fees.get('INGRESS',0)
print(f'  500K sats → {out:.2f} USDC | network {net:.2f} USDC | egress {eg:.4f} USDC | ingress {ig} sats')
print(f'  Liquidez baja: {q.get(\"lowLiquidityWarning\",False)} | ~{int(q.get(\"estimatedDurationSeconds\",0))/60:.0f} min')
" 2>/dev/null && echo "" && \
echo "--- Precio BTC (referencia) ---" && \
curl -sL "https://mempool.space/api/v1/prices" | python3 -c "
import sys,json; d=json.load(sys.stdin); print(f'  BTC/USD: \${d.get(\"USD\",0):,.0f}')
" 2>/dev/null
```

### 7. LendaSwap quote (BTC/LN → stablecoins EVM)
```bash
# Tokens: btc_lightning, btc_onchain, btc_arkade → usdc_pol, usdc_arb, usdc_eth, usdt_arb, usdt_eth, usdt0_pol
FROM="btc_lightning"
TO="usdc_pol"
AMOUNT_SATS=50000
curl -sL "https://apilendaswap.lendasat.com/quote?from=${FROM}&to=${TO}&base_amount=${AMOUNT_SATS}" | python3 -c "
import sys,json,urllib.request
q=json.load(sys.stdin)
rate=float(q['exchange_rate']); nf=q['network_fee']; pf=q['protocol_fee']; pr=q['protocol_fee_rate']
px=json.load(urllib.request.urlopen('https://mempool.space/api/v1/prices'))['USD']
fair=${AMOUNT_SATS}/1e8*px; got=${AMOUNT_SATS}/1e8*rate-nf-pf
spread=(1-rate/px)*100; total=(1-got/fair)*100
print(f'LendaSwap ${AMOUNT_SATS} sats ${FROM}→${TO}')
print(f'  Rate: {rate:.2f} (spread vs spot: {spread:+.2f}%)')
print(f'  Protocol fee: {pr*100:.2f}% = {pf}')
print(f'  Network fee: {nf}')
print(f'  Recibiras: ~{got:.2f} | Justo: \${fair:.2f}')
print(f'  Coste total: ~{total:.2f}%')
print(f'  Min: {q[\"min_amount\"]} sats | Max: {q[\"max_amount\"]} sats')
" 2>/dev/null
```

**API**: `GET https://apilendaswap.lendasat.com/quote?from=<token>&to=<token>&base_amount=<sats>`
**Tokens disponibles**: `GET https://apilendaswap.lendasat.com/tokens`
**Fee protocolo**: 0.25% fijo. El spread sobre spot varía (observado 0.2-2%). Coste total real = spread + 0.25% + network fee.

### HEALTH CHECK — Estado de todas las APIs
Ejecuta esto para verificar que todos los servicios estan operativos:

```bash
echo "=== HEALTH CHECK APIs ===" && echo ""
# Consultar todas las APIs en paralelo
check() { local name=$1 url=$2; code=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$url" 2>/dev/null); [ "$code" = "200" ] && echo "  OK  $name" || echo "  FAIL $name (HTTP $code)"; }
check "Mempool.space      " "https://mempool.space/api/v1/prices" &
check "Liquid Network     " "https://liquid.network/api/v1/fees/recommended" &
check "Boltz submarine    " "https://api.boltz.exchange/v2/swap/submarine" &
check "Boltz reverse      " "https://api.boltz.exchange/v2/swap/reverse" &
check "THORNode           " "https://thornode.ninerealms.com/thorchain/inbound_addresses" &
check "Chainflip backend  " "https://chainflip-swap.chainflip.io/v2/quote?amount=100000&srcChain=Bitcoin&srcAsset=BTC&destChain=Ethereum&destAsset=USDC" &
check "LendaSat           " "https://lendasat.com" &
check "LendaSwap API      " "https://apilendaswap.lendasat.com/tokens" &
wait
echo ""
echo "Nota: Si tienes los skills 'sideswap' y 'buy-on-peer' instalados, usalos para consultas avanzadas"
```

### 2. SideSwap orderbook (L-BTC/L-USDT)

Usa este script inline para obtener precio indice, spread y simulacion basica.
Para herramientas avanzadas (historico OHLCV, spread monitor, whales, alertas, peg, arbitraje, federation audit, activity): Usa `{baseDir}/sideswap_tools.py` con `/tmp/swvenv/bin/python {baseDir}/sideswap_tools.py <command>`
Para API reference y asset IDs: Lee `{baseDir}/references/sideswap-api-reference.md`
Para market maker setup: Lee `{baseDir}/references/sideswap-maker-guide.md`

```python
cat << 'SCRIPT' | timeout 15 /tmp/swvenv/bin/python - 2>&1
import json, asyncio, websockets

LBTC = "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d"
USDT = "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2"

# === CONFIGURE THESE ===
BUDGET = 20000.0        # Amount in quote asset (USDt)
DIRECTION = "buy"       # "buy" = buy BTC with USDt, "sell" = sell BTC for USDt
# =======================

async def main():
    async with websockets.connect("wss://api.sideswap.io/json-rpc-ws") as ws:
        await ws.send(json.dumps({"id":1,"method":"market","params":{"subscribe":{"asset_pair":{"base":LBTC,"quote":USDT}}}}))
        orders = {}
        ind_price = last_price = 0
        for _ in range(3):
            msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=8))
            if "result" in msg and "subscribe" in msg.get("result",{}):
                for o in msg["result"]["subscribe"]["orders"]:
                    orders[o["order_id"]] = o
            p = msg.get("params",{})
            if "market_price" in p:
                ind_price = p["market_price"].get("ind_price",0)
                last_price = p["market_price"].get("last_price",0)

        if DIRECTION == "buy":
            side = sorted([o for o in orders.values() if o["trade_dir"]=="Sell"], key=lambda x: x["price"])
        else:
            side = sorted([o for o in orders.values() if o["trade_dir"]=="Buy"], key=lambda x: -x["price"])

        print(f"Precio indice: ${ind_price:,.2f}  |  Ultimo: ${last_price:,.2f}")
        print(f"Direccion: {DIRECTION.upper()} BTC  |  Presupuesto: ${BUDGET:,.2f}")
        print(f"Ordenes en el lado relevante: {len(side)}")
        print()
        for i, o in enumerate(side[:10], 1):
            btc = o["amount"]/1e8; usdt = btc * o["price"]
            sp = ((o["price"]/ind_price)-1)*100 if ind_price else 0
            if DIRECTION == "sell": sp = -((ind_price/o["price"])-1)*100 if o["price"] else 0
            print(f"  #{i} @ ${o['price']:>12,.2f}  {btc:.8f} BTC  ${usdt:>10,.2f}  spread {sp:+.2f}%")

        remaining = BUDGET; total_btc = 0.0
        for o in side:
            if remaining <= 0: break
            btc = o["amount"]/1e8; cost = btc * o["price"]
            if cost <= remaining: total_btc += btc; remaining -= cost
            else: total_btc += remaining/o["price"]; remaining = 0
        spent = BUDGET - remaining
        avg = spent/total_btc if total_btc else 0
        fee = total_btc * 0.002; net = total_btc - fee
        eff = spent/net if net else 0
        print(f"\nSimulacion: ${spent:,.2f} → {net:.8f} BTC neto @ ${eff:,.2f} efectivo")
        print(f"  Spread: {((avg/ind_price)-1)*100:+.3f}% | Taker fee 0.2%: -{fee:.8f} BTC | Total: {((eff/ind_price)-1)*100:+.3f}%")

asyncio.run(main())
SCRIPT
```

Si `websockets` no esta instalado: `python3 -m venv /tmp/swvenv && /tmp/swvenv/bin/pip install -q websockets`

### 3. Peer.xyz rates (Fiat → Crypto)

Usa esta query inline al indexer de Peer para obtener rates y liquidez.
Para guia de compra paso a paso, tiers, caps, cooldowns: Lee `{baseDir}/references/peer-buying-guide.md`
Para guia de venta, deposits, ARM, vaults: Lee `{baseDir}/references/peer-selling-guide.md`
Para troubleshooting y errores: Lee `{baseDir}/references/peer-troubleshooting.md`
Para bridge fees (BTC/ETH/SOL): Lee `{baseDir}/references/peer-bridge-fees.md`
Para queries avanzadas al indexer: Lee `{baseDir}/references/peer-indexer-queries.md`

```bash
# Ajustar CURRENCY_HASH segun divisa (ver tabla abajo)
CURRENCY_HASH="0x"  # Sin filtro = todas las divisas
# Para EUR: reemplazar con hash de revolut/wise/n26
curl -sL -X POST "https://indexer.zkp2p.xyz/v1/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Deposit(limit: 20, where: {acceptingIntents: {_eq: true}, status: {_eq: \"ACTIVE\"}, remainingDeposits: {_gt: \"1000000\"}}, order_by: {remainingDeposits: desc}) { depositId remainingDeposits currencies { takerConversionRate spreadBps paymentMethodHash rateSource } } }"}' | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', {}).get('Deposit', [])
# Payment method hashes
PM = {
    '0x617f88ab': 'Revolut', '0x554a007c': 'Wise', '0x90262a3d': 'Venmo',
    '0x10940ee6': 'CashApp', '0x3ccc3d4d': 'PayPal'
}
print('Peer.xyz — Liquidez activa (Top 20 deposits)')
print(f'{\"Deposito\":>10}  {\"Rate\":>10}  {\"Spread\":>8}  {\"Metodo\":>10}  {\"Fuente\":>10}')
print('-' * 60)
for d in data:
    amt = int(d['remainingDeposits']) / 1e6
    for c in d.get('currencies', []):
        rate_raw = int(c.get('takerConversionRate', 0))
        if rate_raw == 0: continue
        rate = rate_raw / 1e18
        bps = c.get('spreadBps')
        spread = f'{int(bps)/100:.1f}%' if bps else '-'
        pmh = c.get('paymentMethodHash', '')[:10]
        pm = next((v for k,v in PM.items() if pmh.startswith(k)), pmh[:8])
        src = c.get('rateSource', '?')
        if src == 'NO_FLOOR': continue
        print(f'\${amt:>9,.2f}  {rate:>10.4f}  {spread:>8}  {pm:>10}  {src:>10}')
" 2>/dev/null
```

**Hashes de metodos de pago**:
| Metodo | Hash (primeros 10 chars) |
|---|---|
| Revolut | 0x617f88ab |
| Wise | 0x554a007c |
| Venmo | 0x90262a3d |
| CashApp | 0x10940ee6 |
| PayPal | 0x3ccc3d4d |

**Interpretar rates**: raw / 1e18. Ej: `1032500000000000000` = 1.0325 (fiat por 1 USDC). Deposits: raw / 1e6 (USDC 6 decimales).

### 4. THORChain swap quote (para cantidades especificas)
```bash
# Ajustar AMOUNT (en sats para BTC, en 1e8 para USDC) y ASSET
AMOUNT=500000
curl -sL "https://thornode.ninerealms.com/thorchain/quote/swap?amount=${AMOUNT}&from_asset=BTC.BTC&to_asset=ETH.USDC-0XA0B86991C6218B36C1D19D4A2E9EB0CE3606EB48&destination=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" | python3 -c "
import sys,json; d=json.load(sys.stdin)
fees=d.get('fees',{})
out=int(d.get('expected_amount_out',0))
outf=int(fees.get('outbound','0'))
liqf=int(fees.get('liquidity','0'))
totf=int(fees.get('total','0'))
bps=fees.get('total_bps',0)
print(f'THORChain {AMOUNT} sats BTC → USDC:')
print(f'  Recibiras: \${out/1e8:.2f} USDC')
print(f'  Fee outbound (ETH gas): \${outf/1e8:.2f}')
print(f'  Fee liquidez: \${liqf/1e8:.2f}')
print(f'  Fee total protocolo: \${totf/1e8:.2f} ({bps} bps)')
print(f'  + Fee tx BTC inbound (usuario paga aparte)')
print(f'  Min recomendado: {d.get(\"recommended_min_amount_in\",\"?\")} sats')
" 2>/dev/null
```

### 5. Chainflip swap quote (BTC ↔ USDC/USDT en vivo, con liquidez JIT)
```bash
# Ajustar AMOUNT_SATS y destino
AMOUNT_SATS=500000
# Destinos: Ethereum/Arbitrum/Solana × USDC/USDT (Arbitrum solo USDC)
DEST_CHAIN="Ethereum"
DEST_ASSET="USDC"
# Endpoint oficial del backend Chainflip (incluye liquidez JIT = rate real)
curl -sL "https://chainflip-swap.chainflip.io/v2/quote?amount=${AMOUNT_SATS}&srcChain=Bitcoin&srcAsset=BTC&destChain=${DEST_CHAIN}&destAsset=${DEST_ASSET}" | python3 -c "
import sys,json,urllib.request
data=json.load(sys.stdin)
if not data: print('Sin quotes disponibles'); sys.exit(1)
q=data[0]
out=int(q['egressAmount'])
dec=6 if '${DEST_ASSET}' in ('USDC','USDT') else 18
print(f'Chainflip ${AMOUNT_SATS} sats BTC → ${DEST_ASSET} (${DEST_CHAIN}):')
print(f'  Recibiras: {out/10**dec:.2f} ${DEST_ASSET}')
print(f'  Tipo: {q.get(\"type\",\"?\")}')
print(f'  Tiempo estimado: ~{int(q.get(\"estimatedDurationSeconds\",0))/60:.0f} min')
print(f'  Slippage recomendado: {q.get(\"recommendedSlippageTolerancePercent\",\"?\")}%')
if q.get('lowLiquidityWarning'): print(f'  ⚠ ALERTA: baja liquidez')
print(f'  Fees incluidos:')
for f in q.get('includedFees',[]):
    a=f['asset']; amt=int(f['amount'])
    d2=6 if a in ('USDC','USDT') else 8 if a=='BTC' else 18
    unit='sats' if a=='BTC' else a
    val=amt if a=='BTC' else f'{amt/10**d2:.4f}'
    print(f'    {f[\"type\"]:12s}: {val} {unit}')
try:
    px=json.load(urllib.request.urlopen('https://mempool.space/api/v1/prices'))['USD']
    fair=(${AMOUNT_SATS}/1e8)*px
    cost_pct=(1-out/10**dec/fair)*100
    print(f'  Precio BTC ref: \${px:,.0f} | Valor justo: \${fair:.2f} | Coste total: {cost_pct:.2f}%')
except: pass
" 2>/dev/null
```

Para **quote reverso** (USDC/USDT → BTC):
```bash
# USDC → BTC (vuelta). AMOUNT en unidades minimas (6 decimales para USDC/USDT)
AMOUNT_USDC=500
AMOUNT_RAW=$((AMOUNT_USDC * 1000000))
SRC_CHAIN="Ethereum"  # o Arbitrum, Solana
SRC_ASSET="USDC"      # o USDT
curl -sL "https://chainflip-swap.chainflip.io/v2/quote?amount=${AMOUNT_RAW}&srcChain=${SRC_CHAIN}&srcAsset=${SRC_ASSET}&destChain=Bitcoin&destAsset=BTC" | python3 -c "
import sys,json,urllib.request
data=json.load(sys.stdin)
q=data[0]
out=int(q['egressAmount'])
print(f'Chainflip ${AMOUNT_USDC} ${SRC_ASSET} → BTC:')
print(f'  Recibiras: {out} sats ({out/1e8:.6f} BTC)')
print(f'  Tiempo: ~{int(q.get(\"estimatedDurationSeconds\",0))/60:.0f} min')
for f in q.get('includedFees',[]):
    a=f['asset']; amt=int(f['amount'])
    d2=6 if a in ('USDC','USDT') else 8
    unit='sats' if a=='BTC' else a
    val=amt if a=='BTC' else f'{amt/10**d2:.4f}'
    print(f'  {f[\"type\"]:12s}: {val} {unit}')
try:
    px=json.load(urllib.request.urlopen('https://mempool.space/api/v1/prices'))['USD']
    fair=${AMOUNT_USDC}/px*1e8
    cost_pct=(1-out/fair)*100
    print(f'  Precio BTC ref: \${px:,.0f} | Sats justos: {fair:.0f} | Coste total: {cost_pct:.2f}%')
except: pass
" 2>/dev/null
```

**Cadenas y assets soportados** (BTC como origen):
| Cadena | USDC | USDT | ETH | Otros |
|---|---|---|---|---|
| Ethereum | ✓ | ✓ | ✗¹ | FLIP, WBTC |
| Arbitrum | ✓ | ✗ | ✓ | — |
| Solana | ✓ | ✓ | — | SOL |

¹ ETH en Ethereum falla por liquidez insuficiente en el pool directo. Usar Arbitrum para ETH.

### 6. Boltz BTC → USDT quote (en vivo)
```bash
# Ajustar AMOUNT_SATS
AMOUNT_SATS=500000
python3 -c "
import json, urllib.request
amount_sats = ${AMOUNT_SATS}
px = json.load(urllib.request.urlopen('https://mempool.space/api/v1/prices'))['USD']
fair_usd = amount_sats / 1e8 * px
boltz_fee_sats = int(amount_sats * 0.25 / 100)
chain_pairs = json.load(urllib.request.urlopen('https://api.boltz.exchange/v2/swap/chain'))
ref = chain_pairs.get('RBTC', {}).get('BTC', {})
server_miner = ref.get('fees', {}).get('minerFees', {}).get('server', 600)
after_fees = amount_sats - boltz_fee_sats - server_miner
tbtc_wei = after_fees * 10**10
url = f'https://api.boltz.exchange/v2/quote/ARB/in?tokenIn=0x6c84a8f1c29108F47a79964b5Fe888D4f4D0dE40&tokenOut=0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9&amountIn={tbtc_wei}'
dex = json.load(urllib.request.urlopen(url))
usdt_out = int(dex[0]['quote']) / 1e6
total_cost_pct = (1 - usdt_out / fair_usd) * 100
print(f'Boltz BTC → USDT (Arbitrum) — {amount_sats:,} sats')
print(f'  Fee servicio Boltz: 0.25% = {boltz_fee_sats} sats')
print(f'  Miner fee (server): {server_miner} sats')
print(f'  Recibiras: ~{usdt_out:.2f} USDT')
print(f'  BTC ref: \${px:,.0f} | Valor justo: \${fair_usd:.2f}')
print(f'  Coste total efectivo: ~{total_cost_pct:.2f}%')
print(f'  + Fee tx BTC on-chain (usuario paga aparte)')
" 2>/dev/null
```

**Flujo interno**: BTC →[chain swap]→ TBTC (Arbitrum) →[Uniswap V3: TBTC→WBTC→USDT]→ USDT (Arbitrum) →[USDT0/OFT]→ USDT (cadena destino). El usuario solo ve: enviar BTC → recibir USDT.

**Coste total real**: 0.25% fee Boltz + hasta 1% slippage DEX (configurable en settings de la webapp) + miner fees. Peor caso ~1.3%, caso típico ~0.3-0.5%.

**API endpoints**:
- Chain swap creation: `POST /v2/swap/chain` con `from: "BTC", to: "TBTC"` (par oculto, no listado en GET)
- DEX quote: `GET /v2/quote/ARB/in?tokenIn=<addr>&tokenOut=<addr>&amountIn=<wei>`
- DEX quote reverso: `GET /v2/quote/ARB/out?tokenIn=<addr>&tokenOut=<addr>&amountOut=<wei>`
- Contratos y tokens: `GET /v2/chain/contracts` (muestra TBTC address en Arbitrum)

---

## THORSWAP — ALERTA DE FEE FIJO BTC

### El problema
THORChain usa `outbound_tx_size: 1000 vbytes` para calcular el fee de la tx BTC de salida. Una tx BTC real es ~150-250 vbytes, asi que **sobreestima 4-7x**.

### Fee BTC outbound (FIJO, independiente del monto)
| Mempool BTC | outbound_fee | En $50 swap | En $500 swap | En $5000 swap |
|---|---|---|---|---|
| 3 sat/vb (bajo) | ~1,300 sats | ~1.7% | ~0.17% | ~0.02% |
| 10 sat/vb (tipico) | ~4,300 sats | ~5.7% | ~0.57% | ~0.06% |
| 30 sat/vb (moderado) | ~12,800 sats | ~17% | ~1.7% | ~0.17% |
| 50 sat/vb (congestionado) | ~21,400 sats | ~28% | ~2.8% | ~0.28% |

### Cuando este fee aplica
- **BTC→USDC (ida)**: El frontend AÑADE ~10,000-11,000 sats al monto que introduces como "inbound network fee". Esto cubre la tx BTC (3 outputs: pago + cambio + OP_RETURN). Confirmado en video de la mentoria: "no es el millon que hemos puesto sino que se agregan 10,000 sats mas". Es FIJO independiente del monto.
- **USDC→BTC (vuelta)**: Ademas, el outbound BTC fee (1000 vb × gas_rate) se descuenta del output.
- Formula: `outbound_tx_size (1000 vb) × gas_rate`. A 10 sat/vb = 10,000 sats. A 3 sat/vb (ahora) = 3,000 sats.

### Conclusion
- **THORSwap es caro para cantidades pequenas** y cuando el mempool BTC esta activo
- Para < $500: preferir **Chainflip** (sin este overhead) o **LendaSat** (gasless)
- THORSwap solo merece la pena para **cantidades grandes (>$1,000)** con mempool bajo
- THORSwap tiene MAS LIQUIDEZ que Chainflip, pero el coste fijo lo penaliza

---

## SERVICIOS SIN WALLET CONNECT (solo pegar direccion + enviar BTC)

Estos servicios **no requieren conectar wallet** — el flujo es: pegar direccion destino → recibir direccion BTC temporal → enviar BTC desde cualquier wallet → recibir stablecoin:

| Servicio | Wallet connect? | Flujo |
|---|---|---|
| **Boltz** | NO | Pegar direccion L-BTC/RBTC/USDT(20+ cadenas) → enviar BTC → recibir |
| **Chainflip** | NO | Pegar direccion EVM → enviar BTC → recibir |
| **Unstoppable Money** | App propia | Wallet app con swap integrado. Usa THORChain/1inch/Uniswap internamente. Sin API publica |
| **LendaSat** | NO | Pegar direccion EVM → enviar BTC/LN → recibir |
| **Peer.xyz** | SI (wallet EVM) | Conectar wallet → pagar fiat → recibir |
| **THORSwap** | OPCIONAL | Puedes pegar direccion manualmente (modo externo) |
| **SideSwap** | App propia | Opera dentro de la app SideSwap |

---

## CUADROS DE RUTAS POR ESCENARIO

### BTC → L-USDT (Liquid)

| | Ruta | Fee total | Desglose | Tiempo |
|---|---|---|---|---|
| **Principal** | SideSwap peg-in → Instant | ~0.38-0.48% | Peg-in 0.1% + Taker 0.2% + spread | ~15 min |
| Fallback | Boltz → L-BTC → SideSwap Instant | ~0.48-0.58% | Boltz 0.1% + Taker 0.2% + spread | ~5 min |

### Fiat → USDC/USDT

| | Ruta | Fee | Metodos pago | Limite | Cadena |
|---|---|---|---|---|---|
| **Principal** | Peer.xyz | 0-1.5% | Wise, N26, Revolut | $500 inicial | USDC en Base |

### BTC → USDT/USDC en EVM

| | Ruta | Fee | Cadenas | Minimo | Token |
|---|---|---|---|---|---|
| **Principal** | Chainflip | ~0.2-0.3% | ETH, Arb, SOL | 40k sats | **USDC** |
| **Principal** | Boltz directo (USDT0) | ~0.25%+slip | 20+ cadenas | 25k sats | **USDT** |
| Secundaria | Unstoppable Money | Variable | Multi-cadena | Bajo | USDC y USDT |
| Secundaria | THORSwap | ~0.3% + fee fijo BTC | ETH, Arb, Poly | 100k sats | USDC y USDT |
| Secundaria | LendaSat | ~1.2-2% real | ETH, Arb, Poly | ~$5 | USDC (gasless) |

### L-USDT → USDT en ETH/EVM

| | Ruta | Fee | Tiempo |
|---|---|---|---|
| **Principal** | SideSwap (L-USDT→L-BTC) → Boltz (L-BTC→USDT EVM) | ~0.65-0.85% | Minutos |

### USDC ↔ USDT y viceversa (sin pasar por BTC)

| | Metodo | Fee | Nota |
|---|---|---|---|
| **Principal** | Chainflip | ~0.2-0.3% | USDC↔USDT, puede cambiar de cadena tambien |
| Secundaria | THORSwap | ~0.3% | Mas liquidez |

### USDT entre cadenas EVM

| | Metodo | Fee | Tiempo |
|---|---|---|---|
| **Principal** | usdt0.to | Solo gas ($0.14-0.69) | ~3.5 min |
| Secundaria | Bridges nativos o Chainflip | Gas o ~0.15% | Variable |

### Vuelta: L-USDT → BTC

| | Ruta | Fee total | Tiempo |
|---|---|---|---|
| **Principal** | L-USDT → SideSwap (→L-BTC) → Boltz Tor (→BTC) | ~0.48-0.58% | Minutos |

### Vuelta: USDT EVM → BTC

| | Ruta | Fee | Tiempo |
|---|---|---|---|
| **Principal** | USDT → Boltz (→BTC) | ~0.25%+slip | Minutos |
| Secundaria | USDT → Chainflip → BTC | ~0.2-0.3% | ~15 min |
| Secundaria | USDT → THORSwap → BTC | ~0.3% + fee fijo BTC | ~15 min |

### Vuelta: USDC EVM → BTC

| | Ruta | Fee | Tiempo |
|---|---|---|---|
| **Principal** | USDC → Chainflip → BTC | ~0.2-0.3% | ~15 min |
| Secundaria | USDC → THORSwap → BTC | ~0.3% + fee fijo BTC | ~15 min |

### Lightning → stablecoins

| | Ruta | Fee | Cadena destino |
|---|---|---|---|
| **Principal** | LN → Boltz → L-BTC → SideSwap → L-USDT | ~0.45-0.55% | Liquid |
| **Principal** | LN → Boltz directo → USDT EVM | ~0.25%+slip | 20+ cadenas EVM |
| Secundaria | LN → LendaSat | ~1.2-2% | Poly/Arb/ETH (USDC, gasless) |

### Gas para EVM

| | Ruta | Fee | Cadenas | Nota |
|---|---|---|---|---|
| **Principal** | BTC → Chainflip → ETH | ~0.2-0.3% | ETH, Arb | Min 40k sats |
| Secundaria | BTC → Unstoppable Money → ETH/POL/etc | Variable | Multi-cadena | Sin minimo, ideal para cantidades tiny |
| Secundaria | Fiat → Peer.xyz → ETH via bridge | ~0.5%+bridge | ETH | Si solo tienes fiat |
| Nota | Liquid: SideSwap deduce fees de L-USDT | — | Liquid | No necesitas L-BTC para gas |

---

## MAPA ESQUEMATICO DE RUTAS

```
ENTRADA → STABLECOIN

BTC ──┬── SideSwap peg-in → Instant ─────→ L-USDT          ~0.38-0.48%
      ├── Chainflip ──────────────────────→ USDC EVM        ~0.2-0.3%
      ├── Boltz directo ──────────────────→ USDT EVM (20+)  ~0.25%+slip
      ├── Unstoppable Money ──────────────→ USDC/USDT EVM   variable
      ├── THORSwap ───────────────────────→ USDC/USDT EVM   ~0.3%+fijo
      └── LendaSat ───────────────────────→ USDC EVM        ~1.2-2%

LN ───┬── Boltz → SideSwap ──────────────→ L-USDT           ~0.45-0.55%
      ├── Boltz directo ──────────────────→ USDT EVM         ~0.25%+slip
      └── LendaSat ───────────────────────→ USDC EVM         ~1.2-2%

FIAT ──── Peer.xyz ───────────────────────→ USDC Base        0-1.5%


MOVER ENTRE STABLES

L-USDT ── SideSwap → Boltz ──────────────→ USDT EVM         ~0.65-0.85%
USDT ──── usdt0.to ───────────────────────→ USDT otra EVM   $0.14-0.69
USDC ↔ USDT ── Chainflip ────────────────→ swap directo     ~0.2-0.3%


GAS PARA EVM

BTC ──┬── Chainflip ──────────────────────→ ETH (ETH/Arb)   ~0.2-0.3%
      └── Unstoppable Money ──────────────→ ETH/POL/etc     variable, sin minimo
FIAT ──── Peer.xyz ───────────────────────→ ETH via bridge   ~0.5%+bridge
Liquid ── SideSwap deduce fees de L-USDT ─→ no necesitas L-BTC para gas


VUELTA → BTC

L-USDT ── SideSwap → Boltz Tor ──────────→ BTC              ~0.48-0.58%
USDT EVM ── Boltz ────────────────────────→ BTC              ~0.25%+slip
USDC EVM ── Chainflip ───────────────────→ BTC              ~0.2-0.3%
```

## HERRAMIENTAS NECESARIAS POR RUTA

| Herramienta | Rutas | Notas |
|---|---|---|
| SideSwap (desktop/movil) | 1, 2, 3 | Swap L-BTC/L-USDT. Rates via script inline + `sideswap_tools.py` |
| Boltz.exchange | 1, 2, 3, 7 | BTC/LN ↔ L-BTC o RBTC. Sin registro |
| LendaSat.com | 4 | BTC/LN → USDC gasless. Sin registro |
| Chainflip (swap.chainflip.io) | 5, 9 | BTC → EVM directo. Sin registro |
| THORSwap (app.thorswap.finance) | 6 | BTC → EVM. CUIDADO fee fijo BTC |
| Peer.xyz | 8 | Fiat → crypto. Rates via script inline + references peer-* |
| Rabby Wallet | 5, 6, 9 | Wallet EVM con soporte HW (Trezor/Ledger/Keystone/BitBox) |
| Sparrow Wallet | Todas con BTC | Enviar BTC on-chain |
| Hardware wallet | Recomendado >$500 | Jade, Trezor, Ledger, etc |

## GAS EN EVM

| Cadena | Gas nativo | Coste/tx | Como obtener sin wallet connect |
|---|---|---|---|
| Ethereum | ETH | $1-5 | Chainflip BTC→ETH |
| Arbitrum | ETH | $0.01-0.10 | Chainflip BTC→ETH (Arb) |
| Polygon | MATIC/POL | ~$0.001 | LendaSat incluye gas, Rabby bridge ETH→POL (~$5) |
| Liquid | L-BTC | ~15 sats | SideSwap puede deducir fees de L-USDT (no necesitas L-BTC) |
| Alternativas | - | - | gas.zip, Rabby GasAccount |

## ADVERTENCIAS

1. **Verificar direccion** antes de enviar. Copiar-pegar y comparar.
2. **Importe exacto** en THORSwap/Chainflip — si no coincide, refund automatico.
3. **Slippage**: 1% en THORSwap. Chainflip usa JIT AMM automatico.
4. **Privacidad**: L-USDT en Liquid = confidencial. EVM = transparente + direccion reutilizada.
5. **Censura**: >$3,100M USDT congelados en EVM. L-USDT en Liquid sin congelaciones historicas.
6. **Nunca enviar a contratos inteligentes** — solo a wallets propias.
7. **THORSwap fee fijo**: El outbound BTC fee es significativo para cantidades pequenas o mempool alto.
8. **USDT0 cross-chain**: Para mover USDT entre cadenas EVM usa usdt0.to — solo USDT (no USDC), costo ~$0.14-0.69 segun direccion, ~3.5 min. USDC requiere bridges.
9. **LendaSat fee real**: El fee anunciado es 0.25% pero el coste real es 1.2-2% por spread de makers. THORSwap/Chainflip son mas baratos.
10. **Regulacion MiCA**: Tether (USDT) salio del mercado europeo por MiCA. Creo token USD para EEUU. La regulacion puede afectar stablecoins en cualquier momento.
11. **Boltz USDT directo (produccion desde marzo 2026)**: Boltz soporta BTC→USDT directo via USDT0 (LayerZero OFT). 20+ cadenas destino: Ethereum, Arbitrum, Polygon, Optimism, Rootstock, Solana, Tron, Berachain, Sei, Unichain, Ink, Mantle, y mas. Limites: 25K-2M sats. API usa endpoints `/v2/quote/{currency}/in|out` con params `tokenIn`, `tokenOut`, `amountIn`. La web app normaliza "USDT0" como "USDT" en la UI.

---

## DEPENDENCIAS

Esta skill es **100% autonoma** — incluye todas las references, scripts y herramientas de SideSwap y Peer.xyz. No necesita skills adicionales.

**Requisito**: Python 3 con `websockets` para consultar SideSwap orderbook en vivo.
Setup: `python3 -m venv /tmp/swvenv && /tmp/swvenv/bin/pip install -q websockets`
