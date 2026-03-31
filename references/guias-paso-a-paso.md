# Guias paso a paso — Stablecoin Expert

---

## Guia A: BTC → L-USDT via SideSwap peg-in (RUTA PRINCIPAL)

**Tiempo total:** ~15-20 minutos (2 conf BTC + swap instantaneo)
**Coste:** ~0.38-0.48% (instant) o ~0.20-0.30% (maker)
**Necesitas:** Sparrow Wallet, SideSwap, hardware wallet recomendado

### Paso 1: Obtener L-BTC via SideSwap peg-in
1. Abrir SideSwap → Peg-In
2. SideSwap genera una direccion BTC de peg-in
3. Copiar esa direccion
4. Enviar BTC desde Sparrow a esa direccion:
   - En Sparrow: Send → Pegar direccion peg-in → Importe
   - Ajustar fee (~1-2 sat/vbyte si no hay urgencia)
   - Firmar con hardware wallet
   - Emitir transaccion
5. Esperar 2 confirmaciones BTC (~20 min)
6. SideSwap adelanta L-BTC sin esperar las 102 conf del peg-in real (fee 0.1%)

### Paso 2: Swap L-BTC → L-USDT en SideSwap

**Opcion A: Instant Swap (rapido, fee ~0.28%)**
1. En SideSwap → Swap
2. Seleccionar L-BTC → L-USDT
3. Introducir cantidad
4. Ver precio y spread ofrecido
5. Confirmar swap → L-USDT disponible inmediatamente

**Opcion B: Crear orden Maker (barato, ~0.05-0.10% spread)**
1. En SideSwap → Swap Market → Crear orden
2. Seleccionar Vender L-BTC (recibir L-USDT)
3. Poner precio competitivo (ver orderbook para referencia)
4. Confirmar → Esperar a que un taker tome tu orden
5. Puedes cancelar en cualquier momento si no se ejecuta

### Resultado
- L-USDT disponible en SideSwap
- Puedes enviarlo a HodlHodl para lending o mantenerlo en SideSwap

---

## Guia A-alt: BTC → L-USDT via Boltz + SideSwap (FALLBACK — solo si peg-in no disponible)

**Tiempo total:** ~5-10 minutos
**Coste:** ~0.48-0.58% (instant)
**Necesitas:** Sparrow Wallet, SideSwap
**Cuando usar:** Solo si SideSwap peg-in no esta disponible o no tiene liquidez

### Paso 1: Obtener L-BTC via Boltz
1. Abrir https://boltz.exchange
2. Seleccionar **Bitcoin → Liquid** (chain swap)
3. Introducir la cantidad de BTC que quieres convertir
4. En "Direccion Liquid de destino", pegar tu direccion de SideSwap:
   - Abrir SideSwap → Recibir → L-BTC → Copiar direccion
5. Verificar la direccion comparando primeros y ultimos caracteres
6. Boltz genera una direccion BTC temporal
7. Enviar BTC desde Sparrow a esa direccion
8. Esperar 1 confirmacion BTC (~10 min)
9. Boltz ejecuta el swap y L-BTC llega a SideSwap

### Paso 2: Swap L-BTC → L-USDT en SideSwap
(Igual que Guia A, Paso 2)

### Resultado
- L-USDT disponible en SideSwap

---

## Guia B: BTC → USDC via LendaSat + Rabby (gasless)

**Tiempo total:** ~2-5 minutos
**Coste:** ~0.25% + 16-17 sats
**Necesitas:** Sparrow/LN wallet, Rabby Wallet (con hardware wallet)

### Preparacion: Instalar Rabby
1. Descargar extension Rabby desde https://rabby.io
2. Instalar en Brave/Chrome
3. Conectar hardware wallet (Trezor/Ledger/Keystone/BitBox):
   - Para Ledger: instalar app Ethereum en Ledger primero
   - Poner contrasena en Rabby
   - Seleccionar cuenta (si ya tienes una usada, elegir la siguiente)
4. Etiquetar wallet (ej: "Lending")
5. Ir a Recibir → Copiar direccion EVM

### Paso 1: Swap en LendaSat
1. Ir a https://lendasat.com
2. Seleccionar **BTC → USDC**
3. Elegir cadena destino: **Polygon** o **Arbitrum**
4. Pegar tu direccion de Rabby como destino
5. Verificar la direccion
6. Introducir cantidad ($5 a $2,000)
7. LendaSat genera direccion/invoice BTC
8. Enviar BTC desde Sparrow (o pagar invoice LN)
9. Esperar ~1-2 min

### Paso 2: Verificar en Rabby
1. Abrir Rabby → ver balance
2. USDC debe aparecer en la cadena seleccionada (Polygon o Arbitrum)
3. Listo para enviar a HodlHodl o donde necesites

### Ventajas de esta ruta
- **Gasless:** LendaSat cubre el gas en Polygon/Arbitrum — no necesitas MATIC/ETH
- **Rapido:** Minutos
- **Simple:** Sin pasos intermedios

---

## Guia C: BTC → USDC/USDT via Chainflip

**Tiempo total:** ~15-20 minutos
**Coste:** ~0.2-0.3%
**Necesitas:** Sparrow Wallet, Rabby Wallet (con hardware wallet)

### Paso 1: Preparar Rabby (si no lo tienes)
- Ver seccion "Preparacion: Instalar Rabby" en Guia B

### Paso 2: Swap en Chainflip
1. Ir a https://swap.chainflip.io/
2. Seleccionar origen: **Bitcoin**
3. Seleccionar destino: **USDC** (o USDT) en **Ethereum** o **Arbitrum**
4. Introducir cantidad de BTC a enviar
5. Ver cotizacion: precio estimado, fees, output esperado
6. Pegar direccion de destino (tu direccion Rabby)
7. Proporcionar direccion de refund BTC (una direccion de Sparrow)
8. Confirmar → Se genera direccion BTC temporal
9. Enviar BTC **exacto** desde Sparrow a esa direccion
10. Esperar ~15 min (confirmaciones BTC + ejecucion swap)
11. Recibir USDC/USDT en Rabby

### Notas importantes
- El importe debe ser **exacto** segun lo que indica Chainflip
- Si el swap falla (slippage, error), refund automatico a la direccion proporcionada
- Para mover las stablecoins luego, necesitas ETH como gas en la cadena destino
- Si usas Arbitrum, el gas es muy barato (~$0.01-0.10 por tx)

---

## Guia D: BTC → USDC/USDT via THORSwap

**Tiempo total:** ~15-20 minutos
**Coste:** ~0.3-0.5%
**Necesitas:** Sparrow Wallet, Rabby Wallet (con hardware wallet)
**Minimo:** 100,000 sats

### Paso 1: Obtener ETH para gas (si no tienes)
1. Ir a Unstoppable Money (para cantidades pequenas de ETH)
2. Seleccionar BTC → ETH
3. Pegar direccion Rabby como destino
4. Proporcionar direccion BTC refund
5. Enviar ~50,000 sats desde Sparrow
6. Esperar → Recibir ~$30-35 en ETH
7. Este ETH servira como gas para futuras transacciones

### Paso 2: Swap BTC → Stablecoin
1. Ir a https://app.thorswap.finance/
2. Seleccionar **Bitcoin → USDC** (o USDT)
3. Elegir cadena: Ethereum, Arbitrum, o Polygon
4. Introducir cantidad (minimo 100,000 sats)
5. **Configurar slippage a 1%** (Settings → Slip Tolerance)
6. Conectar wallet EVM: Click MetaMask → Rabby intercepta
7. Verificar cotizacion, fees, y output esperado
8. Click "Swap"
9. Copiar la direccion BTC que aparece
10. **Verificar la direccion cuidadosamente**
11. Enviar importe **EXACTO** desde Sparrow:
    - Etiquetar como "Swap a USDC THORSwap"
    - Ajustar fee (1-2 sat/vbyte)
    - Firmar con hardware wallet
12. Ventana de 6 horas para completar el envio
13. Esperar ~15 min → USDC/USDT aparece en Rabby

### Paso 3: Vuelta BTC (cuando quieras)
1. En THORSwap, seleccionar USDC → Bitcoin
2. Conectar wallet EVM (MetaMask → Rabby)
3. Seleccionar 100% del balance USDC
4. **Primera firma**: Approve (autorizar USDC para el swap)
5. **Segunda firma**: Swap (ejecutar el intercambio)
6. Pegar direccion BTC de Sparrow como destino
7. Verificar direccion
8. Firmar ambas transacciones con hardware wallet
9. Esperar ~15 min → BTC en Sparrow
10. El ETH restante se queda como gas para el siguiente movimiento

### Notas
- THORSwap: refund automatico a direccion origen si el swap falla
- Unstoppable Money: pide refund address explicitamente
- Para cantidades < 100k sats, usar Chainflip o LendaSat en vez de THORSwap

---

## Guia E: Fiat → BTC/USDC via Peer.xyz

**Tiempo total:** Variable (depende del vendedor)
**Coste:** 2-5% spread tipico
**Necesitas:** Cuenta bancaria/Bizum/Revolut, wallet crypto

Ver script inline de Peer en SKILL.md para rates en vivo. Para guia completa: `{baseDir}/references/peer-buying-guide.md`

Resumen rapido:
1. Ir a peer.xyz
2. Seleccionar moneda fiat (EUR, USD, GBP, etc.)
3. Elegir metodo de pago (Bizum, SEPA, Revolut, etc.)
4. Elegir crypto destino (BTC o USDC)
5. Conectar wallet o pegar direccion
6. Enviar pago fiat al vendedor
7. Recibir crypto automaticamente via smart contract

---

## Consejo general: Elegir la cadena de destino

| Destino | Mejor para | Gas necesario | Privacidad |
|---|---|---|---|
| **Liquid (L-USDT)** | HodlHodl Lend ordenes Liquid, maxima privacidad | L-BTC (minimo) | Alta (Confidential TX) |
| **Ethereum (USDC/USDT)** | HodlHodl Lend ordenes ETH, maxima liquidez | ETH ($1-5/tx) | Baja (transparente) |
| **Arbitrum (USDC/USDT)** | Fees bajos, DeFi | ETH ($0.01-0.10/tx) | Baja |
| **Polygon (USDC)** | Fees minimos, muchas ordenes HH | MATIC (casi gratis) | Baja |
| **Rootstock (DOC/USDT)** | Stablecoin colateralizada por BTC | RBTC | Baja |
