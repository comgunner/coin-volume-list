# 📊 Generador de Lista de Coins Ordenadas por Volumen

**Autor:** @comgunner  
**Versión:** v0.0.1  
**Licencia:** Licencia de Atribución (ver [LICENSE](LICENSE))

> **💡 ¿Qué es esto?** Este script te ayuda a obtener **monedas activas en mercados de futuros/spot** de manera sencilla. Si quieres saber qué monedas están activas en un exchange en un momento determinado, esta herramienta obtiene los datos automáticamente y genera una lista clasificada por volumen de trading.

**Descarga Rápida:** [📦 Descargar Release v0.0.1 (ZIP)](https://github.com/comgunner/coin-volume-list/releases/download/v0.0.1/coin-volume-list-v0.0.1.zip)

Generador de listas de criptomonedas que obtiene pares de trading activos de múltiples exchanges usando **CCXT** y genera listas ordenadas por **volumen de trading de 24 horas**.

---

## 🚀 Características

- ✅ **Soporte Multi-Exchange:** Binance, Bybit, BingX, OKX, Bitget
- ✅ **Clasificación por Volumen:** Ordenado por volumen de 24h en USDT
- ✅ **Filtrado Inteligente:**
  - Exclusión automática de activos no-cripto (Forex, Materias Primas, Índices)
  - Soporte para lista de exclusión manual (`exclude_coins.txt`)
  - Solo contratos lineales USDT
  - Filtro de mercados activos
- ✅ **Gestión de Rate Limits:** Integrado vía CCXT
- ✅ **Salida JSON:** Datos estructurados con metadatos
- ✅ **Soporte de Zona Horaria:** América/México (CDMX)
- ✅ **Ejecución Flexible:** Un exchange o todos a la vez

---

## 📋 Requisitos

- Python 3.8+
- Librería CCXT
- Variables de entorno configuradas

---

## 🛠️ Instalación

### 1. Clonar o Descargar

```bash
cd coin-volume-list
```

### 2. Configurar Entorno Virtual

#### Linux / macOS

```bash
# Crear entorno virtual
python3.12 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Verificar versión de Python
python -V

# Actualizar pip
python -m pip install -U pip
```

#### Windows (10/11)

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate

# Verificar versión de Python
python -V

# Actualizar pip
python -m pip install -U pip
```

### 3. Instalar Dependencias

```bash
# Actualizar pip y setuptools
pip install --upgrade pip setuptools

# Instalar requirements
pip install -r requirements.txt
```

**Dependencias:**
- `ccxt>=4.4.0` - Librería de exchanges de criptomonedas
- `python-dotenv>=1.0.0` - Gestión de variables de entorno
- `pytz>=2024.1` - Soporte de zona horaria

### 4. Configurar Entorno

```bash
# Copiar configuración de ejemplo
cp .env.example .env

# Editar con tu configuración
# Linux/macOS: Usar nano, vim o cualquier editor
nano .env

# Windows: Usar Notepad o cualquier editor
notepad .env
```

**Configuración .env:**

```bash
# Selección de exchange (binance, bybit, bingx, okx, bitget)
EXCHANGE_CCXT=binance

# Opcional: Credenciales de API para límites más altos
BINANCE_API_KEY=tu_api_key
BINANCE_API_SECRET=tu_secret
```

---

## 📖 Uso

### Un Solo Exchange (desde .env)

```bash
# Salida JSON por defecto
python3 volume_sorted_coin_list.py

# Lista simple de símbolos (formato TOON/TXN - uno por línea)
python3 volume_sorted_coin_list.py --output-format toon
python3 volume_sorted_coin_list.py --output-format txn

# Lista separada por comas (formato CSV)
python3 volume_sorted_coin_list.py --output-format csv
```

### Todos los Exchanges a la Vez

```bash
# Salida JSON por defecto
python3 volume_sorted_coin_list.py --all-exchanges

# Lista simple de símbolos (formato TOON/TXN - uno por línea)
python3 volume_sorted_coin_list.py --all-exchanges --output-format toon
python3 volume_sorted_coin_list.py --all-exchanges --output-format txn

# Lista separada por comas (formato CSV)
python3 volume_sorted_coin_list.py --all-exchanges --output-format csv
```

### Opciones de Línea de Comandos

```bash
# Mostrar ayuda
python3 volume_sorted_coin_list.py --help

# Generar para todos los exchanges (formato JSON - por defecto)
python3 volume_sorted_coin_list.py --all-exchanges

# Generar para todos los exchanges (formato TOON - solo lista de símbolos)
python3 volume_sorted_coin_list.py --all-exchanges --output-format toon

# Generar para todos los exchanges (formato TXN - igual que TOON)
python3 volume_sorted_coin_list.py --all-exchanges --output-format txn

# Generar para todos los exchanges (formato CSV - separado por comas)
python3 volume_sorted_coin_list.py --all-exchanges --output-format csv

# Generar para todos los exchanges (formato ALL - generar todos a la vez)
python3 volume_sorted_coin_list.py --all-exchanges --output-format all

# Un exchange con formato JSON (por defecto)
python3 volume_sorted_coin_list.py --output-format json

# Un exchange con formato TOON o TXN (lista simple)
python3 volume_sorted_coin_list.py --output-format toon
python3 volume_sorted_coin_list.py --output-format txn

# Un exchange con formato CSV (separado por comas)
python3 volume_sorted_coin_list.py --output-format csv

# Un exchange con TODOS los formatos (generar todos a la vez)
python3 volume_sorted_coin_list.py --output-format all
```

### Opciones de Formato de Salida

| Formato | Flag | Descripción | Extensión | Ejemplo |
|---------|------|-------------|-----------|---------|
| **JSON** | `--output-format json` | Metadatos completos con símbolos, volúmenes y rankings (por defecto) | `.json` | `{"symbols": [...]}` |
| **TOON** | `--output-format toon` | Token-Oriented Object Notation - Datos completos (rank, símbolo, volumen) | `.toon` | `#1 BTCUSDT - $1,234,567.89` |
| **TXN** | `--output-format txn` | Token-Oriented Object Notation (alias) - Igual que TOON | `.toon` | `#1 BTCUSDT - $1,234,567.89` |
| **CSV** | `--output-format csv` | Comma-Separated Values - Símbolos ordenados por volumen | `.csv` | `BTCUSDT,ETHUSDT,SOLUSDT` |
| **TXT** | `--output-format txt` | Text file - Lista separada por comas (igual que CSV) | `.txt` | `BTCUSDT,ETHUSDT,SOLUSDT` |
| **ALL** | `--output-format all` | Genera TODOS los formatos a la vez (JSON + TOON + CSV + TXT) | Múltiple | Todos los anteriores |

---

## 📁 Salida

Los archivos generados se almacenan en el directorio `output/`:

### Formato JSON (Por Defecto)

```
output/
├── binance_active_coins_list.json
├── bybit_active_coins_list.json
├── bingx_active_coins_list.json
├── okx_active_coins_list.json
└── bitget_active_coins_list.json
```

### Formato CSV/TXT (Comma-Separated Values)

```
output/
├── binance_active_coins_list.csv
├── binance_active_coins_list.txt
├── bybit_active_coins_list.csv
├── bybit_active_coins_list.txt
├── bingx_active_coins_list.csv
├── bingx_active_coins_list.txt
├── okx_active_coins_list.csv
├── okx_active_coins_list.txt
├── bitget_active_coins_list.csv
└── bitget_active_coins_list.txt
```

**Ejemplo de contenido (ambos CSV y TXT):**
```
BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT,DOGEUSDT,ADAUSDT...
```

### Estructura JSON

```json
{
  "metadata": {
    "generated_at": "2026-03-29 12:00",
    "timezone": "America/Mexico_City",
    "update_frequency": "30M",
    "exchange": "BINANCE",
    "volume_filter_active": false,
    "min_volume_usdt": null,
    "total_symbols": 150,
    "manually_excluded_count": 5
  },
  "symbols": [
    {
      "rank": 1,
      "symbol": "BTCUSDT",
      "volume_24h_usdt": 1234567890.50
    },
    {
      "rank": 2,
      "symbol": "ETHUSDT",
      "volume_24h_usdt": 987654321.25
    }
  ],
  "excluded_symbols": ["EXCLUDED1USDT", "EXCLUDED2USDT"]
}
```

### Formato TOON/TXN (Token-Oriented Object Notation)

```
#1 BTCUSDT - $1,234,567,890.50
#2 ETHUSDT - $987,654,321.25
#3 SOLUSDT - $456,789,012.75
#4 BNBUSDT - $234,567,890.00
#5 XRPUSDT - $123,456,789.50
```

---

## ⚙️ Configuración

### Filtro de Volumen

Edita `volume_sorted_coin_list.py` para habilitar el filtrado por volumen:

```python
USE_VOLUME_FILTER = True   # Habilitar filtro de volumen
MIN_VOLUME_USDT = 100000   # Volumen mínimo de 24h en USDT
```

### Lista de Exclusión Manual

Crea `exclude_coins.txt` en la raíz del proyecto:

```
BADCOINUSDT
SCAMCOINUSDT
LOWLIQUIDITYUSDT
```

Estos símbolos serán automáticamente excluidos de todas las listas generadas.

---

## 🔧 Exchanges Soportados

| Exchange | CCXT ID | Credenciales Requeridas |
|----------|---------|------------------------|
| Binance | `binance` | Opcional (límites más altos) |
| Bybit | `bybit` | Opcional (límites más altos) |
| BingX | `bingx` | Opcional (límites más altos) |
| OKX | `okx` | Opcional (límites más altos) |
| Bitget | `bitget` | Opcional (límites más altos) |

---

## 🏗️ Arquitectura

### Componentes Clave

1. **Integración CCXT:** API unificada para múltiples exchanges
2. **Filtrado Inteligente:**
   - `is_likely_crypto()` - Filtra Forex, Materias Primas, Índices
   - Validación de tipo de contrato (solo linear/swap)
   - Filtro de moneda de cotización (solo USDT)
3. **Clasificación por Volumen:** Ordenado por volumen de 24h (descendente)
4. **Generador de Salida:** JSON con metadatos y rankings de símbolos

### Lógica de Filtrado

```
Todos los Mercados
    ↓
[Filtro] Solo Contratos/Derivados
    ↓
[Filtro] USDT Linear (quote=USDT)
    ↓
[Filtro] Mercados activos
    ↓
[Filtro] Activos cripto (no Forex/Materias Primas/Índices)
    ↓
[Filtro] Lista de exclusión manual
    ↓
[Ordenar] Por volumen 24h (descendente)
    ↓
Lista Final
```

---

## 🧪 Testing

```bash
# Probar con Binance (por defecto)
python3 volume_sorted_coin_list.py

# Probar con exchange específico
EXCHANGE_CCXT=bybit python3 volume_sorted_coin_list.py

# Probar todos los exchanges
python3 volume_sorted_coin_list.py --all-exchanges
```

---

## 📝 Ejemplos

### Ejemplo de Salida (Consola)

```
============================================================
🚀 Iniciando Generación Multi-Exchange de Lista de Coins
📅 2026-03-29 12:00
📛 Coins manualmente excluidas: 5
============================================================

============================================================
[INFO] Procesando exchange: BINANCE
[INFO] Archivo de salida: output/binance_active_coins_list.json
============================================================
[CCXT] Configurando cliente para: BINANCE...
[CCXT] Mercados cargados: 2500
[CCXT] Obteniendo tickers de 24h...
[CCXT] Procesados 180 mercados válidos (USDT/Linear/Activo).
♻️ Actualización de lista de coins (30M) 2026-03-29 12:00
📈 Filtro de volumen deshabilitado. Base: 180 símbolos.
🪙 Ejemplos: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT
🔍 Total de símbolos finales: 175
📛 Manualmente excluidos: 5
[OK] Lista generada: output/binance_active_coins_list.json (175 símbolos ordenados por volumen)
```

---

## 🔐 Notas de Seguridad

- Las credenciales de API se almacenan localmente en `.env` (no se commiten a Git)
- Las credenciales son opcionales - el acceso público de solo lectura funciona sin ellas
- Los rate limits son manejados automáticamente por CCXT
- No se registran ni almacenan datos sensibles en los archivos de salida

---

## 🤝 Contribuciones

Este es un **proyecto personal** de @comgunner. Para preguntas o solicitudes de colaboración, por favor contacta al autor.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia de Atribución** - ver el archivo [LICENSE](LICENSE) para más detalles.

**Requisitos Clave:**
- ✅ Libre uso para propósitos personales y comerciales
- ✅ Libre modificación y distribución
- ⚠️ **Debe dar el crédito apropiado al autor (@comgunner)**
- ⚠️ **Debe incluir una copia de la licencia**

---

## 📞 Soporte

- **GitHub:** [@comgunner](https://github.com/comgunner)
- **Repositorio:** https://github.com/comgunner/coin-volume-list

---

## 🙏 Agradecimientos

- **Equipo CCXT:** Por la excelente librería de exchanges de criptomonedas
- **APIs de Exchanges:** Binance, Bybit, BingX, OKX, Bitget por el acceso público a las APIs

---

*Última Actualización: 29 de Marzo, 2026*
