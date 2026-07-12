# TradingView Publication — ADX + VWAP + EMA

How to publish: open the script in the Pine Editor → **Publish script** (top-right) →
choose visibility (Private / Public) and access (Open-source / Protected / Invite-only) →
paste the title and description below → add tags → Publish.

Recommended settings for a first publication:
- **Visibility:** Private first (only people with the link see it), then republish Public once you're happy.
- **Access:** Open-source is approved fastest; Protected hides the code.
- **Tags:** `ADX`, `VWAP`, `EMA`, `trend-analysis`, `volume`

> House Rules note: public descriptions must explain what the script does and how
> to use it in enough detail that a trader can understand it without reading the
> code. The description below is written to satisfy that.

---

## Title

**ADX + VWAP + Triple EMA — Trend Strength Toolkit**

---

## Description (English)

This indicator combines three classic tools into a single script so you can judge
trend **strength**, **fair value**, and **direction** at a glance, plus optional
entry markers that only fire when all three agree.

**What it plots**

*ADX pane (below the chart):*
- ADX line (Wilder's smoothing) with DI+ and DI- shown as green/red columns.
- A threshold line (default 25). ADX above it = trending market; below = ranging.
- The zone under the threshold is shaded so choppy conditions are obvious.

*Main chart (force-overlay):*
- Anchored **VWAP** with up to three standard-deviation or percentage bands.
  Anchor options: Session, Week, Month, Quarter, Year, Decade, Century,
  Earnings, Dividends, Splits.
- **Three EMAs** (defaults 9, 21, 50), each with its own toggle, length and color.
- An **EMA Timeframe** input: leave empty to use the chart timeframe, or select a
  higher timeframe (e.g. 1H EMAs on a 5-minute chart). Higher-timeframe values are
  requested with lookahead off, so historical bars show what you would have seen live.
- An **ATR info table** showing the current ATR value and ATR-based high/low levels
  for stop placement.

**Buy / Sell markers (optional)**

A buy triangle prints only when *all* of these are true:
1. EMA 9 crosses above EMA 21 (momentum turn),
2. EMA 21 is above EMA 50 (aligned uptrend),
3. ADX is above the threshold (the move has strength),
4. DI+ is above DI- (bullish directional pressure),
5. price is above VWAP (buyers control the session) — this condition can be
   switched off in settings.

Sell signals are the exact mirror. Both have matching alert conditions, so you can
create TradingView alerts on "Buy" and "Sell" directly.

**How to use it**

- Use ADX first: no ADX strength, no trade — the shaded zone tells you to stand aside.
- Use VWAP as your intraday value anchor: longs are higher-probability above it.
- Use the EMA stack for direction and timing; the 50 EMA filters counter-trend crosses.
- ATR levels in the table suggest stop distance for the current volatility.

This script works on any symbol and timeframe. VWAP requires volume data from your
data vendor; on symbols without volume the script raises an error by design.

**Credits & originality:** ADX follows Wilder's original smoothing method. VWAP
banding follows TradingView's standard anchored-VWAP approach. The combination
logic (triple-EMA cross gated by ADX strength, DI direction and VWAP side, with a
selectable EMA timeframe) is what this script adds.

*This is a technical analysis tool, not financial advice. Always test on your own
markets and timeframes before trading with real money.*

---

## Description (العربية)

يجمع هذا المؤشر ثلاث أدوات كلاسيكية في سكربت واحد لتقييم **قوة الاتجاه**
و**القيمة العادلة** و**اتجاه السوق** بنظرة واحدة، مع إشارات دخول اختيارية
لا تظهر إلا عند توافق الأدوات الثلاث.

**ما يرسمه المؤشر**

*نافذة ADX (أسفل الشارت):*
- خط ADX بتنعيم وايلدر مع أعمدة خضراء/حمراء لـ DI+ و DI-.
- خط عتبة (الافتراضي 25): فوقه سوق ذو اتجاه، وتحته سوق عرضي.
- تظليل المنطقة تحت العتبة لتمييز فترات التذبذب بوضوح.

*الشارت الرئيسي:*
- **VWAP** مرساة مع حتى ثلاث حزم بالانحراف المعياري أو النسبة المئوية،
  وخيارات مرساة: جلسة، أسبوع، شهر، ربع سنة، سنة، وغيرها.
- **ثلاثة متوسطات EMA** (افتراضياً 9 و21 و50) لكل منها تفعيل وطول ولون مستقل.
- خيار **فريم EMA**: اتركه فارغاً لاستخدام فريم الشارت، أو اختر فريماً أعلى
  (مثلاً EMA الساعة على شارت 5 دقائق) بدون إعادة رسم تاريخي.
- **جدول ATR** يعرض قيمة ATR ومستويات عليا/سفلى لتحديد وقف الخسارة.

**إشارات الشراء والبيع (اختيارية)**

تظهر إشارة الشراء فقط عند تحقق كل الشروط التالية:
1. تقاطع EMA 9 فوق EMA 21،
2. EMA 21 فوق EMA 50 (اتجاه صاعد متوافق)،
3. ADX فوق العتبة (قوة في الحركة)،
4. DI+ فوق DI- (ضغط شرائي)،
5. السعر فوق VWAP (يمكن إيقاف هذا الشرط من الإعدادات).

إشارات البيع معاكسة تماماً، مع تنبيهات جاهزة يمكن تفعيلها من نافذة التنبيهات.

**طريقة الاستخدام**

- ابدأ بـ ADX: لا قوة في الاتجاه = لا صفقة.
- استخدم VWAP كمرجع للقيمة اليومية: الشراء فوقه أعلى احتمالاً.
- استخدم المتوسطات الثلاثة للاتجاه والتوقيت، وEMA 50 كمرشح ضد الصفقات العكسية.
- استخدم مستويات ATR في الجدول لتحديد مسافة وقف الخسارة حسب التذبذب الحالي.

*هذا المؤشر أداة تحليل فني وليس نصيحة استثمارية. اختبره على أسواقك وفرياتك
قبل التداول بأموال حقيقية.*
