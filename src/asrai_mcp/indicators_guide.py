"""
Indicator interpretation guide for Asrai MCP.

Field names and descriptions sourced directly from Asrai API source code:
- alsat.py, superalsat_api.py, psar.py, macd_dema.py, alphatrend.py, td9.py
- aipromt_result_long_version.txt (official Asrai trading playbook)
- aipromt_for_api.txt (API endpoint reference)

Any AI agent using this MCP can call indicator_guide() to understand how to
read and act on the JSON returned by each Asrai tool.
"""
import json

GUIDE: dict = {

    # -----------------------------------------------------------------------
    # ALSAT  (al=buy, sat=sell in Turkish — cycle bottom/top detector)
    # Called by: technical_analysis() via /api/signal/ and /api/alsat/
    # -----------------------------------------------------------------------
    "ALSAT": {
        "what_it_is": (
            "ALSAT (Al-Sat) is Asrai's proprietary cycle bottom and top detector. "
            "Combines MavilimW (multi-layered WMA), Bollinger Bands, RSI, and Wave Trend "
            "to identify exact price exhaustion turning points — bottoms for buying, tops for selling. "
            "Also referred to as 'ASRAI signal' in documentation. "
            "'AL' = buy in Turkish, 'SAT' = sell in Turkish."
        ),
        "key_fields": {
            "action": "Current recommendation: BUY | SELL | HOLD",
            "signal_strength": "Signal conviction: STRONG | MEDIUM | WEAK",
            "confidence": "Confidence rating from underlying recommendation engine",
            "bars_since_buy": "Candles since last BUY signal. <5 = fresh active signal. >15 = stale, ignore",
            "bars_since_sell": "Candles since last SELL signal. <5 = fresh. >15 = stale",
            "profit_loss": "P&L % since signal fired (e.g. '+5.2%' = signal is working, '-2.1%' = failed)",
            "position_status": "Implied position: LONG | SHORT | NO_POSITION",
            "last_buy_date": "Timestamp of most recent BUY signal — compare to today to gauge freshness",
            "last_sell_date": "Timestamp of most recent SELL signal",
            "last_buy_price": "Price when last BUY fired — compare to current_price to see P&L",
            "last_sell_price": "Price when last SELL fired",
            "current_price": "Current market price",
            "rsi": "Current RSI value (0-100)",
            "market_condition": "OVERSOLD | NEUTRAL | OVERBOUGHT",
            "risk_level": "LOW | MEDIUM | HIGH",
            "pmax.value": "Current PMax line price level — key dynamic S/R",
            "pmax.trend": "UP (price above PMax = uptrend) | DOWN (price below = downtrend)",
            "pmax.distance_percentage": "How far price is from PMax line in %",
            "bollinger_bands.upper": "Upper BB band — potential resistance",
            "bollinger_bands.lower": "Lower BB band — potential support",
            "bollinger_bands.squeeze": "SQUEEZE = low volatility, big move imminent. EXPANDING = trending",
            "support_resistance.support": "Key support price level",
            "support_resistance.resistance": "Key resistance price level",
        },
        "how_to_interpret": (
            "1. action + signal_strength first: STRONG BUY = highest conviction entry. "
            "2. bars_since_buy < 5 = fresh active signal, good entry window. >15 = already played out. "
            "3. profit_loss positive = signal is working (confirm trend). Negative = signal failed. "
            "4. pmax.trend UP = price in uptrend, PMax is trailing support — hold above it. "
            "5. STRONG BUY + bars_since_buy < 5 + profit_loss positive + pmax.trend UP = A+ long setup."
        ),
    },

    # -----------------------------------------------------------------------
    # SuperALSAT  (ALSAT Daily + AlphaTrend 4H dual confirmation)
    # Called by: technical_analysis() via /api/superalsat/
    # -----------------------------------------------------------------------
    "SuperALSAT": {
        "what_it_is": (
            "SuperALSAT is the strongest confirmation signal in Asrai's toolkit. "
            "Fires only when ALSAT (daily timeframe) BUY + AlphaTrend (4H) both agree simultaneously. "
            "Requires two independent timeframes to confirm — fewer signals, much higher reliability. "
            "SuperALSAT BUY = major confirmed cycle bottom. SELL = major confirmed cycle top."
        ),
        "key_fields": {
            "superalsat_status": "Overall status: BUY_NOW | SELL_NOW | NEUTRAL | WATCHING",
            "current_position": "LONG_CONFIRMED | SHORT_CONFIRMED | NEUTRAL",
            "signal_quality": "Signal quality: HIGH | MEDIUM | LOW",
            "confirmation_strength": "How strongly both components agree",
            "buy_signal.date": "Timestamp when SuperALSAT BUY confirmation fired",
            "buy_signal.price": "Price when SuperALSAT BUY fired",
            "buy_signal.age_days": "Days since BUY fired. <7 = very fresh. >30 = stale",
            "buy_signal.confirmed": "true = active BUY signal exists",
            "sell_signal.date": "Timestamp when SuperALSAT SELL fired",
            "sell_signal.price": "Price at SELL signal",
            "sell_signal.age_days": "Days since SELL fired. <7 = fresh. >30 = stale",
            "component_signals.alsat.bars_since_buy": "ALSAT candles since buy — freshness of underlying signal",
            "component_signals.alphatrend.trend_status": "AlphaTrend current trend: BULLISH | BEARISH",
            "entry_strategy": "Suggested entry approach based on signal combination",
            "risk_level": "LOW | MEDIUM | HIGH",
        },
        "how_to_interpret": (
            "BUY_NOW + age_days < 7 = highest-conviction bottom, strong case to enter long. "
            "SELL_NOW = major top, exit longs immediately or consider short. "
            "WATCHING = one component agrees, wait for second to confirm. "
            "SuperALSAT BUY + ALSAT BUY both active = elite setup, maximum conviction. "
            "age_days > 30 = stale, treat as historical context only, not entry trigger."
        ),
    },

    # -----------------------------------------------------------------------
    # AlphaTrend  (dynamic trend line using ATR + MFI/RSI)
    # Called by: technical_analysis() via /api/alphatrend/
    # -----------------------------------------------------------------------
    "AlphaTrend": {
        "what_it_is": (
            "AlphaTrend is a dynamic support/resistance trend line that adapts to volatility using ATR. "
            "Uses MFI (Money Flow Index) when volume data is available, RSI otherwise. "
            "Hugs price tightly in strong trends — smarter and faster than a standard EMA. "
            "The 4H AlphaTrend is the confirmation layer in SuperALSAT."
        ),
        "key_fields": {
            "last_buy_date": "Timestamp of last AlphaTrend BUY crossover signal",
            "last_sell_date": "Timestamp of last AlphaTrend SELL crossover signal",
            "last_buy_price": "Price when last BUY crossover occurred",
            "last_sell_price": "Price when last SELL crossover occurred",
            "trend_status": "Current trend: BULLISH | BEARISH",
            "trend_strength": "Trend strength rating",
            "alphatrend_value": "Current line price level (= support in uptrend, resistance in downtrend)",
        },
        "how_to_interpret": (
            "BULLISH = price above AlphaTrend line — buy dips toward alphatrend_value. "
            "BEARISH = price below line — line is resistance, avoid longs. "
            "Fresh BUY crossover (recent last_buy_date) = early bullish trend signal. "
            "4H AlphaTrend BULLISH + daily ALSAT BUY = SuperALSAT confirmed — maximum conviction entry."
        ),
    },

    # -----------------------------------------------------------------------
    # PMax  (Pivot Max — dynamic S/R + trend identifier)
    # Appears inside ALSAT response as pmax section
    # -----------------------------------------------------------------------
    "PMax": {
        "what_it_is": (
            "PMax (Pivot Max) combines ATR trailing stop with a moving average "
            "to create a dynamic support/resistance line that also identifies trend direction. "
            "Price above PMax = uptrend (PMax = trailing support). "
            "Price below PMax = downtrend (PMax = resistance). "
            "Close above PMax = trend flip bullish. Close below = trend flip bearish."
        ),
        "key_fields": {
            "pmax.value": "Current PMax line price — the key S/R level to watch",
            "pmax.trend": "UP = price above PMax (uptrend). DOWN = price below (downtrend). UNKNOWN = computing",
            "pmax.distance_percentage": "Distance from current price to PMax in %. Large % = extended from trend",
        },
        "how_to_interpret": (
            "trend UP: PMax is your trailing stop-loss for longs — hold above it. "
            "trend DOWN: PMax is resistance, do not buy until price closes above it. "
            "Fresh cross above PMax = trend flip bullish, potential entry. "
            "Fresh cross below PMax = trend flip bearish, exit. "
            "ALSAT STRONG BUY + pmax.trend UP = A+ long setup."
        ),
    },

    # -----------------------------------------------------------------------
    # MavilimW  (multi-layered WMA — core of ALSAT engine)
    # -----------------------------------------------------------------------
    "MavilimW": {
        "what_it_is": (
            "MavilimW is a 6-layer weighted moving average (WMA of WMA of WMA...) — "
            "the smoothed trend filter powering the ALSAT algorithm. "
            "Much smoother than a standard EMA, catches trends earlier. "
            "Acts as dynamic support in uptrends and resistance in downtrends."
        ),
        "key_fields": {
            "mavw_value": "Current MavilimW line price level",
        },
        "how_to_interpret": (
            "Price above MavilimW = bullish. Below = bearish. "
            "Price crossing above MavilimW + PMax simultaneously = strong buy confirmation. "
            "ALSAT uses MavilimW internally: price must be above MAVW for BUY signals, below for SELL."
        ),
    },

    # -----------------------------------------------------------------------
    # TD9  (Tom DeMark Sequential — exhaustion counter)
    # Called by: technical_analysis() via /api/td/
    # -----------------------------------------------------------------------
    "TD9": {
        "what_it_is": (
            "Tom DeMark Sequential counts 9 consecutive closes in one direction. "
            "At count 9, the move is likely exhausted and a reversal is near. "
            "TD9 BUY = 9 consecutive lower closes = sellers exhausted, bounce expected. "
            "TD9 SELL = 9 consecutive higher closes = buyers exhausted, pullback expected. "
            "Works best in extended trending moves, not choppy markets."
        ),
        "key_fields": {
            "last_buy_date": "Timestamp of last TD9 BUY signal (9 lower closes completed)",
            "last_sell_date": "Timestamp of last TD9 SELL (9 higher closes completed)",
            "last_buy_price": "Price when TD9 BUY completed",
            "last_sell_price": "Price when TD9 SELL completed",
            "last_buy_rsi": "RSI at time of BUY — low RSI + TD9 BUY = very high conviction",
            "last_sell_rsi": "RSI at time of SELL — high RSI + TD9 SELL = very high conviction",
        },
        "how_to_interpret": (
            "Freshness: compare last_buy_date to today. < 5 days = fresh reversal zone. >15 days = played out. "
            "TD9 BUY + ALSAT BUY together = elite bottom signal, sellers truly exhausted. "
            "TD9 SELL + ALSAT SELL together = confirmed top. "
            "TD9 is reversal only — works at extremes, combine with RSI oversold/overbought for confirmation."
        ),
    },

    # -----------------------------------------------------------------------
    # PSAR  (Parabolic SAR — trailing stop & trend direction)
    # Called by: technical_analysis() via /api/psar/
    # -----------------------------------------------------------------------
    "PSAR": {
        "what_it_is": (
            "Parabolic SAR (Stop And Reverse) — a trailing stop that follows price. "
            "Dots below price = UPTREND (bullish). Dots above price = DOWNTREND (bearish). "
            "A PSAR flip (dots switch sides) = trend reversal signal. "
            "PSAR value = exact dynamic stop-loss level for active positions."
        ),
        "key_fields": {
            "parabolic_sar.psar_value": "Current PSAR price level — use as stop-loss",
            "parabolic_sar.direction": "UPTREND (bullish, dots below price) | DOWNTREND (bearish)",
            "parabolic_sar.distance_percent": "Distance from price to PSAR in % — large % = extended trend",
            "parabolic_sar.support_resistance.type": "SUPPORT (in uptrend) | RESISTANCE (in downtrend)",
            "signal.type": "BUY | SELL | HOLD",
            "signal.buy_signal_now": "true = PSAR just flipped bullish THIS candle — fresh reversal entry",
            "signal.sell_signal_now": "true = PSAR just flipped bearish — exit longs now",
            "recent_opportunities[].bars_ago": "Candles since signal. 1-3 = still in entry window",
            "recent_opportunities[].price_change": "P&L % since that signal fired",
            "trading_advice.confidence": "0-100 confidence in current signal",
            "trading_advice.trend": "BULLISH | BEARISH",
        },
        "how_to_interpret": (
            "UPTREND: use psar_value as trailing stop-loss for longs. Exit if price closes below it. "
            "buy_signal_now = true: PSAR just flipped bullish — strong reversal entry signal. "
            "sell_signal_now = true: PSAR flipped bearish — exit longs immediately. "
            "bars_ago 1-3: still in early entry window, good risk/reward. "
            "PSAR flip + ALSAT BUY + TD9 BUY = highest-probability reversal combo."
        ),
    },

    # -----------------------------------------------------------------------
    # MACD-DEMA  (MACD with Double EMA — faster momentum indicator)
    # Called by: technical_analysis() via /api/macd-dema/
    # -----------------------------------------------------------------------
    "MACD_DEMA": {
        "what_it_is": (
            "MACD using Double Exponential Moving Averages (DEMA) instead of standard EMA. "
            "DEMA is faster — catches momentum shifts earlier than standard MACD. "
            "Histogram above 0 = bullish momentum. Below 0 = bearish. "
            "Key entry: histogram crossing zero line 1-3 bars ago = early entry opportunity. "
            "Asrai playbook: 'Buy when histogram crosses above zero, sell when crosses below.'"
        ),
        "key_fields": {
            "macd_dema.histogram": "Current value. Positive = bullish momentum. Negative = bearish",
            "macd_dema.color": "GREEN (histogram > 0) | RED (histogram < 0)",
            "macd_dema.strength": "STRONG | MEDIUM | WEAK",
            "macd_dema.macd_line": "MACD line value",
            "macd_dema.signal_line": "Signal line value",
            "signal.type": "BUY | SELL | HOLD",
            "signal.crossed_just_now": "true = histogram crossed zero THIS candle — fresh signal!",
            "recent_opportunities[].bars_ago": "Candles since cross. 1-3 = still in early entry window",
            "recent_opportunities[].momentum": "CONTINUING | WEAKENING — momentum building or fading?",
            "trading_advice.confidence": "0-100 confidence",
            "trading_advice.priority": "HIGH | MEDIUM | LOW",
        },
        "how_to_interpret": (
            "histogram > 0 growing: strong bullish momentum, hold or add longs. "
            "crossed_just_now = true: momentum just flipped — best timing window for entry. "
            "bars_ago 1-3: still early entry window, good risk/reward. "
            "momentum WEAKENING: histogram positive but shrinking — tighten stops, trend may be ending. "
            "MACD-DEMA GREEN + ALSAT BUY + PSAR UPTREND = elite long entry combo."
        ),
    },

    # -----------------------------------------------------------------------
    # SMC  (Smart Money Concepts)
    # Called by: smart_money() via /api/smartmoney/
    # -----------------------------------------------------------------------
    "SMC": {
        "what_it_is": (
            "Smart Money Concepts (SMC) tracks institutional order flow and price structure. "
            "Based on ICT methodology. Identifies where large traders placed orders "
            "and where price is likely to move next."
        ),
        "key_fields": {
            "CHoCH": "Change of Character — trend reversed. Bullish CHoCH = uptrend started. Bearish = downtrend",
            "BOS": "Break of Structure — trend continuation confirmed in current direction",
            "FVG": "Fair Value Gap — price imbalance zone that price returns to fill (strong entry area)",
            "FVG.top / FVG.bottom": "FVG zone boundaries — buy at bottom of bullish FVG",
            "OB.bullish": "Bullish Order Block = institutional buy zone, strong support — buy on touch",
            "OB.bearish": "Bearish Order Block = institutional sell zone, strong resistance",
            "EQH": "Equal Highs — liquidity pool above price, likely swept before reversal down",
            "EQL": "Equal Lows — liquidity pool below price, likely swept before bounce up",
        },
        "how_to_interpret": (
            "Bullish CHoCH = trend just reversed bullish, new uptrend confirmed — go long. "
            "BOS in uptrend = trend continuing — hold longs, add on dips. "
            "FVG below current price = strong dip-buy zone, price will likely return to fill it. "
            "Bullish OB = best support level, buy on touch with stop just below OB. "
            "EQH above price = liquidity sweep target — price may spike up to sweep before reversing. "
            "EQL below price = smart money may push price down to grab liquidity before bouncing."
        ),
    },

    # -----------------------------------------------------------------------
    # Elliott Wave
    # Called by: elliott_wave() via /api/ew/
    # -----------------------------------------------------------------------
    "Elliott_Wave": {
        "what_it_is": (
            "Elliott Wave Theory: price moves in a 5-wave impulse (trend direction) "
            "followed by a 3-wave ABC correction. Wave 3 is longest/strongest. "
            "Wave 5 ends the trend. ABC corrects back. "
            "Identifies current wave position and what comes next."
        ),
        "key_fields": {
            "current_wave": "Wave number: 1-5 (impulse) or A, B, C (correction)",
            "wave_type": "IMPULSE | CORRECTION",
            "wave_target": "Price target for current wave completion",
            "fib_levels": "Key Fibonacci levels: 23.6%, 38.2%, 50%, 61.8%, 76.4%",
            "market_sentiment": "BULLISH | BEARISH based on wave position",
        },
        "how_to_interpret": (
            "Wave 1 = trend just started, early but risky. "
            "Wave 2 = corrective pullback = best dip-buy opportunity (deepest correction). "
            "Wave 3 = strongest/longest move, best risk/reward. Enter here. "
            "Wave 4 = secondary corrective pullback, shallower than wave 2. "
            "Wave 5 = final impulse, trend near end — reduce size, tighten stops. "
            "Wave A/B/C = full correction, wait before adding longs. "
            "Wave C end = excellent entry for new impulse."
        ),
    },

    # -----------------------------------------------------------------------
    # Ichimoku Cloud
    # Called by: ichimoku() via /api/ichimoku/
    # -----------------------------------------------------------------------
    "Ichimoku": {
        "what_it_is": (
            "Ichimoku Kinko Hyo — all-in-one trend, momentum, and support/resistance system. "
            "Cloud (Kumo) = main S/R zone. Tenkan (9-period) = fast signal line. "
            "Kijun (26-period) = slow signal line. Green cloud = bullish. Red = bearish. "
            "From Asrai playbook: price above cloud = bullish. Below = bearish. Inside = neutral."
        ),
        "key_fields": {
            "cloud_top": "Top of Kumo cloud — resistance below, support target above",
            "cloud_bottom": "Bottom of Kumo cloud — key support in uptrend",
            "cloud_color": "GREEN (Lead1 > Lead2, bullish) | RED (bearish)",
            "price_vs_cloud": "ABOVE (bullish) | BELOW (bearish) | INSIDE (neutral/indecision)",
            "trend": "BULLISH | BEARISH | NEUTRAL",
            "tenkan": "Short-term signal line value",
            "kijun": "Medium-term signal line value",
            "tenkan_kijun_cross": "BULLISH_CROSS (tenkan above kijun) | BEARISH_CROSS | NEUTRAL",
        },
        "how_to_interpret": (
            "Price ABOVE GREEN cloud = strong uptrend. Buy dips toward cloud_top. "
            "Price BELOW RED cloud = strong downtrend. Avoid longs. "
            "Price INSIDE cloud = indecision, wait for breakout. "
            "Thick cloud ahead = strong S/R barrier. Thin cloud = weak, price can break through. "
            "Bullish Tenkan/Kijun cross above cloud = strong entry signal. "
            "Price above cloud + PMax UP + ALSAT BUY = full triple trend confirmation."
        ),
    },

    # -----------------------------------------------------------------------
    # Bollinger Bands
    # Appears inside ALSAT response as bollinger_bands section
    # -----------------------------------------------------------------------
    "Bollinger_Bands": {
        "what_it_is": (
            "20-period SMA ± 2 standard deviations. "
            "Bands expand in high volatility, contract in low volatility. "
            "Lower band = potential buy zone. Upper band = potential sell zone. "
            "BB Squeeze (narrow bands) = big move incoming. ALSAT uses BB to confirm cycle turns."
        ),
        "key_fields": {
            "bollinger_bands.upper": "Upper band — potential resistance/overbought zone",
            "bollinger_bands.middle": "Middle band (20-SMA) — dynamic mean, price reverts to it",
            "bollinger_bands.lower": "Lower band — potential support/oversold zone",
            "bollinger_bands.squeeze": "SQUEEZE = breakout imminent. EXPANDING = trending market",
        },
        "how_to_interpret": (
            "Price at lower band + RSI < 30 + ALSAT BUY = high-conviction bottom — buy. "
            "Price at upper band + RSI > 70 + ALSAT SELL = overbought top — exit/sell. "
            "SQUEEZE: direction breakout coming — watch ALSAT for which direction. "
            "Middle band = mean reversion target after extremes. "
            "Price piercing lower band + bouncing back inside = classic buy signal (used by ALSAT internally)."
        ),
    },

    # -----------------------------------------------------------------------
    # RSI  (Relative Strength Index)
    # -----------------------------------------------------------------------
    "RSI": {
        "what_it_is": (
            "Relative Strength Index 0-100. Measures momentum and overbought/oversold conditions. "
            "Standard: < 30 = oversold, > 70 = overbought. "
            "Asrai's ALSAT internally uses 40 (buy zone) and 60 (sell zone) as thresholds."
        ),
        "key_fields": {
            "rsi": "Current RSI value (inside ALSAT response)",
            "market_condition": "OVERSOLD (≤30) | OVERBOUGHT (≥70) | NEUTRAL",
            "last_buy_rsi": "RSI at last BUY signal — lower = higher conviction",
            "last_sell_rsi": "RSI at last SELL signal — higher = higher conviction",
        },
        "how_to_interpret": (
            "RSI < 30: oversold — look for ALSAT BUY to confirm reversal. "
            "RSI > 70: overbought — look for ALSAT SELL to confirm top. "
            "RSI holding > 50 in uptrend = trend strength confirmed, continue holding longs. "
            "Bullish divergence (price lower low, RSI higher low) = warning of incoming reversal up. "
            "Bearish divergence (price higher high, RSI lower high) = topping warning."
        ),
    },

    # -----------------------------------------------------------------------
    # CBBI  (Crypto Bull Bear Index)
    # Called by: sentiment() via /api/cbbi/
    # -----------------------------------------------------------------------
    "CBBI": {
        "what_it_is": (
            "Crypto Bull Bear Index — Bitcoin market cycle position. Scale 0-100. "
            "Combines 9 on-chain metrics (NUPL, RHODL, Puell Multiple, etc.) "
            "to identify where we are in the Bitcoin macro cycle. "
            "A macro context tool, not a short-term entry signal."
        ),
        "key_fields": {
            "value": "0-100 cycle score",
        },
        "thresholds": {
            "0-10": "Deep cycle bottom — maximum accumulation zone. Historic lows",
            "10-25": "Early recovery — strong accumulation phase",
            "25-50": "Early-mid bull market",
            "50-75": "Mid-to-late bull market — healthy uptrend",
            "75-90": "Late bull — reduce exposure, watch for exhaustion",
            "90-100": "Cycle top zone — very high risk, significant reduction recommended",
        },
        "how_to_interpret": (
            "CBBI > 90: near cycle top. Reduce position sizes significantly. "
            "CBBI < 10: cycle bottom. Best long-term accumulation window. "
            "CBBI 40-70: mid-cycle, normal DCA and position building. "
            "Use for macro context (weeks/months), not daily entries. "
            "High CBBI + ALSAT SELL = double top confirmation. Low CBBI + ALSAT BUY = double bottom."
        ),
    },

    # -----------------------------------------------------------------------
    # Forecast  (AI-powered 3-7 day price prediction)
    # Called by: forecast() via /api/forecasting/
    # -----------------------------------------------------------------------
    "Forecast": {
        "what_it_is": (
            "Asrai's AI Forecasting Engine — 3-7 day price predictions using "
            "multi-timeframe signal hierarchy. "
            "Priority: Reversal signals (ALSAT, TD9, MACD-DEMA, PSAR) > Trend signals. "
            "Daily weight 100%, 4H confirmation 30%. Confidence range: 24-85%."
        ),
        "key_fields": {
            "direction": "BULLISH | BEARISH | NEUTRAL",
            "confidence": "Confidence %. >70% = reliable. 50-70% = moderate. <50% = weak/uncertain",
            "primary_target": "Primary price target based on nearest S/R",
            "secondary_target": "Secondary target if primary is exceeded",
            "timeframe_estimate": "3-5 days (strong) | 4-7 days (medium) | 7-10 days (weak signals)",
        },
        "how_to_interpret": (
            "Confidence > 70% = actionable. Combine with ALSAT + PMax for entry timing. "
            "Confidence 50-70% = use as directional bias only. "
            "Confidence < 50% = weak, treat as context only. "
            "BULLISH + confidence > 70% + ALSAT BUY = high-conviction long setup."
        ),
    },

    # -----------------------------------------------------------------------
    # Market Overview Indicators
    # Called by: market_overview(), sentiment(), screener()
    # -----------------------------------------------------------------------
    "Market_Indicators": {
        "what_it_is": "Reference for indicators returned by market_overview, sentiment, and screener tools.",
        "indicators": {
            "trending": "Hot coins by search/social activity. Trending + ALSAT BUY = momentum play",
            "gainers_losers": "Top gaining/losing coins. Gainers with RSI < 70 = still room to run",
            "rsi_screener": "Coins with extreme RSI — oversold list = reversal candidates",
            "top_bottom": "Coins near tops or bottoms via multi-indicator detection",
            "sar_coins": "Recent PSAR flip signals — buy when PSAR crosses below price",
            "macd_coins": "MACD bullish crossovers — confirmed momentum entries",
            "emacross": "EMA 9/21 crossover. BUY when EMA9 > EMA21. EMA55 for extra confirmation",
            "techrating": "TradingView tech ratings. StrongBuy + volume > 5% = actionable",
            "vwap": "VWAP score. Below VWAP = undervalued. Above = overvalued",
            "galaxyscore": "LunarCrush Galaxy Score 0-100. >70 = strong social + on-chain signal",
            "socialdominance": "Social mention share. Rising = narrative building. Too high = euphoria",
            "cmc_sentiment": "CMC per-coin sentiment — bullish/bearish crowd reading",
            "highvolumelowcap": "High volume + small cap = early mover potential, higher risk",
            "bounce_dip": "Auto-detected dip-buy or bounce zones — best aligned with ALSAT BUY",
            "ath": "Coins near all-time highs — momentum continuation or blow-off top risk",
            "late_unlocked_coins": "Far-future vesting tokens — no near-term selling pressure, safer hold",
            "cmcai": "CMC AI insights — explains why market is up/down, narratives, institutional flow",
            "channel_summary": "Asrai's AI analysis of crypto narratives and on-chain flows across chains",
        },
    },

    # -----------------------------------------------------------------------
    # Support & Resistance
    # Called by: smart_money() via /api/support-resistance/
    # -----------------------------------------------------------------------
    "Support_Resistance": {
        "what_it_is": (
            "Key price levels from Fibonacci retracements, pivot points, "
            "EMA levels, and trendline analysis."
        ),
        "key_fields": {
            "latest_high_pivot": "Recent swing high — current resistance",
            "latest_low_pivot": "Recent swing low — current support",
            "fib_0_618": "0.618 Fib retracement — strongest bounce level",
            "fib_1_618": "1.618 extension — primary profit target",
            "fib_2_618": "2.618 extension — extended profit target",
            "ema.ema21": "21-period EMA — short/medium trend line",
            "ema.ema55": "55-period EMA — medium trend",
            "ema.ema200": "200-period EMA — critical long-term trend defense",
            "trendline_breaks.current_support": "Active trendline support price",
            "trendline_breaks.current_resistance": "Active trendline resistance price",
        },
        "how_to_interpret": (
            "0.618 Fib = strongest bounce level. Buy dips to it in uptrend with ALSAT confirmation. "
            "200 EMA = macro trend defense. Below 200 EMA = macro bearish, above = macro bullish. "
            "21 weekly EMA = long-term accumulation zone in bull markets. "
            "Trendline support break = bearish. Resistance break = bullish breakout. "
            "Best entries: 0.618 Fib + EMA confluence + ALSAT BUY = maximum conviction setup."
        ),
    },
}


# Compact one-liner summary for each indicator — used by the "list" mode (~400 tokens total)
SUMMARY: dict = {
    "ALSAT": "Asrai's cycle bottom/top detector. Fields: action, signal_strength, bars_since_buy, profit_loss, pmax.trend, rsi",
    "SuperALSAT": "ALSAT(1D) + AlphaTrend(4H) dual confirmation. Fields: superalsat_status, buy_signal.age_days, current_position",
    "AlphaTrend": "Dynamic trend line (ATR-based). Fields: trend_status, alphatrend_value, last_buy_date",
    "PMax": "Dynamic S/R + trend identifier. Fields: pmax.value, pmax.trend (UP=uptrend/support, DOWN=resistance)",
    "MavilimW": "6-layer WMA — core of ALSAT engine. Dynamic support/resistance",
    "TD9": "Tom DeMark exhaustion counter (9 consecutive closes). Fields: last_buy_date, last_sell_date, last_buy_rsi",
    "PSAR": "Trailing stop + trend. Fields: parabolic_sar.direction, psar_value, signal.buy_signal_now, recent_opportunities[].bars_ago",
    "MACD_DEMA": "Faster MACD using DEMA. Fields: macd_dema.histogram, macd_dema.color, signal.crossed_just_now, recent_opportunities[].bars_ago",
    "SMC": "Smart Money Concepts — institutional order flow. Fields: CHoCH, BOS, FVG, OB.bullish, EQH, EQL",
    "Elliott_Wave": "5-wave impulse + 3-wave ABC correction. Fields: current_wave, wave_type, wave_target",
    "Ichimoku": "All-in-one trend system. Fields: price_vs_cloud, cloud_color, tenkan_kijun_cross, trend",
    "Bollinger_Bands": "Volatility bands. Fields: bollinger_bands.upper/lower/middle, squeeze",
    "RSI": "Momentum 0-100. <30=oversold, >70=overbought. In ALSAT response as rsi + market_condition",
    "CBBI": "Bitcoin cycle position 0-100. <10=bottom, >90=top. From sentiment() tool",
    "Forecast": "AI 3-7 day prediction. Fields: direction, confidence (>70%=reliable), primary_target",
    "Market_Indicators": "trending, gainers_losers, rsi_screener, sar_coins, macd_coins, emacross, techrating, vwap, galaxyscore, bounce_dip, cmcai",
    "Support_Resistance": "Key levels. Fields: fib_0_618, ema.ema200, latest_high_pivot, trendline_breaks.current_support",
}


async def indicator_guide(indicator: str = "") -> str:
    """
    Return the interpretation guide for Asrai indicators.
    FREE — no x402 payment required.

    indicator = ""       → compact list of all indicators with 1-line summaries (~400 tokens)
    indicator = "list"   → same compact list
    indicator = "ALSAT"  → full detailed guide for that specific indicator (~400-640 tokens)
    indicator = "all"    → full guide for ALL indicators (~5800 tokens, use sparingly)
    """
    if not indicator or indicator.lower() == "list":
        # Default: compact summary list — cheapest, enough to decide which to look up
        return json.dumps({
            "usage": "Call indicator_guide('<name>') for full details on any indicator.",
            "indicators": SUMMARY,
        }, indent=2)

    if indicator.lower() == "all":
        # Full guide — only use when you need comprehensive detail on everything
        return json.dumps(GUIDE, indent=2)

    # Look up a specific indicator
    key = next((k for k in GUIDE if k.lower() == indicator.lower()), None)
    if not key:
        key = next((k for k in GUIDE if k.lower().startswith(indicator.lower())), None)
    if not key:
        key = next((k for k in GUIDE if indicator.lower() in k.lower()), None)
    if key:
        return json.dumps({key: GUIDE[key]}, indent=2)

    return json.dumps({
        "error": f"Indicator '{indicator}' not found.",
        "available": list(GUIDE.keys()),
    })
