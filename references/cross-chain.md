# Cross-chain y Bridges — Stablecoin Expert

## Escenario: Ya tengo stablecoins, necesito moverlas a otra cadena

---

## 1. Liquid → EVM (L-USDT → USDT en Ethereum/Polygon/Arbitrum)

### Ruta Principal: SideSwap → Boltz (L-BTC → USDT EVM)
- **IMPORTANTE:** Boltz solo maneja L-BTC en Liquid, nunca L-USDT. Se necesita SideSwap primero.
1. SideSwap: L-USDT → L-BTC (taker 0.2% + spread ~0.15-0.35%)
2. Boltz: L-BTC → USDT EVM directo via USDT0 (0.25% + slippage, 20+ cadenas)
- **Fee total:** ~0.65-0.85%
- **Tiempo:** Minutos

### Ruta Secundaria: Swap a BTC y reconvertir
1. SideSwap: L-USDT → L-BTC
2. Boltz: L-BTC → BTC
3. Chainflip/THORSwap: BTC → USDC en cadena destino
- **Desventaja:** Triple swap = mas fees (~0.8-1.1% total)

---

## 2. EVM → Liquid (USDC/USDT en EVM → L-USDT)

### Ruta: Swap a BTC y entrar a Liquid
1. THORSwap/Chainflip: USDC → BTC
2. Boltz: BTC → L-BTC
3. SideSwap: L-BTC → L-USDT
- **Coste total:** ~0.5-0.8%
- **Tiempo:** ~20-30 min

---

## 3. Entre cadenas EVM (Polygon → Arbitrum, etc.)

### Opcion A: usdt0.to (RECOMENDADO para USDT)
- **URL:** https://usdt0.to
- **Como funciona:** Mueve USDT entre cadenas EVM directamente, trustless, sin bridge tradicional. Creado por Tether para mover tokens USDT entre cadenas de forma nativa
- **Cadenas:** Ethereum, Polygon, Arbitrum, Optimism, Base, BNB Chain, Avalanche, etc.
- **Solo USDT:** NO funciona con USDC (para USDC usar bridges o Chainflip)
- **Fee:** Solo gas en cadena origen:
  - Ethereum → Polygon: ~$0.14
  - Polygon → Ethereum: ~$0.69 (mas caro en direccion a Ethereum)
- **Tiempo:** ~3.5 minutos
- **Proceso:** Conectar wallet (Rabby) → seleccionar origen/destino → aprobar (1 firma) → transferir (1 firma)
- **Gas necesario:** En ambas cadenas (origen para enviar, destino para recibir). Si no tienes gas en destino, primero hacer bridge de ETH/POL via Rabby (~$5)
- **Nota:** Boltz tambien usa USDT0 para su nueva ruta BTC→USDT directo en EVM

### Opcion B: Bridge nativo (Arbitrum Bridge, Polygon Bridge)
- **Fee:** Solo gas
- **Tiempo:** Variable (Arbitrum → Ethereum puede tardar 7 dias por periodo de disputa)
- **Nota:** De Ethereum a L2 es rapido (~10 min), de L2 a Ethereum es lento

### Opcion C: Chainflip
- Swap USDC en una cadena → USDC en otra
- Util si necesitas cambiar de Ethereum a Arbitrum por ejemplo
- Fee del protocolo aplica

---

## 4. EVM → Bitcoin (vuelta a BTC)

### Via THORSwap (recomendado para cantidades > $100)
1. Conectar Rabby en THORSwap
2. Seleccionar USDC/USDT → BTC
3. Aprobar (primera firma)
4. Swap (segunda firma — pegar direccion BTC de Sparrow)
5. Esperar ~15 min
- **Fee:** ~0.3-0.5%

### Via Chainflip
1. Ir a swap.chainflip.io
2. Seleccionar USDC/USDT (cadena origen) → Bitcoin
3. Conectar wallet EVM o proporcionar direccion
4. Pegar direccion BTC de Sparrow
5. Aprobar y confirmar
- **Fee:** ~0.2-0.3%

---

## 5. Gas management

### Problema comun: Tengo stablecoins pero no tengo gas para moverlas

| Cadena | Gas nativo | Como obtener |
|---|---|---|
| Ethereum | ETH | Chainflip BTC→ETH, THORSwap BTC→ETH, Unstoppable Money |
| Arbitrum | ETH | Chainflip BTC→ETH (Arbitrum), bridge desde Ethereum |
| Polygon | MATIC/POL | LendaSat incluye gas, o gas.zip |
| Rootstock | RBTC | Boltz BTC→RBTC |
| Liquid | L-BTC | Boltz BTC→L-BTC, SideSwap peg-in |

### Soluciones universales
- **gas.zip** — Envia BTC/ETH y recibe gas en cualquier cadena EVM
- **Rabby GasAccount** — Deposita ETH una vez, paga gas en cualquier cadena desde ese saldo

### Consejo
- Al hacer el primer swap a una cadena EVM, obtener primero un poco de ETH (~$30-50) para gas
- En Polygon/Arbitrum el gas es tan barato que $5 en gas duran meses
- Guardar el ETH residual para futuras transacciones

---

## Tabla resumen de bridges

| Origen | Destino | Metodo | Coste | Tiempo |
|---|---|---|---|---|
| L-USDT | USDT EVM | SideSwap→Boltz (L-BTC→USDT0) | ~0.65-0.85% | Min |
| USDT ETH | USDT Polygon | usdt0.to | ~$0.14 gas | ~3.5 min |
| USDT Polygon | USDT ETH | usdt0.to | ~$0.69 gas | ~3.5 min |
| USDT Polygon | USDT Arbitrum | usdt0.to | Solo gas | ~3.5 min |
| USDC ETH | USDC Arbitrum | Bridge Arbitrum | Solo gas | ~10 min |
| USDC Arbitrum | USDC ETH | Bridge Arbitrum | Solo gas | ~7 dias |
| USDC cualquier | BTC | THORSwap/Chainflip | 0.15-0.5% | ~15 min |
| BTC | USDT EVM | Boltz directo (USDT0) | 0.25%+slip | Min |
| BTC | L-BTC | Boltz | ~0.1% | Min |
| L-BTC | BTC | SideSwap peg-out | 0% (solo miner fee) | ~2 conf |
| ETH | POL (gas) | Rabby bridge | ~$0.50 fee | Min |
