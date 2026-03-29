# Cómo Agregar Nuevos Exchanges al Generador de Listas de Coins

**Última Actualización:** 29 de Marzo, 2026  
**Módulo:** `exchanges.py`

---

## Resumen

Esta guía explica cómo agregar soporte para nuevos exchanges de criptomonedas al generador de listas de coins. El script está diseñado para **mercados de futuros/derivativos** (swaps con margen en USDT), por lo que la configuración correcta es esencial para evitar errores.

---

## Prerrequisitos

1. **Soporte CCXT**: El exchange debe estar soportado por la [librería CCXT](https://github.com/ccxt/ccxt)
2. **Mercados de Futuros/Swap**: El exchange debe ofrecer swaps perpetuos o futuros con margen en USDT
3. **Acceso Público a la API**: Al menos acceso público a datos de mercado (la autenticación es opcional para límites más altos)

---

## Guía Paso a Paso

### Paso 1: Verificar Soporte CCXT

Verifica si el exchange está soportado por CCXT:

```python
import ccxt

# Listar todos los exchanges soportados
print(ccxt.exchanges)

# Verificar exchange específico
if hasattr(ccxt, 'kucoin'):
    print("¡KuCoin está soportado!")
```

### Paso 2: Probar Mercados de Futuros

Verifica que el exchange tenga futuros/swaps en USDT:

```python
import ccxt

exchange = ccxt.kucoin()  # Reemplaza con tu exchange
exchange.load_markets()

# Verificar mercados de swap/futuros
swap_markets = [m for m in exchange.markets.values()
                if m.get('swap') and m.get('quote') == 'USDT']

print(f"Se encontraron {len(swap_markets)} mercados swap en USDT")
```

### Paso 3: Editar `exchanges.py`

Abre `exchanges.py` y realiza los siguientes cambios:

#### 3.1 Agregar a `SUPPORTED_EXCHANGES`

```python
SUPPORTED_EXCHANGES = ["binance", "bybit", "bingx", "okx", "bitget", "kucoin"]
#                                                              ^^^^^^ Agregar aquí
```

#### 3.2 Agregar a `CREDENTIALS_MAP`

Agrega el mapeo de credenciales de API (incluso si es opcional):

```python
CREDENTIALS_MAP = {
    "binance": {"apiKey": "BINANCE_API_KEY", "secret": "BINANCE_API_SECRET"},
    "bybit":   {"apiKey": "BYBIT_API_KEY",   "secret": "BYBIT_API_SECRET"},
    "bingx":   {"apiKey": "BINGX_API_KEY",   "secret": "BINGX_API_SECRET"},
    "okx":     {"apiKey": "OKX_API_KEY",     "secret": "OKX_API_SECRET", "password": "OKX_PASSWORD"},
    "bitget":  {"apiKey": "BITGET_API_KEY",  "secret": "BITGET_API_SECRET", "password": "BITGET_PASSWORD"},
    "kucoin":  {"apiKey": "KUCOIN_API_KEY",  "secret": "KUCOIN_API_SECRET", "password": "KUCOIN_PASSWORD"},
    #          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Agregar aquí
}
```

**Nota**: Algunos exchanges requieren passphrase (OKX, Bitget, KuCoin).

#### 3.3 Agregar a `EXCHANGE_TYPE_MAP`

Especifica el tipo de mercado correcto para futuros:

```python
EXCHANGE_TYPE_MAP = {
    "binance": "future",    # Binance Futures
    "bybit": "linear",      # Bybit Linear (USDT)
    "bingx": "swap",        # BingX Swaps
    "okx": "swap",          # OKX Swaps
    "bitget": "swap",       # Bitget Swaps
    "kucoin": "swap",       # KuCoin Swaps
    #         ^^^^^^ Agregar aquí con el tipo correcto
}
```

**Tipos de Mercado Comunes:**
- `"future"` - Futuros estilo Binance
- `"linear"` - Contratos lineales estilo Bybit (con margen en USDT)
- `"swap"` - Swaps perpetuos (el más común)
- `"inverse"` - Contratos inversos (con margen en moneda, menos común)

#### 3.4 Actualizar `build_exchange_config()` (si es necesario)

La mayoría de exchanges funcionan con la configuración por defecto. Agrega manejo especial si es necesario:

```python
def build_exchange_config(exchange_id):
    """Construir diccionario de configuración CCXT para un exchange específico."""
    config = {
        "enableRateLimit": True,
        "options": {"defaultType": "swap"}
    }

    exchange_type = EXCHANGE_TYPE_MAP.get(exchange_id, "swap")

    if exchange_id == "binance":
        config["options"]["defaultType"] = "future"
    elif exchange_id == "bybit":
        config["options"]["defaultType"] = "linear"
        config["options"]["adjustForTimeDifference"] = True  # Bybit necesita sincronización de tiempo
    elif exchange_id == "kucoin":
        config["options"]["defaultType"] = "swap"
        # Agregar opciones específicas de KuCoin aquí si es necesario
    elif exchange_id in ["bingx", "okx", "bitget"]:
        config["options"]["defaultType"] = exchange_type

    return config
```

### Paso 4: Actualizar `.env.example`

Agrega la plantilla de credenciales del nuevo exchange:

```bash
# KuCoin
KUCOIN_API_KEY=
KUCOIN_API_SECRET=
KUCOIN_PASSWORD=
```

### Paso 5: Probar el Nuevo Exchange

```bash
# Probar un exchange
EXCHANGE_CCXT=kucoin python volume_sorted_coin_list.py

# Probar con todos los exchanges (incluye el nuevo)
python volume_sorted_coin_list.py --all-exchanges
```

---

## Problemas Comunes y Soluciones

### Problema 1: No Se Encontraron Mercados

**Problema:** El script reporta "0 símbolos obtenidos"

**Causas:**
1. Configuración de tipo de mercado incorrecta
2. El exchange no tiene futuros en USDT
3. El endpoint de la API cambió

**Solución:**
```python
# Debug: Verificar qué mercados están disponibles
import ccxt
exchange = ccxt.kucoin()
exchange.load_markets()

# Imprimir tipos de mercado
types = set(m.get('type') for m in exchange.markets.values())
print(f"Tipos de mercado disponibles: {types}")

# Verificar mercados en USDT
usdt_markets = [m for m in exchange.markets.values() if m.get('quote') == 'USDT']
print(f"Mercados en USDT: {len(usdt_markets)}")
```

### Problema 2: Errores de Autenticación

**Problema:** Errores de API incluso con credenciales

**Solución:**
1. Verifica que los nombres de credenciales en `CREDENTIALS_MAP` coincidan con las variables `.env`
2. Verifica si el exchange requiere passphrase
3. Asegúrate de que las claves API tengan los permisos correctos (solo lectura es suficiente)

### Problema 3: Errores de Límite de Tasa

**Problema:** Errores "Rate limit exceeded"

**Solución:**
```python
# Agregar configuración personalizada de límite de tasa
if exchange_id == "kucoin":
    config["rateLimit"] = 1000  # Aumentar retraso entre solicitudes
    config["enableRateLimit"] = True
```

### Problema 4: Tipo de Contrato Incorrecto

**Problema:** El script obtiene mercados spot en lugar de futuros

**Solución:**
Verifica que `EXCHANGE_TYPE_MAP` sea correcto y `defaultType` esté configurado correctamente:

```python
# Para la mayoría de exchanges de futuros en USDT:
config["options"]["defaultType"] = "swap"  # o "future" o "linear"
```

---

## Referencia de Configuración de Exchanges

### Binance
```python
"binance": {
    "type": "future",
    "credentials": ["apiKey", "secret"],
    "notas": "Usa 'future' para futuros USDⓈ-M"
}
```

### Bybit
```python
"bybit": {
    "type": "linear",
    "credentials": ["apiKey", "secret"],
    "notas": "Necesita adjustForTimeDifference=True"
}
```

### OKX
```python
"okx": {
    "type": "swap",
    "credentials": ["apiKey", "secret", "password"],
    "notas": "Requiere passphrase"
}
```

### Bitget
```python
"bitget": {
    "type": "swap",
    "credentials": ["apiKey", "secret", "password"],
    "notas": "Requiere passphrase"
}
```

### BingX
```python
"bingx": {
    "type": "swap",
    "credentials": ["apiKey", "secret"],
    "notas": "Usa mercados swap estándar"
}
```

### KuCoin (Ejemplo)
```python
"kucoin": {
    "type": "swap",
    "credentials": ["apiKey", "secret", "password"],
    "notas": "Requiere passphrase para futuros"
}
```

---

## Lista de Verificación de Testing

Antes de enviar un nuevo exchange, verifica:

- [ ] El exchange está soportado por CCXT
- [ ] El exchange tiene futuros/swaps con margen en USDT
- [ ] `SUPPORTED_EXCHANGES` incluye el ID del exchange
- [ ] `CREDENTIALS_MAP` tiene los nombres correctos de credenciales
- [ ] `EXCHANGE_TYPE_MAP` tiene el tipo de mercado correcto
- [ ] El script se ejecuta sin errores: `EXCHANGE_CCXT=xyz python script.py`
- [ ] El archivo de salida se genera con datos válidos
- [ ] Los símbolos están correctamente normalizados (sin guiones, etc.)
- [ ] El ordenamiento por volumen funciona correctamente

---

## Mejores Prácticas

1. **Probar Sin Credenciales Primero**: Verifica que el acceso público a la API funcione antes de agregar credenciales
2. **Usar Límites de Tasa Conservadores**: Comienza con `enableRateLimit=True`
3. **Documentar Requisitos Especiales**: Agrega comentarios para exchanges con necesidades únicas
4. **Mantener Tipo de Mercado Consistente**: Usa "swap" para la mayoría de futuros perpetuos
5. **Validar en `is_likely_crypto()`**: Asegúrate de que el formato de mercado del nuevo exchange pase los filtros

---

## Ejemplo: Agregar Gate.io

```python
# 1. Agregar a SUPPORTED_EXCHANGES
SUPPORTED_EXCHANGES = ["binance", "bybit", "bingx", "okx", "bitget", "gateio"]

# 2. Agregar a CREDENTIALS_MAP
CREDENTIALS_MAP = {
    # ... existente ...
    "gateio": {"apiKey": "GATEIO_API_KEY", "secret": "GATEIO_API_SECRET"},
}

# 3. Agregar a EXCHANGE_TYPE_MAP
EXCHANGE_TYPE_MAP = {
    # ... existente ...
    "gateio": "swap",
}

# 4. Probar
EXCHANGE_CCXT=gateio python volume_sorted_coin_list.py
```

---

## Solución de Problemas

### El Exchange Usa Convención de Nombres Diferente

Algunos exchanges usan símbolos diferentes (ej. `BTC/USDT:USDT` en lugar de `BTC/USDT`).

**Solución:** Actualiza `is_likely_crypto()` en `volume_sorted_coin_list.py` si es necesario.

### El Exchange Tiene Spot y Futuros

Asegúrate de que el script solo obtenga futuros:

**Solución:** Verifica que la verificación `market.get('swap')` o `market.get('future')` esté en su lugar.

### El Exchange Requiere Versión Específica de API

**Solución:** Agrega configuración de versión:
```python
if exchange_id == "gateio":
    config["options"]["version"] = "2"
```

---

## Recursos Adicionales

- [Documentación CCXT](https://docs.ccxt.com/)
- [Lista de Exchanges CCXT](https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets)
- [Manual CCXT](https://github.com/ccxt/ccxt/wiki/Manual)

---

## Enlaces Relacionados

- [Guía de Normalización de Símbolos](SYMBOL_NORMALIZATION.es.md)
- [exchanges.py](../exchanges.py) - Módulo de configuración de exchanges
- [README.es.md](../README.es.md) - Documentación principal en español

---

**¿Preguntas?** Abre un issue en GitHub o contacta a @comgunner
