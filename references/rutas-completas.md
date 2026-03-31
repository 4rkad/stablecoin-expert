# Mapa completo de rutas — Stablecoin Expert

## Cuadros de rutas por escenario

### BTC → L-USDT (Liquid)

| | Ruta | Fee total | Desglose | Tiempo |
|---|---|---|---|---|
| **Principal** | SideSwap peg-in → Instant | ~0.38-0.48% | Peg-in 0.1% + Taker 0.2% + spread | Minutos |
| Secundaria | Boltz → L-BTC → SideSwap Instant | ~0.48-0.58% | Boltz 0.1% + Taker 0.2% + spread | Minutos |

**Notas:**
- SideSwap peg-in adelanta L-BTC sin esperar 102 conf
- Boltz solo maneja L-BTC en Liquid, nunca L-USDT. SideSwap es el unico que hace swap L-BTC ↔ L-USDT
- Taker paga 0.2% + spread. Maker no paga fee pero requiere esperar (no contemplado por rapidez)

### Fiat → USDC/USDT

| | Ruta | Fee | Metodos pago | Limite | Cadena |
|---|---|---|---|---|---|
| **Principal** | Peer.xyz | 0-1.5% | Wise, N26, Revolut | $500 inicial | USDC en Base |

**Notas:**
- Sin KYC: ZK proof del pago (hash, no datos personales)
- Limite sube a $2000+ con trades exitosos
- PayPal solo para ranking alto
- Enviar importe EXACTO, divisa correcta, no cuentas business

### BTC → USDT/USDC en EVM

| | Ruta | Fee | Cadenas | Minimo | Token |
|---|---|---|---|---|---|
| **Principal** | Chainflip | ~0.2-0.3% | ETH, Arb, SOL | 40k sats | **USDC** |
| **Principal** | Boltz directo (USDT0) | ~0.25%+1% slip max | 20+ cadenas | 25k sats | **USDT** |
| Secundaria | THORSwap | ~0.3% + fee fijo BTC | ETH, Arb, Poly | 100k sats | USDC y USDT |
| Secundaria | LendaSat | ~1.2-2% real | ETH, Arb, Poly | ~$5 | USDC (gasless) |

**Notas:**
- Chainflip: principal para USDC. Sin wallet connect, JIT AMM automatico
- Boltz: principal para USDT. Sin wallet connect, 20+ cadenas via USDT0 (LayerZero OFT). Slippage DEX configurable en settings (default 1%)
- THORSwap: fee fijo BTC sobreestimado (outbound_tx_size=1000vb), caro para cantidades pequenas
- LendaSat: fee real 1.2-2% (no 0.25% anunciado), util para gasless y cantidades tiny

### L-USDT → USDT en ETH/EVM

| | Ruta | Fee | Tiempo |
|---|---|---|---|
| **Principal** | SideSwap (L-USDT→L-BTC) → Boltz (L-BTC→USDT EVM) | ~0.65-0.85% | Minutos |

**Notas:**
- SideSwap convierte L-USDT a L-BTC (taker 0.2% + spread ~0.15-0.35% = ~0.40-0.55%)
- Boltz convierte L-BTC a USDT en 20+ cadenas EVM directo via USDT0 (0.25%+slip)
- Boltz solo maneja L-BTC en Liquid, nunca L-USDT — por eso se necesita SideSwap primero

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

**Notas:**
- usdt0.to: nativo de Tether, trustless, solo USDT (no USDC)
- Para USDC entre cadenas: bridges nativos (Arbitrum Bridge, etc.) o Chainflip

### Vuelta: L-USDT → BTC

| | Ruta | Fee total | Tiempo |
|---|---|---|---|
| **Principal** | L-USDT → SideSwap (→L-BTC) → Boltz Tor (→BTC) | ~0.48-0.58% | Minutos |

**Notas:**
- Usar Boltz via Tor por privacidad (atomic swap, IP no expuesta)
- NUNCA peg-out SideSwap para salir — Boltz es mas rapido y privado

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
| **Principal** | LN → Boltz (0.25% + routing LN) → L-BTC → SideSwap (taker 0.2% + spread) → L-USDT | ~0.45-0.75% | Liquid |
| **Principal** | LN → Boltz directo → USDT EVM | ~0.25%+1% slip max | 20+ cadenas EVM |
| Secundaria | LN → LendaSat | ~1.2-2% | Poly/Arb/ETH (USDC, gasless) |

**Desglose LN → L-USDT**:
1. LN → L-BTC (Boltz submarine): 0.25% + routing fees Lightning (variables, ~1-10 sats)
2. L-BTC → L-USDT (SideSwap swap): taker fee 0.2% + spread orderbook (~0.15-0.35%)

---

## Detalle de pasos por ruta

### Ruta: SideSwap peg-in → Instant (BTC → L-USDT)
1. En SideSwap, generar direccion de peg-in
2. Enviar BTC desde Sparrow a esa direccion
3. SideSwap adelanta L-BTC
4. Hacer Instant Swap L-BTC → L-USDT

### Ruta: Boltz → SideSwap (BTC → L-USDT)
1. Ir a boltz.exchange, seleccionar BTC → L-BTC
2. Enviar BTC desde Sparrow a la direccion de Boltz
3. Recibir L-BTC en SideSwap
4. En SideSwap, hacer Instant Swap L-BTC → L-USDT

### Ruta: Chainflip (BTC → USDC)
1. Ir a swap.chainflip.io
2. Seleccionar Bitcoin → USDC en Ethereum o Arbitrum
3. Pegar direccion EVM de destino
4. Se genera direccion BTC temporal
5. Enviar BTC desde Sparrow a esa direccion
6. Esperar ~15 min → recibir USDC

### Ruta: Boltz directo (BTC → USDT EVM)
1. Ir a boltz.exchange, seleccionar BTC → USDT → elegir cadena destino
2. Pegar direccion destino (EVM, Solana o Tron segun cadena)
3. Crear swap, guardar archivo de backup
4. Enviar BTC a la direccion proporcionada
5. Recibir USDT directamente en cadena destino

### Ruta: Peer.xyz (Fiat → USDC)
1. Ir a peer.xyz, login con email
2. Seleccionar divisa fiat y metodo de pago
3. Pegar direccion EVM (Rabby)
4. Iniciar orden — se genera QR del vendedor
5. Pagar importe EXACTO desde app bancaria
6. Instalar extension navegador (genera ZK proof)
7. Login en extension → prueba automatica → recibir USDC

### Ruta: LendaSat (BTC/LN → USDC gasless)
1. Ir a lendasat.com (servicio "LendaSwap")
2. Seleccionar BTC/LN → USDC/USDT (Polygon/Arbitrum/ETH)
3. Pegar direccion EVM
4. Descargar seed phrase del trade (recuperacion)
5. Enviar BTC/LN a la direccion proporcionada
6. Recibir stablecoin directamente — sin necesidad de gas

### Ruta: THORSwap (BTC → USDC/USDT)
1. Ir a app.thorswap.finance
2. Seleccionar BTC → USDC (cadena deseada)
3. Conectar wallet EVM o pegar direccion
4. Configurar slippage a 1%
5. Confirmar swap, copiar direccion BTC destino
6. Enviar importe EXACTO desde Sparrow
7. Esperar ~15 min → recibir stablecoin

### Ruta: Vuelta L-USDT → BTC
1. SideSwap: L-USDT → L-BTC (Instant swap)
2. Boltz via Tor: L-BTC → BTC (atomic swap, privado)

### Ruta: Vuelta USDT EVM → BTC (Boltz)
1. Ir a boltz.exchange via Tor
2. Seleccionar USDT → BTC
3. Pegar direccion BTC destino
4. Aprobar USDT y confirmar
5. Recibir BTC

### Ruta: Vuelta USDC EVM → BTC (Chainflip)
1. Ir a swap.chainflip.io
2. Seleccionar USDC → Bitcoin
3. Pegar direccion BTC de Sparrow
4. Aprobar y confirmar
5. Esperar ~15 min → recibir BTC

---

## Herramientas necesarias

| Herramienta | Uso | Notas |
|---|---|---|
| SideSwap (desktop/movil) | L-BTC ↔ L-USDT | Rates via script inline + sideswap_tools.py |
| Boltz.exchange | BTC/LN/L-BTC → L-BTC, BTC, USDT EVM | Sin registro. Usar via Tor para salida |
| Chainflip (swap.chainflip.io) | BTC ↔ USDC/USDT EVM, USDC↔USDT | Sin registro |
| THORSwap (app.thorswap.finance) | BTC ↔ USDC/USDT EVM | CUIDADO fee fijo BTC |
| LendaSat.com | BTC/LN → USDC gasless | Fee real 1.2-2% |
| Peer.xyz | Fiat → USDC | Rates via script inline + references peer-* |
| usdt0.to | USDT entre cadenas EVM | Solo USDT, no USDC |
| Rabby Wallet | Wallet EVM | Soporte HW (Trezor/Ledger/Keystone/BitBox) |
| Sparrow Wallet | Enviar BTC on-chain | Para todas las rutas con BTC |
