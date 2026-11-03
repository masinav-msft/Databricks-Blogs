# Brand-New Customer POC & Live Demo Playbook: The Modern Azure Journey (`Zava_*` Nomenclature)

*Deployed & Verified in Sandbox Environment: `admin@MngEnvMCAP927255.onmicrosoft.com`*

![The Modern Azure Journey: 3-Act Architecture Diagram](../images/3-act-architecture-diagram.svg)

---

## 1. Brand-New `Zava_*` POC Artifacts Deployed in Your Sandbox

Every single item below is **brand-new**, created specifically for this blog and customer demo with clean, consistent **`Zava_*` / `zava_*`** naming so your portal screenshots look cohesive end-to-end:

### A. Azure Databricks (`dbrx-mirroring-pe-fabric`)
- **Workspace URL:** [https://adb-7405607060119348.8.azuredatabricks.net/explore/data?o=7405607060119348](https://adb-7405607060119348.8.azuredatabricks.net/explore/data?o=7405607060119348)
- **Serverless SQL Warehouse:** `serverless` (`4a57219370b180ea`)

| Catalog Name | Catalog Type | Schema | Tables Created | Purpose in Demo |
| :--- | :--- | :--- | :--- | :--- |
| **`zava_enterprise_uc`** | `MANAGED_CATALOG` (ADLS Gen2 `sadatabrickslab01`) | `bronze_ingestion` | `raw_order_events` | **Act 1 (Medallion Bronze):** Raw ingested order events |
| **`zava_enterprise_uc`** | `MANAGED_CATALOG` | `silver_curated` | `dim_products` | **Act 1 (Medallion Silver):** Curated product & margin master |
| **`zava_enterprise_uc`** | `MANAGED_CATALOG` | `gold_analytics` | `regional_sales_performance`<br/>`customer_churn_risk`<br/>`campaign_bounce_metrics` | **Act 1 (Medallion Gold — Inbound to Fabric):** Mirrored zero-copy into Microsoft Fabric OneLake |
| **`zava_fabric_onelake_catalog`** | `FOREIGN_CATALOG` (OneLake Connection `dbrx1lake`) | `dbo` | `dim_region_targets` | **Act 1 (Outbound Federation from Fabric):** Reads Fabric `Zava_Enterprise_Warehouse` directly inside Databricks without copying data |

---

### B. Microsoft Fabric (`ws_1_copilotdemo`)
- **Workspace URL:** [https://app.fabric.microsoft.com/groups/8b72677f-f882-4123-93bd-6da6856677be/list?experience=fabric-developer](https://app.fabric.microsoft.com/groups/8b72677f-f882-4123-93bd-6da6856677be/list?experience=fabric-developer)

| Fabric Item Name | Item Type | Item ID | What's Inside |
| :--- | :--- | :--- | :--- |
| **`Zava_Mirrored_Databricks_UC`** | `MirroredAzureDatabricksCatalog` | `19ebb1e0-bfd8-42ff-8058-681ed813d97a`<br/>*(SQL Endpoint: `c5083167-d2e7-4b0d-bfb7-b4604710a8a6`)* | **Act 1 (Inbound Zero-Copy Mirror):** Automatically mirrors `bronze_ingestion.raw_order_events`, `silver_curated.dim_products`, `gold_analytics.regional_sales_performance`, `gold_analytics.customer_churn_risk`, and `gold_analytics.campaign_bounce_metrics` from `zava_enterprise_uc`. |
| **`Zava_Unified_Lakehouse`** | `Lakehouse` | `014e8d94-1f30-45b2-a732-18ef9873f027`<br/>*(SQL Endpoint: `4260e545-4aef-4e71-b027-16267b85153a`)* | **Act 1 (OneLake Shortcuts):** Contains 5 zero-copy OneLake shortcuts pointing to `Zava_Mirrored_Databricks_UC`:<br/>• `dbo.gold_regional_sales_performance`<br/>• `dbo.gold_customer_churn_risk`<br/>• `dbo.gold_campaign_bounce_metrics`<br/>• `dbo.silver_dim_products`<br/>• `dbo.bronze_raw_order_events` |
| **`Zava_Enterprise_Warehouse`** | `Warehouse` | `768bae7f-8ca1-44ba-b4d0-061177d0fe22` | **Act 1 (Outbound Federation Source):** Contains `dbo.dim_region_targets` (Regional VPs, quarterly revenue targets, and strategic priorities)—federated into Databricks as `zava_fabric_onelake_catalog`. |
| **`Zava_Enterprise_Ontology_IQ`** | `Ontology` *(Fabric IQ)* | `cc9b99a3-e222-493c-9273-d2b033baf6a2`<br/>*(GraphModel: `a65aa491-f780-4df7-8890-d21f633abad8`)* | **Act 2 (Fabric IQ Semantic Layer):** Enterprise Ontology & Graph Model for Zava's business entities. |
| **`Zava_Insights_DataAgent`** | `DataAgent` | `2bd3427a-d55a-4064-8f10-86c1eb9c02c7` | **Act 2 (Fabric Data Agent):** Conversational Data Agent for Zava's unified lakehouse data. |

---

### C. Microsoft Foundry (`aishu-ai-foundry` / `aishu-foundry-project`)
- **Foundry Project Resource:** `/subscriptions/9e114e9d-1e81-4b56-9ddd-55bae9226770/resourceGroups/aishu-ai-learnings/providers/Microsoft.CognitiveServices/accounts/aishu-ai-foundry/projects/aishu-foundry-project`

| Foundry Resource Name | Type | ID / Version | Purpose in Demo |
| :--- | :--- | :--- | :--- |
| **`Zava_Insights_DataAgent_Conn`** | Project Connection (`fabric_dataagent`) | Connected to `Zava_Insights_DataAgent` (`2bd3427a-d55a-4064-8f10-86c1eb9c02c7`) | **Act 2 → Act 3 Bridge:** Links Microsoft Foundry to the Fabric Data Agent in `ws_1_copilotdemo`. |
| **`Zava-Enterprise-Insights-Agent`** | Foundry Agent (`gpt-4o` + `code_interpreter`) | `Zava-Enterprise-Insights-Agent:1` (`eb18acf7-5523-4295-a543-edb494e62901`) | **Act 2 & Act 3 Agent:** Grounded in Zava's Databricks + Fabric + Fabric IQ data with Code Interpreter enabled. |

---

## 2. Step-by-Step Live Customer Demo Script (With Exact Queries to Run)

### ACT 1 — DATA (1/3): Bidirectional Zero-Copy Interoperability

#### Step 1.1: Show `zava_enterprise_uc` & `zava_fabric_onelake_catalog` in Azure Databricks
1. Open [Azure Databricks Catalog Explorer](https://adb-7405607060119348.8.azuredatabricks.net/explore/data?o=7405607060119348).
2. Expand **`zava_enterprise_uc`** and show the three Medallion schemas:
   - `bronze_ingestion` (`raw_order_events`)
   - `silver_curated` (`dim_products`)
   - `gold_analytics` (`regional_sales_performance`, `customer_churn_risk`, `campaign_bounce_metrics`)
3. Next, expand **`zava_fabric_onelake_catalog`** → `dbo` → `dim_region_targets` to show **OneLake Catalog Federation** reading `Zava_Enterprise_Warehouse` from Microsoft Fabric.
4. Open the **Databricks SQL Editor** and run this **cross-platform zero-copy JOIN** combining **Fabric OneLake (`zava_fabric_onelake_catalog`)** with **Databricks Unity Catalog (`zava_enterprise_uc`)**:

```sql
-- Run in Azure Databricks SQL Editor: Cross-Platform Zero-Copy Join!
SELECT
  t.region,
  t.regional_vp,
  t.quarterly_revenue_target,
  ROUND(SUM(s.total_revenue), 2) AS actual_revenue,
  ROUND(SUM(s.total_revenue) - t.quarterly_revenue_target, 2) AS target_variance,
  t.strategic_priority
FROM zava_fabric_onelake_catalog.dbo.dim_region_targets t
JOIN zava_enterprise_uc.gold_analytics.regional_sales_performance s
  ON t.region = s.region
GROUP BY t.region, t.regional_vp, t.quarterly_revenue_target, t.strategic_priority
ORDER BY target_variance ASC;
```

---

#### Step 1.2: Show `Zava_Mirrored_Databricks_UC` & `Zava_Unified_Lakehouse` in Microsoft Fabric
1. Switch to your [Microsoft Fabric Workspace (`ws_1_copilotdemo`)](https://app.fabric.microsoft.com/groups/8b72677f-f882-4123-93bd-6da6856677be/list?experience=fabric-developer) and filter the item list by typing **`Zava_`**.
2. Click on **`Zava_Mirrored_Databricks_UC`** to show all 3 schemas (`bronze_ingestion`, `silver_curated`, `gold_analytics`) and 5 tables mirrored automatically from Azure Databricks without moving data.
3. Open **`Zava_Unified_Lakehouse`** and show the 5 OneLake shortcuts (`gold_regional_sales_performance`, `gold_customer_churn_risk`, `gold_campaign_bounce_metrics`, `silver_dim_products`, `bronze_raw_order_events`).
4. Open the **SQL analytics endpoint** of **`Zava_Unified_Lakehouse`** and run this T-SQL query:

```sql
-- Run in Microsoft Fabric SQL Analytics Endpoint (Zava_Unified_Lakehouse)
SELECT
  r.region,
  r.product_name,
  p.brand_family,
  r.customer_segment,
  SUM(r.units_sold) AS total_units,
  ROUND(SUM(r.total_revenue), 2) AS total_revenue,
  SUM(CASE WHEN r.return_flag = 'Yes' THEN 1 ELSE 0 END) AS return_transactions
FROM dbo.gold_regional_sales_performance r
JOIN dbo.silver_dim_products p
  ON r.product_id = p.product_id
GROUP BY r.region, r.product_name, p.brand_family, r.customer_segment
ORDER BY r.region, total_revenue DESC;
```

---

### ACT 2 & ACT 3 — INTELLIGENCE & EXPERIENCE: Fabric IQ, Data Agent & Microsoft Foundry

1. In the Fabric workspace filtered to **`Zava_`**, show:
   - **`Zava_Enterprise_Ontology_IQ`** (Fabric IQ Ontology & Graph Model)
   - **`Zava_Insights_DataAgent`** (Fabric Data Agent)
2. In **Microsoft Foundry** (`aishu-ai-foundry` → `aishu-foundry-project`), open **Agents** and select **`Zava-Enterprise-Insights-Agent`** (connected to `Zava_Insights_DataAgent_Conn`), or run the automated end-to-end live POC runner from your terminal:

```powershell
python .\poc\run_zava_live_poc.py
```
