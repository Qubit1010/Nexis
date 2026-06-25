# Case Study: StockWise Real-Time Inventory Intelligence Dashboard

**Client:** StockWise  
**Industry:** Retail (multi-location chain)  
**Project:** Real-Time Inventory Dashboard with Demand Forecasting  
**Tech Stack:** Python, FastAPI, React, PostgreSQL, Redis  
**Engagement Length:** 8 weeks  
**Built by:** NexusPoint

---

## The Problem

StockWise operates 23 retail locations across the Midwest, managing over 15,000 SKUs. Their inventory stack was fragmented across three systems: legacy on-premise POS terminals at each store, a Shopify storefront for online orders, and handheld warehouse scanners that fed a separate stock ledger. None of these systems talked to each other in real time.

The result was predictable: store managers discovered a stockout only when a customer reached for an empty shelf. Reorder decisions were based on gut feel and weekly CSV exports. The warehouse team had no visibility into what was selling online versus in-store. StockWise estimated they were losing $340,000 per year in missed sales from preventable stockouts alone, not counting the long-tail cost of customers who never came back.

When the COO reached out to NexusPoint, the brief was direct: "I need one screen that tells me what I have, where it is, and what I need to order -- right now, not yesterday."

---

## What We Built

NexusPoint designed and delivered a real-time inventory intelligence platform that unifies StockWise's three data sources into a single dashboard that refreshes every 30 seconds.

### Architecture

- **Data ingestion layer (Python + FastAPI):** Lightweight connectors pull inventory events from the POS systems, Shopify webhooks, and warehouse scanner APIs. Each movement -- a sale, a restock, a transfer, a return -- becomes an event in the pipeline.

- **Real-time event processing:** Redis handles the firehose of roughly 50,000 inventory movements per day. Rather than polling databases, the system processes events as they stream in, keeping the dashboard current within 30 seconds of any change.

- **Demand forecasting engine:** A lightweight ML model (gradient-boosted trees trained on 18 months of historical sales data) runs hourly, predicting demand per SKU per location for the next 7 days. The model factors in day-of-week patterns, seasonal trends, and promotional lift from StockWise's marketing calendar.

- **Frontend (React):** A single-page dashboard organized around three views: a live inventory heatmap across all locations, a prioritized low-stock alert feed with reorder recommendations, and a demand forecast explorer that store managers can drill into per SKU.

- **PostgreSQL:** The source of truth for historical inventory data, sales records, and forecast outputs. Redis sits in front as a caching and pub/sub layer for real-time state.

### Key Capabilities

| Capability | Detail |
|---|---|
| Real-time inventory visibility | All 23 locations, 15,000+ SKUs, updated every 30 seconds |
| Low-stock alerts | Configurable thresholds per SKU, color-coded by urgency |
| Automated reorder recommendations | Quantity + suggested vendor, based on lead time and forecasted demand |
| Demand forecasting | 7-day forward-looking forecast per SKU per location, refreshed hourly |
| Multi-source unification | POS, Shopify, and warehouse scanner data merged into a single view |
| Role-based access | Store managers see their location; regional managers see their territory; HQ sees everything |

---

## The Results

Within the first 30 days of going live:

| Metric | Before | After | Change |
|---|---|---|---|
| Stockout incidents (monthly) | 187 | 123 | **-34%** |
| Average time to detect a stockout | 4.2 hours | Under 2 minutes | **99% faster** |
| Inventory carrying cost | $412,000 | $378,000 | **-8.2%** (less safety stock needed) |
| Reorder processing time (per order) | 18 minutes | Under 30 seconds | **97% faster** |
| Store manager time spent on inventory tasks | ~11 hours/week | ~3 hours/week | **73% reduction** |

The COO's quote after the first month: "I open the dashboard, scan the red items, and I know exactly what to do. It used to take Monday morning meetings to figure out what we were out of."

---

## Why It Worked

**Data unification first, AI second.** Rather than jumping straight to forecasting, we solved the integration problem: getting all three data sources flowing into one canonical stream. ML only works when the input data is clean and complete.

**Real-time, not fast-enough.** StockWise's initial ask was for a dashboard that refreshed every 10 minutes. We pushed for sub-minute updates because the high-velocity items (top 20% of SKUs driving 80% of revenue) moved fast enough that a 10-minute delay still meant lost sales. Redis pub/sub made the 30-second target achievable without overloading the Postgres instance.

**Forecasting that earns trust.** We deliberately kept the ML model simple -- gradient-boosted trees, not a black-box deep learning model -- so StockWise's ops team could understand what drove a forecast. We built a forecast explainability panel into the dashboard that shows the top factors influencing each prediction (day of week, recent velocity, seasonal index). The team started trusting the reorder recommendations within two weeks.

**Built for the floor, not just the boardroom.** The primary users are store managers on warehouse floors and at stock counters. The UI is touch-friendly, works on tablets, and surfaces the single most important action at any moment: "Order 14 units of SKU #4821 for Location 7."

---

## Tech Stack Detail

| Layer | Technology | Purpose |
|---|---|---|
| API & ingestion | Python, FastAPI | REST endpoints, webhook receivers, connector orchestration |
| Real-time layer | Redis | Pub/sub event bus, caching current inventory state, 30-second refresh cycle |
| Database | PostgreSQL | Historical sales, inventory ledger, forecast storage, user accounts |
| ML engine | scikit-learn (gradient-boosted trees) | 7-day demand forecasting per SKU per location |
| Frontend | React, Recharts | Dashboard UI with live heatmap, alert feed, forecast explorer |
| Deployment | Docker, AWS ECS | Containerized services behind an Application Load Balancer |

---

## What's Next

NexusPoint is working with StockWise on Phase 2, which will add:

- **Automated purchase order generation:** Reorder recommendations that create and send POs directly to approved vendors with manager one-click approval.
- **Supplier lead-time modeling:** Factoring vendor reliability and shipping variability into reorder timing.
- **Multi-location stock balancing:** Automatic transfer recommendations when one location is overstocked and another is at risk of stocking out.

---

*NexusPoint builds AI-powered operational systems for businesses that need their data to work as fast as they do. If your team is running on spreadsheets and gut feel, [let's talk](https://nexus-point.co).*