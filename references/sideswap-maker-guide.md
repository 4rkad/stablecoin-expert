# SideSwap Market Maker Guide

## Overview

The swap market operates as a non-custodial exchange on the Liquid Bitcoin network. Market makers (makers) provide liquidity by placing limit orders. Exchange operations are constructed as confidential Liquid Bitcoin transactions and settled on-chain.

## Order Types

### Online Limit Orders
- Maker must be connected to the server
- Server requires list of UTXOs and receive/change addresses
- Client submits an order list
- Can be **partially matched**
- If maker doesn't sign in time, they get disconnected and orders are pulled temporarily

### Offline Limit Orders
- Maker provides a pre-signed Liquid transaction
- One input, one output
- Input signed with `SIGHASH_SINGLE | ANYONECANPAY`
- Input asset/value and output asset/value determine market, direction, and price
- Can only be **fully matched** (no partial fills)
- Hardware wallets supported (currently Jade only)

## Fee Structure

- **Makers pay 0% fee**
- Takers pay 0.2% + fixed network fee
- For asset/asset swaps, server includes its own L-BTC inputs to cover the network fee

## Running Your Own Dealer

SideSwap provides an open-source dealer implementation:
https://github.com/sideswap-io/sideswapclient/tree/master/rust/sideswap_dealer_elements

For custom market maker integrations, contact SideSwap support.

## Swap Flow (Taker Side)

1. Taker sends `start_quotes` with UTXOs, addresses, amount, and direction
2. Server constructs a PSET (Partially Signed Elements Transaction)
3. Multiple makers can participate in one swap transaction
4. Online makers are requested to sign the PSET
5. Once all maker inputs are signed, taker receives the quote
6. Taker has ~30 seconds to accept
7. Server repeats this process every ~5 seconds for fresh quotes

## AMP Assets

AMP (Blockstream Asset Management Platform) assets use multi-sig. For AMP swaps, the server only requires user signatures (not the AMP co-signer).
