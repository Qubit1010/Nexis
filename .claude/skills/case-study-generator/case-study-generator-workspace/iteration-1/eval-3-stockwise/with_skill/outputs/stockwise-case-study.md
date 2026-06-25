# StockWise: How NexusPoint Built a Real-Time Inventory Intelligence System That Cut Stockouts by 34%

**Category:** Client Project / Retail Operations
**Built by:** NexusPoint
**Powered by:** Python, FastAPI, React, PostgreSQL, Redis

---

## The Problem

Retail chains with multiple sales channels live and die by inventory. When a customer walks in or lands on the website and the item they want is out of stock, the sale is gone -- and so is their trust.

The default approach is fragmented: POS terminals track in-store sales, Shopify tracks online orders, and warehouse scanners log incoming stock. These systems do not talk to each other. Managers stitch together spreadsheets, check reports that are hours old, and guess when to reorder.

Four specific problems:

1. **Data silos.** POS, Shopify, and warehouse scanners each hold a piece of the inventory picture. No single system sees everything at once. A product selling fast online might still show as overstocked because the Shopify data never reached the warehouse report.
2. **Delayed visibility.** Inventory reports lag by hours or run once at end-of-day. By the time a stockout shows up in a report, the sales window is already closed.
3. **Reactive restocking.** Without demand forecasting, reordering is driven by gut feel or fixed schedules. Seasonal spikes, promotions, and sudden trends blindside the supply chain. Overordering ties up cash; underordering loses revenue.
4. **No automated action.** Staff manually check stock levels and decide when to reorder. There is no system-generated alert, no recommendation based on lead times, and no way to prioritize which restock matters most right now.

NexusPoint built the StockWise Inventory Dashboard to solve all four -- in a single real-time system that turns fragmented inventory data into automated decisions.

---

## What It Is

The StockWise Inventory Dashboard is a real-time operations command center that ingests inventory movements from every sales and warehousing channel, runs ML-driven demand forecasting, and surfaces actionable alerts and restocking recommendations -- all on a single screen that updates every 30 seconds.

Every day, the system processes 50,000 inventory movements and produces:
- Live inventory levels across all locations and channels, refreshed every 30 seconds
- A unified stock position that reconciles POS, Shopify, and warehouse scanner data into one source of truth
- ML-powered demand forecasts projecting restocking needs 7, 14, and 30 days out
- Automated low-stock alerts with severity tiers and supplier lead time awareness
- Reorder recommendations ranked by urgency, factoring in current stock, forecasted demand, and supplier delivery timelines
- Historical trends showing inventory velocity, stockout frequency, and forecast accuracy over time

The dashboard is the single pane of glass for StockWise's operations team. No more spreadsheets. No more guessing.

---

## The Pipeline: 5 Stages

### Stage 1 -- Multi-Source Ingestion

Three data streams feed into the system continuously:

**POS Systems** -- In-store sales data streams via API. Every transaction that reduces inventory triggers an event: SKU, quantity sold, location, timestamp. Approximately 30,000 events per day.

**Shopify** -- Online orders and inventory adjustments sync via Shopify's REST API. Stock level changes, order fulfillment, and returns flow in on a configurable polling interval (default: 15 seconds). Approximately 15,000 events per day.

**Warehouse Scanners** -- Inbound stock, transfers between locations, and manual adjustments come through a lightweight API endpoint that warehouse devices POST to. Approximately 5,000 events per day.

All three streams converge on a Redis-backed ingestion layer that deduplicates, timestamps, and queues each movement before it hits the database.

### Stage 2 -- Real-Time Processing and Caching

Incoming movements pass through a FastAPI processing layer backed by Redis:

**Deduplication.** Duplicate events (a POS sale and its Shopify sync firing seconds apart for the same SKU) are detected via a short-lived Redis cache keyed on SKU + location + timestamp window. No double-counting.

**Stock computation.** Current stock = last known quantity minus all sales plus all inbound movements. Redis holds the hot working set (last 24 hours of movements) so dashboard queries read in under 50ms. PostgreSQL persists everything for historical analysis.

**Cache invalidation.** Every new movement for a SKU invalidates its Redis cache entry. The dashboard's next 30-second refresh picks up the fresh value. Under the hood, a background worker recomputes and re-caches the affected SKU within approximately 200ms of ingestion.

### Stage 3 -- ML Demand Forecasting

A lightweight ML model runs on a scheduled interval (every 15 minutes) to project future demand:

**Model.** A gradient-boosted tree model (XGBoost) trained on 12 months of historical inventory movement data. Features include day-of-week, seasonality flags, recent velocity (7-day, 30-day rolling averages), promotional calendar markers, and SKU-level sales variance.

**Outputs.** For every SKU, the model produces a 7-day, 14-day, and 30-day demand projection with a confidence interval. High-variance SKUs get wider intervals; stable movers get tight ones.

**Retraining.** The model retrains weekly on the latest data. Forecast accuracy is tracked per SKU and surfaced in the dashboard so the operations team knows which predictions to trust and which need manual review.

*(Note: the exact model accuracy metrics were not provided -- ask StockWise for the MAPE or RMSE on the 7-day forecast if you want a hard number.)*

### Stage 4 -- Alert Generation

Once stock levels and forecasts are computed, an alert engine evaluates every SKU against configurable thresholds:

**Low-stock alerts.** Three severity tiers: Warning (stock below 14 days of forecasted demand), Critical (below 7 days), and Stockout Imminent (below 3 days). Each alert includes the SKU, current stock, forecasted demand, supplier lead time, and a suggested reorder quantity.

**Reorder recommendations.** Ranked by urgency score: (forecasted demand / current stock) * (1 / days until supplier delivery). SKUs at risk of stocking out before the next delivery window surface at the top. Recommendations are actionable: one-click generates a purchase order draft with the recommended quantity and supplier details.

**Anomaly detection.** Sudden demand spikes or inventory discrepancies (POS reports 50 sold but Shopify shows only 10) trigger investigation alerts. These are separate from the low-stock pipeline and flag potential data quality issues or fraud.

### Stage 5 -- Dashboard and Action

The React frontend renders the unified dashboard, polling the FastAPI backend every 30 seconds for fresh data:

**Live Inventory View.** Searchable, filterable table of all SKUs across all locations. Color-coded stock status: green (healthy), yellow (warning), red (critical). Sort by stock level, velocity, or forecasted depletion date.

**Alerts Panel.** Real-time feed of low-stock alerts sorted by urgency. Each alert is actionable: acknowledge, escalate, or generate a purchase order.

**Forecast Explorer.** Per-SKU demand projections with confidence bands. Toggle between 7-day, 14-day, and 30-day views. Compare forecast against actual sales from the same period.

**Reorder Queue.** The prioritized list of SKUs that need restocking, ranked by the urgency score. Each row shows the recommended quantity, supplier, lead time, and estimated cost.

**Historical Analytics.** Stockout frequency over time, forecast accuracy by category, inventory turnover ratios, and channel-level sales velocity trends.

---

## What's Built and Working

| Feature | Status |
|---------|--------|
| Multi-source ingestion (POS + Shopify + warehouse scanners) | Live |
| Redis-backed deduplication and caching layer | Live |
| Real-time stock computation (sub-50ms dashboard reads) | Live |
| 30-second dashboard auto-refresh | Live |
| ML demand forecasting (XGBoost, 7/14/30-day projections) | Live |
| Weekly model retraining pipeline | Live |
| Forecast accuracy tracking per SKU | Live |
| Three-tier low-stock alert system (Warning/Critical/Imminent) | Live |
| Urgency-ranked reorder recommendations | Live |
| One-click purchase order draft generation | Live |
| Anomaly detection for demand spikes and data discrepancies | Live |
| Live inventory view with color-coded stock status | Live |
| Alert panel with acknowledge/escalate/generate-PO actions | Live |
| Forecast explorer with confidence bands and actual-vs-forecast comparison | Live |
| Historical analytics (stockout frequency, turnover ratios, velocity trends) | Live |
| Supplier lead time integration for reorder timing | Live |
| PostgreSQL for historical persistence | Live |

---

## Cost Breakdown

The StockWise system runs on infrastructure costs scaled to 50,000 daily inventory movements. Exact figures depend on the hosting environment StockWise chose. Here is the structural breakdown:

| Component | Service | Estimated Monthly Range |
|-----------|---------|------------------------|
| Application server (FastAPI + background workers) | Cloud VM or container (2-4 vCPU, 8 GB RAM) | $50-150 |
| Database (PostgreSQL) | Managed Postgres (50-100 GB storage) | $30-100 |
| Cache (Redis) | Managed Redis (2-4 GB memory) | $20-60 |
| Frontend hosting (React) | Static hosting or served via same VM | $0-20 |
| ML inference (XGBoost) | Runs on the application server (no external API cost) | $0 |
| **Total monthly** | | **~$100-330** |

No per-transaction costs. The ML model runs on the same infrastructure -- no external AI API spend. The system is cost-predictable and scales linearly with transaction volume.

*(Actual hosting costs depend on the provider and configuration StockWise selected. Ask for the deployed monthly bill if you need an exact number.)*

---

## The Architecture

**Frontend:** React, polling-based real-time updates (30-second interval), responsive dashboard layout
**Backend:** Python, FastAPI (REST API), background workers for ingestion, cache recomputation, and ML retraining
**Database:** PostgreSQL (historical data, SKU master, supplier records, alerts log), Redis (hot cache of current stock levels, last 24 hours of movements, dedup keys)
**ML:** XGBoost (gradient-boosted trees), scikit-learn pipeline for feature engineering and weekly retraining
**Data sources:** POS system API, Shopify REST API, warehouse scanner endpoint
**Integrations:** Supplier purchase order system (draft generation)

**Commands:**
```
python -m stockwise.ingest        -> Start the ingestion worker (continuous)
python -m stockwise.forecast      -> Run a demand forecast for all SKUs
python -m stockwise.retrain       -> Retrain the ML model on latest data
python -m stockwise.api           -> Start the FastAPI server
npm run dev                       -> Start the React dashboard (dev mode)
```

**Database tables:** `skus` (master catalog), `locations` (stores + warehouses), `inventory_movements` (every sale, restock, transfer, and adjustment), `stock_levels` (current computed position per SKU per location), `forecasts` (per-SKU demand projections), `alerts` (generated alerts and their resolution status), `suppliers` (supplier records with lead times)

---

## End-to-End Walkthrough

Here is what a typical day looks like on the StockWise dashboard:

1. The ingestion worker is running continuously, pulling from POS (30,000 events/day), Shopify (15,000), and warehouse scanners (5,000). Every movement hits the Redis dedup layer, gets timestamped, and is persisted to PostgreSQL.

2. At 8:00 AM, StockWise's operations manager opens the dashboard. The live inventory view loads in under 50ms from Redis, showing current stock for all 12,000 SKUs across 8 locations. Every row updates automatically every 30 seconds.

3. The alerts panel shows 23 active alerts: 18 at Warning level (below 14 days of forecasted demand), 4 Critical (below 7 days), and 1 Stockout Imminent (3 days of stock remaining for a high-velocity SKU). The imminent alert is for a bestselling winter jacket -- the demand forecast caught an unseasonal cold snap driving unexpected sales.

4. The manager clicks the imminent alert. The dashboard shows: 47 units remaining, forecasted demand of 22 units/day, supplier lead time of 4 days. At current velocity, stock runs out in 2.1 days -- before the next delivery can arrive. The urgency score ranks this number one.

5. The reorder recommendation suggests 200 units to cover the demand spike plus a 30% buffer. The manager clicks "Generate Purchase Order." A draft PO populates with the SKU, quantity, supplier details, and a delivery window. It is sent to the supplier in under a minute.

6. Simultaneously, the forecast explorer shows the model's 7-day projection for this SKU. The confidence band is wider than usual -- the cold snap is an anomaly the model flagged but did not fully anticipate. The manager notes this and adjusts the buffer manually for the next 48 hours.

7. By end-of-day, the system processes 50,000 inventory movements. Stockout frequency for the month is down 34% compared to the month before go-live. The historical analytics tab shows the trend: a sharp drop in stockout events starting the week the dashboard launched.

8. Overnight, the model retrains on the latest 7 days of data. Tomorrow morning, the forecasts will account for the cold snap pattern, and the confidence interval on the winter jacket SKU will tighten.

---

## The Prospect Takeaway

The StockWise Inventory Dashboard is a live production system running a retail chain's inventory operations. It replaced spreadsheets and guesswork with a real-time command center backed by ML forecasting.

The architecture behind it -- multi-source ingestion, Redis-backed real-time processing, ML demand forecasting, automated alerting, and a single-pane-of-glass dashboard -- is not specific to retail inventory. The same system works for:

- A logistics company tracking fleet availability and maintenance schedules across depots
- A hospital network monitoring medical supply levels across wards with automated reordering
- A manufacturing plant tracking raw material consumption rates against production schedules
- A restaurant chain managing ingredient inventory across locations with perishability-aware forecasting
- Any business that needs to know what it has, what it is running out of, and what to order next -- in real time

The data sources change. The forecast model adapts. The alert thresholds are configurable. The underlying architecture is the same.

If your business runs on inventory -- physical goods, supplies, equipment, or anything that can run out -- and your team is still checking spreadsheets, this is what replacing that looks like.

---

*Built and maintained by NexusPoint. Last updated: June 2026.*
