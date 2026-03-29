# Guía de Normalización de Símbolos

**Última Actualización:** 29 de Marzo, 2026  
**Módulo:** `volume_sorted_coin_list.py`

---

## Resumen

Diferentes exchanges usan diferentes convenciones de nomenclatura de símbolos. Esta guía explica cómo funciona la normalización de símbolos y cómo solucionar problemas al agregar nuevos exchanges.

---

## Formatos de Símbolos por Exchange

| Exchange | Formato | Ejemplo | Normalizado |
|----------|--------|---------|-------------|
| **Binance** | `BTCUSDT` | `BTCUSDT` | `BTCUSDT` |
| **Bybit** | `BTCUSDT` | `BTCUSDT` | `BTCUSDT` |
| **OKX** | `BTC-USDT-SWAP` | `BTC-USDT-SWAP` | `BTCUSDT` |
| **Bitget** | `BTCUSDT` | `BTCUSDT` | `BTCUSDT` |
| **BingX** | `BTC-USDT` | `BTC-USDT` | `BTCUSDT` |
| **KuCoin** | `XBTUSDTM` | `XBTUSDTM` | `XBTUSDTM` |

---

## Lógica de Normalización Actual

Ubicada en la función `get_ccxt_symbols_by_volume()`:

```python
# --- NORMALIZACIÓN DE ID ---
raw_id = market['id']
clean_id = raw_id

# Caso OKX: BTC-USDT-SWAP -> BTCUSDT
if clean_id.endswith('-SWAP'):
    clean_id = clean_id.replace('-SWAP', '').replace('-', '')
# Caso BingX: BTC-USDT -> BTCUSDT
elif '-' in clean_id and clean_id.endswith('-USDT'):
    clean_id = clean_id.replace('-', '')

base_candidates.append(clean_id)
```

---

## Agregar Normalización para Nuevos Exchanges

### Paso 1: Identificar el Patrón

Verifica qué formato usa el exchange:

```python
import ccxt

exchange = ccxt.kucoin()
exchange.load_markets()

# Imprimir los primeros 10 IDs de mercados swap
swap_markets = [m for m in exchange.markets.values()
                if m.get('swap') and m.get('quote') == 'USDT']

for m in swap_markets[:10]:
    print(f"ID: {m['id']} | Símbolo: {m['symbol']}")
```

### Paso 2: Agregar Regla de Normalización

Agrega la regla en el orden correcto (lo más específico primero):

```python
# --- NORMALIZACIÓN DE ID ---
raw_id = market['id']
clean_id = raw_id

# Caso OKX: BTC-USDT-SWAP -> BTCUSDT
if clean_id.endswith('-SWAP'):
    clean_id = clean_id.replace('-SWAP', '').replace('-', '')

# Caso Gate.io: BTC_USDT -> BTCUSDT
elif '_' in clean_id and clean_id.endswith('_USDT'):
    clean_id = clean_id.replace('_', '')

# Caso BingX: BTC-USDT -> BTCUSDT
elif '-' in clean_id and clean_id.endswith('-USDT'):
    clean_id = clean_id.replace('-', '')

# Por defecto: ya está limpio (Binance, Bybit, Bitget)
# clean_id permanece sin cambios

base_candidates.append(clean_id)
```

---

## Patrones Comunes y Soluciones

### Patrón 1: Separador de Guion Bajo

**Exchange:** Gate.io y otros  
**Formato:** `BTC_USDT`  
**Solución:**
```python
if '_' in clean_id and clean_id.endswith('_USDT'):
    clean_id = clean_id.replace('_', '')
```

### Patrón 2: Separador de Barra

**Exchange:** Algunos exchanges usan `BTC/USDT`  
**Formato:** `BTC/USDT`  
**Solución:**
```python
if '/' in clean_id:
    clean_id = clean_id.replace('/', '')
```

### Patrón 3: Variaciones de Sufijo

**Exchange:** Algunos usan sufijo `PERP`  
**Formato:** `BTCUSDT-PERP`  
**Solución:**
```python
if clean_id.endswith('-PERP'):
    clean_id = clean_id.replace('-PERP', '')
```

### Patrón 4: Moneda de Cotización Diferente

**Exchange:** Algunos usan `USD` en lugar de `USDT`  
**Formato:** `BTCUSD`  
**Solución:** Actualiza la lógica de filtrado, no solo la normalización

---

## Lógica de Filtrado

El script filtra los mercados antes de la normalización:

```python
# --- FILTROS DE MERCADO ---
# 1. Contrato (Derivativo)
if not market.get('contract'):
    continue

# 2. Margen en USDT (Linear)
is_linear = market.get('linear', False) is True
is_usdt = market.get('quote') == 'USDT'
is_active = market.get('active', True)

# Verificación adicional para BingX/otros donde 'linear' puede no ser explícito
if not is_linear:
    if market.get('type') == 'swap' and market.get('quote') == 'USDT':
        is_linear = True

if not (is_linear and is_usdt and is_active):
    continue
```

### Agregar Nuevas Condiciones de Filtrado

Si un nuevo exchange necesita filtrado especial:

```python
# Ejemplo Gate.io: usa campo 'settle'
if exchange_id == "gateio":
    is_usdt = market.get('settle') == 'usdt'
else:
    is_usdt = market.get('quote') == 'USDT'
```

---

## Testing de Normalización

### Script de Prueba

```python
import ccxt
from exchanges import create_ccxt_client

# Probar con nuevo exchange
exchange_id = "kucoin"
client = create_ccxt_client(exchange_id)

tickers = client.fetch_tickers()

for symbol, ticker in list(tickers.items())[:5]:
    market = client.markets.get(symbol)
    if not market:
        continue

    # Aplicar tu lógica de normalización
    raw_id = market['id']
    clean_id = raw_id

    # Agregar tus reglas aquí
    if '-' in raw_id:
        clean_id = raw_id.replace('-', '')

    print(f"Raw: {raw_id:20} -> Clean: {clean_id}")
```

### Salida Esperada

```
Raw: BTC-USDT-SWAP       -> Clean: BTCUSDT
Raw: ETH-USDT-SWAP       -> Clean: ETHUSDT
Raw: SOL-USDT-SWAP       -> Clean: SOLUSDT
```

---

## Problemas Comunes

### Problema 1: Símbolos Duplicados

**Problema:** La misma coin aparece dos veces después de la normalización

**Causa:** Diferentes tipos de mercado se normalizan al mismo ID

**Solución:** Usar desduplicación basada en volumen (ya implementada):
```python
if clean_id not in vol_map:
    final_list.append(clean_id)
    vol_map[clean_id] = quote_vol
```

### Problema 2: Símbolos Incorrectos Incluidos

**Problema:** Activos no-cripto pasan el filtro

**Causa:** El filtro `is_likely_crypto()` no detecta nuevos patrones

**Solución:** Actualiza la lista de bloqueo en `is_likely_crypto()`:
```python
BLOCKLIST = [
    "ALUMINIUM", "ALUM", "COPPER", "ZINC",  # Metales
    "GOLD", "SILVER", "PLATINUM",           # Metales preciosos
    "OIL", "GAS", "BRENT", "WTI",           # Energía
    "SPX500", "NAS100", "US30",             # Índices
    "FOREX", "INDEX"                        # Tipos
]
```

### Problema 3: Símbolos No Normalizados

**Problema:** El archivo de salida contiene guiones o guiones bajos

**Causa:** La regla de normalización no coincide con el patrón

**Solución:** Verifica el formato exacto y agrega la regla correcta:
```python
# Debug: imprimir IDs raw
print(f"Raw ID sample: {market['id']}")
# Luego agregar la regla correspondiente
```

---

## Notas Específicas por Exchange

### OKX
- Formato: `BTC-USDT-SWAP`
- Regla: Eliminar `-SWAP` luego eliminar `-`
- Ya soportado ✓

### BingX
- Formato: `BTC-USDT`
- Regla: Eliminar `-`
- Ya soportado ✓

### Gate.io
- Formato: `BTC_USDT` (guion bajo)
- Regla: Eliminar `_`
- **Necesita ser agregado**

### KuCoin
- Formato: `XBTUSDTM` (ya limpio)
- Regla: No necesita normalización
- Usa `XBT` en lugar de `BTC`

### Bybit
- Formato: `BTCUSDT` (ya limpio)
- Regla: No necesita normalización
- Ya soportado ✓

### Binance
- Formato: `BTCUSDT` (ya limpio)
- Regla: No necesita normalización
- Ya soportado ✓

---

## Mejores Prácticas

1. **Lo Más Específico Primero**: Verifica `-SWAP` antes de verificar `-`
2. **Preservar el Original**: Siempre comienza con `clean_id = raw_id`
3. **Probar Extensamente**: Verifica con múltiples símbolos del exchange
4. **Documentar Cambios**: Agrega comentarios explicando cada regla
5. **Validar Salida**: Verifica que los archivos generados tengan el formato correcto

---

## Lista de Verificación de Validación

Después de agregar normalización para un nuevo exchange:

- [ ] Ejecutar script con el nuevo exchange
- [ ] Verificar archivo de salida para formato correcto de símbolos
- [ ] Verificar que no haya guiones o guiones bajos en los símbolos
- [ ] Confirmar que el ordenamiento por volumen funciona
- [ ] Verificar que no haya símbolos duplicados
- [ ] Asegurar que los activos no-cripto estén filtrados
- [ ] Probar con `--output-format toon` para legibilidad
- [ ] Probar con `--output-format csv` para lista limpia

---

## Ejemplo: Agregar Normalización para Gate.io

```python
# En get_ccxt_symbols_by_volume()

# --- NORMALIZACIÓN DE ID ---
raw_id = market['id']
clean_id = raw_id

# Caso OKX: BTC-USDT-SWAP -> BTCUSDT
if clean_id.endswith('-SWAP'):
    clean_id = clean_id.replace('-SWAP', '').replace('-', '')

# Caso Gate.io: BTC_USDT -> BTCUSDT
elif '_' in clean_id and clean_id.endswith('_USDT'):
    clean_id = clean_id.replace('_', '')

# Caso BingX: BTC-USDT -> BTCUSDT
elif '-' in clean_id and clean_id.endswith('-USDT'):
    clean_id = clean_id.replace('-', '')

base_candidates.append(clean_id)
```

---

## Documentación Relacionada

- [Cómo Agregar Exchanges](ADDING_EXCHANGES.es.md) - Guía completa para agregar nuevos exchanges
- [exchanges.py](../exchanges.py) - Módulo de configuración de exchanges
- [README.es.md](../README.es.md) - Documentación principal en español

---

## Recursos Adicionales

- [Documentación CCXT](https://docs.ccxt.com/)
- [Lista de Exchanges CCXT](https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets)
- [Manual CCXT](https://github.com/ccxt/ccxt/wiki/Manual)

---

**¿Preguntas?** Contacta a @comgunner en GitHub
