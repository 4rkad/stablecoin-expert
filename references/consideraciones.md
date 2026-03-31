# Consideraciones — Privacidad, Riesgos, Censura, Fiscalidad

---

## 1. Privacidad: Liquid vs EVM

### Liquid Network
- **Confidential Transactions** por defecto: importes y tipo de activo estan cifrados
- Solo emisor y receptor pueden ver los importes (blinding keys)
- Explorador (liquid.network) muestra "Confidential" en campos de valor
- **Direcciones nuevas** cada vez (como Bitcoin)
- Mejor privacidad que Bitcoin on-chain y mucho mejor que EVM

### Cadenas EVM (Ethereum, Polygon, Arbitrum)
- **Todo es publico**: importes, direcciones origen/destino, historico completo
- **Direccion estatica**: se reutiliza la misma direccion para todo
- Con una sola direccion se puede ver:
  - Balance actual de todos los tokens
  - Historico completo de transacciones
  - Actividad en TODAS las cadenas EVM (misma direccion cross-chain)
- Ejemplo real: la direccion de Vitalik (0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045) muestra 73,823 transacciones y fondos en 7+ cadenas
- Si alguna vez hiciste KYC con esa direccion, tu identidad esta vinculada permanentemente

### Privacidad en la ruta Liquid — Consideraciones detalladas

**ENTRADA (BTC → Liquid via SideSwap peg-in):**
- SideSwap **adelanta L-BTC de sus reservas** — el L-BTC que recibes NO tiene relacion on-chain con tu UTXO de Bitcoin
- Es un corte natural de la cadena de trazabilidad — un analista no puede vincular tu BTC con tu L-BTC
- **Punto debil:** SideSwap como empresa si sabe que tu (IP/sesion) enviaste X BTC y recibiste Y L-BTC

**Control de UTXOs en Bitcoin:**
- En Sparrow, elegir que UTXO especifica envias al peg-in — no usar UTXOs de exchanges KYC
- **Enviar la UTXO completa** sin cambio — Boltz permite enviar un rango de valores (no importe exacto), asi puedes gastar la UTXO entera sin generar cambio
- Si no puedes evitar cambio con SideSwap peg-in (pide importe fijo), ese cambio queda vinculado a la tx del peg-in
- No consolidar muchas UTXOs antes del peg-in — vinculas todas tus direcciones entre si
- Al recibir BTC de vuelta de Boltz: **etiquetar en Sparrow** y nunca gastar junto con UTXOs KYC (coin control)

**DENTRO de Liquid:**
- Confidential Transactions ocultan importes pero no direcciones
- SideSwap genera direccion nueva automaticamente
- El operador de SideSwap ve los detalles del swap (es contraparte)

**SALIDA (Liquid → BTC via Boltz Tor):**
- Acceder SIEMPRE por la direccion .onion de Boltz, no por clearnet
- Si usas clearnet, Boltz ve tu IP y puede correlacionar el swap
- No reutilizar la direccion BTC de destino
- Espaciar temporalmente si haces varias salidas

**Riesgos que persisten:**
| Riesgo | Descripcion |
|---|---|
| SideSwap como contraparte | Ve ambos lados: tu BTC de entrada y tu L-BTC/L-USDT |
| Federacion Liquid | 15 firmantes validan bloques. Podrian censurar tx, nunca ha pasado |
| Correlacion temporal | Si entras y sales rapido con importes similares, se puede inferir |
| Boltz sin Tor | Si accedes por clearnet, Boltz ve tu IP + detalles del swap |

**Practicas recomendadas:**
1. Seleccionar UTXO limpia en Sparrow, enviar completa sin cambio (Boltz acepta rango)
2. No enviar desde exchange KYC directamente al peg-in
3. VPN/Tor para SideSwap — minimizar correlacion IP
4. Tor obligatorio para Boltz (.onion) en la vuelta
5. No importes redondos — 0.03487 BTC es menos rastreable que 0.035 BTC
6. Espaciar operaciones — no peg-in + swap + lending en 5 minutos
7. Etiquetar y no mezclar UTXOs limpias con KYC en Sparrow (coin control)
8. Hardware wallet para firmar
9. No mezclar sesiones con operaciones en cadenas transparentes (EVM)

### Comparacion de privacidad Liquid vs EVM

| Aspecto | Liquid | EVM (Chainflip/Boltz USDT) |
|---|---|---|
| Importes visibles | **No** (Confidential Tx) | Si, publicos |
| Vinculo entrada→salida | **Roto** (SideSwap adelanta) | Directo (misma tx) |
| Historial rastreable | Parcial (grafo sin importes) | **Completo** |
| Direccion reutilizada | No (nueva cada vez) | **Si** (misma para todo) |
| Congelacion de fondos | Sin precedentes | >$3,100M congelados |
| Cross-chain tracking | Dificil | Trivial (misma dir en todas las EVM) |

### Recomendacion
- Para maxima privacidad: **Liquid (L-USDT)** con las practicas de arriba
- Si usas EVM: crear wallets separadas para distintos propositos
- Nunca enviar desde una direccion con KYC a una sin KYC directamente
- Si necesitas privacidad en EVM: usar wallets separadas, distintas hardware wallets

---

## 2. Riesgo de censura de stablecoins

### USDT (Tether)
- Mas de **$3,100M congelados** historicamente en direcciones de Ethereum
- Tether puede congelar cualquier direccion en Ethereum/Tron/otras cadenas EVM
- El congelamiento es irreversible sin autorizacion de Tether
- **Regulacion MiCA (Europa):** Tether tuvo que salir del mercado europeo por MiCA. Creo un nuevo token (USD) para cumplir regulacion de EEUU. La regulacion puede afectar la disponibilidad de stablecoins en cualquier momento, no solo las monedas sino tambien las plataformas.

### L-USDT (Liquid)
- Emitido por **Blockstream** (no directamente por Tether)
- Historicamente **no ha habido congelaciones** en Liquid
- Confidential Transactions dificultan la identificacion de titulares
- **Menor riesgo relativo**, aunque no inmune teoricamente

### USDC (Circle)
- Circle tambien puede congelar direcciones (lo ha hecho, ej: Tornado Cash)
- Mas regulado que Tether, responde a sanciones OFAC

### DOC (Money on Chain / Rootstock)
- **Colateralizada por BTC**, no por reservas fiat
- No puede ser censurada por un emisor centralizado
- Riesgo: menor liquidez, dependencia del smart contract

### Recomendacion
- Diversificar entre L-USDT y USDC si es posible
- Para importes grandes o largo plazo: preferir L-USDT
- Ser consciente de que CUALQUIER stablecoin centralizada puede ser censurada
- No mantener grandes cantidades en una sola stablecoin/cadena

---

## 3. Riesgos por cadena

| Cadena | Riesgo principal | Mitigacion |
|---|---|---|
| **Liquid** | Federacion de 15 firmantes (funcionalarios de Blockstream + partners) | Menor riesgo de censura, pero dependencia de la federacion |
| **Ethereum** | Gas alto, congelamiento tokens, transparencia total | Usar L2s (Arbitrum, Polygon) para fees bajos |
| **Arbitrum** | Rollup optimista — periodo de disputa de 7 dias para retirar a L1 | Usar para operaciones en L2, no para bridge frecuente a L1 |
| **Polygon** | PoS chain — mas centralizada que Ethereum | Fees casi nulos, buena para cantidades pequenas |
| **Rootstock** | Merge-mined con Bitcoin — menos desarrolladores y liquidez | Para entusiastas de BTC-DeFi |

---

## 4. Fiscalidad (orientativo — no es asesoramiento)

### Swaps BTC → Stablecoin
- En la mayoria de jurisdicciones, un swap BTC → USDT/USDC es un **evento imponible**
- Se considera venta de BTC al precio de mercado
- La ganancia/perdida se calcula vs precio de adquisicion del BTC

### Stablecoins como colateral en lending
- Prestar stablecoins: los intereses recibidos pueden ser ingreso imponible
- Pedir prestado contra BTC: generalmente NO es evento imponible (no vendes BTC)

### Movimientos entre cadenas
- Bridge L-USDT → USDT EVM: generalmente **no es evento imponible** (mismo activo)
- Swap USDT → USDC: puede ser evento imponible en algunas jurisdicciones

### Recomendaciones generales
- Mantener registro de cada swap: fecha, cantidades, fees, tipo de cambio
- Consultar con un asesor fiscal en tu jurisdiccion
- Las herramientas de tracking (Koinly, CoinTracking, etc.) pueden ayudar

---

## 5. Seguridad operativa

### Hardware wallet — SIEMPRE para importes > $500
- Rabby Wallet soporta: Trezor, Ledger, Keystone, BitBox Multi
- Firmar SIEMPRE desde el dispositivo, verificar en pantalla
- No usar hot wallets (extensiones solas) para importes significativos

### Verificacion de direcciones
- Copiar-pegar y comparar primeros + ultimos caracteres
- En hardware wallet, verificar la direccion en la pantalla del dispositivo
- Nunca enviar a direcciones que no sean tuyas o de un swap verificado

### Proteccion contra phishing
- Verificar siempre las URLs:
  - boltz.exchange (no boltz.io, boltzswap.com, etc.)
  - sideswap.io
  - lendasat.com
  - swap.chainflip.io
  - app.thorswap.finance
  - peer.xyz
- Guardar en marcadores las URLs correctas
- No hacer click en links de Telegram/Discord/email

### Slippage y proteccion de precio
- Configurar tolerancia al 1% en THORSwap
- Si hay volatilidad alta, mejor esperar o reducir la tolerancia
- Chainflip usa JIT AMM que mitiga slippage automaticamente

---

## 6. Cuanto cubre cada via para HodlHodl Lend

Basado en las ordenes disponibles en HodlHodl:
- **L-USDT (Liquid):** ~25-30% de las ordenes
- **USDC/USDT (Ethereum):** ~50% de las ordenes
- **USDC/USDT (Polygon/Arbitrum):** ~15-20% de las ordenes
- **Total con Liquid + Ethereum:** >75% de ordenes cubiertas
- **Total con todas las cadenas:** >90% de ordenes cubiertas
