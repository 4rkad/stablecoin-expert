# Chainflip — Referencia detallada

**URL:** https://swap.chainflip.io/
**Tipo:** Protocolo de swaps cross-chain descentralizado
**Mainnet:** Noviembre 2023
**Token:** FLIP (Ethereum)

---

## Como funciona

1. **Red de validadores**: ~150 nodos que operan bovedas multi-firma (TSS)
2. **State Chain**: Cadena separada para coordinar swaps
3. **JIT AMM**: Market makers compiten en tiempo real para ofrecer el mejor precio
4. **Sin wrapping**: Los activos se intercambian de forma nativa (no hay tokens wrapped)

### Flujo de un swap BTC → USDC
1. Usuario solicita swap en la interfaz
2. Chainflip genera una **direccion BTC temporal** (deposit channel)
3. Usuario envia BTC a esa direccion
4. Validadores detectan el deposito (despues de confirmaciones)
5. JIT market makers compiten para ofrecer el mejor precio
6. Se ejecuta el swap internamente
7. Validadores envian USDC a la direccion EVM del usuario
8. Si falla: refund automatico a la direccion de refund

---

## Cadenas y activos soportados

### Cadenas (verificado via API 2026-03-30)
| Cadena | Estado | Activos |
|---|---|---|
| Bitcoin | Nativo | BTC |
| Ethereum | Nativo | ETH, USDC, USDT, FLIP, WBTC |
| Arbitrum | Nativo | ETH, USDC, USDT |
| Solana | Nativo | SOL, USDC, USDT |
| Polkadot | Nativo | DOT |
| Assethub | Nativo | DOT, USDT, USDC |

### NO soporta
- Lightning Network
- Liquid Network
- Polygon
- Rootstock
- Base (de momento)

---

## Fees

### Componentes (verificado via API cf_environment 2026-03-30)
1. **Ingress fee BTC**: 246 sats (0xf6) — fijo, muy bajo
2. **Fee del protocolo (network fee)**: **0.10%** (1000 hundredth pips) con minimo de $5 (500000 USDC units)
3. **Spread JIT AMM**: Variable, depende de liquidez y competencia entre MMs
4. **Egress fee** (red destino): Descontado del output

### Depositos minimos (verificado via API)
| Activo | Min deposito |
|---|---|
| BTC | 40,000 sats (~$34) |
| ETH (Ethereum) | 0.01 ETH |
| USDC (Ethereum) | $20 |
| USDT (Ethereum) | $20 |
| USDC (Arbitrum) | $10 |
| USDT (Arbitrum) | $10 |
| USDC (Solana) | $10 |

### Estimaciones por par
| Par | Fee total estimado | Notas |
|---|---|---|
| BTC → USDC (ETH) | 0.15-0.30% | Protocol 0.1% + LP spread + egress ETH |
| BTC → USDC (Arb) | 0.10-0.25% | Gas destino mas barato |
| BTC → USDC (SOL) | 0.10-0.20% | Gas destino muy barato |
| BTC → ETH | 0.10-0.25% | Buena liquidez |
| ETH → BTC | 0.10-0.20% | |
| USDC → BTC | 0.15-0.30% | |

**Nota:** El modelo JIT hace que los fees sean dinamicos. Para cantidades grandes, los MMs pueden ofrecer mejores precios. El minimo de $5 network fee penaliza swaps muy pequenos.

---

## Limites

- **Minimo BTC:** 40,000 sats (~$34) — mayor que el ~$10 anterior, verificado via API
- **Minimo USDC:** $10 (Arbitrum/Solana), $20 (Ethereum)
- **Network fee minimo:** $5 — penaliza swaps muy pequenos
- **Maximo:** Limitado por liquidez de los pools. Swaps de $50,000+ posibles pero con slippage
- **Nota:** THORSwap requiere 100,000 sats, Chainflip requiere 40,000 — diferencia menor de lo que se pensaba

---

## Ventajas vs THORSwap

1. **Sin minimo alto**: Puedes hacer swaps desde ~$10
2. **Fees potencialmente menores**: JIT AMM es eficiente
3. **Arbitrum nativo**: Soporte directo sin pasar por bridges
4. **Interfaz limpia**: swap.chainflip.io es simple y directa
5. **Solana**: Soporta SOL y USDC en Solana (THORSwap tambien, pero via Maya)

## Desventajas vs THORSwap

1. **Menor liquidez**: Protocolo mas joven, menos TVL
2. **Sin Polygon**: THORSwap soporta Polygon via Maya
3. **Menos cadenas**: THORSwap tiene mas variedad de cadenas
4. **Menos battle-tested**: THORChain lleva desde 2021

---

## Comparativa para el alumno

### Para obtener stablecoins en Arbitrum
**Chainflip gana**: soporte nativo, fees menores, sin minimo alto

### Para obtener stablecoins en Polygon
**THORSwap gana**: Chainflip no soporta Polygon

### Para obtener stablecoins en Ethereum
**Empate**: Similar en fees y experiencia. THORSwap tiene mas liquidez, Chainflip puede tener mejor precio via JIT

### Para cantidades < 100k sats (~$100)
**Chainflip gana**: THORSwap requiere minimo 100k sats

### Para cantidades > $10,000
**THORSwap gana**: Mayor liquidez = menor slippage

---

## Tips para el usuario

1. **Direccion de refund**: Siempre proporcionar una direccion BTC valida para refund
2. **Importe exacto**: Enviar la cantidad exacta que indica la interfaz
3. **Espera**: Las confirmaciones de BTC tardan ~10-20 min
4. **Gas destino**: Si recibes en Ethereum, necesitas ETH previo para mover stablecoins despues
5. **Arbitrum recomendado**: Gas muy barato ($0.01-0.10), ideal para la mayoria de usos
