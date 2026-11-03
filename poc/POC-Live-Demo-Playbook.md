# Enterprise-Scale Customer POC & Live Demo Playbook: The Modern Azure Journey (`Zava_*` Nomenclature | 405,050 Rows | `gpt-5.5`)

*Deployed & Verified in Sandbox Environment: `admin@MngEnvMCAP927255.onmicrosoft.com`*

![The Modern Azure Journey: 3-Act Architecture Diagram](../images/3-act-architecture-diagram.svg)

---

## 1. Brand-New `Zava_*` POC Artifacts Deployed in Your Sandbox

Every single item below is **brand-new**, created specifically for this blog and customer demo with clean, consistent **`Zava_*` / `zava_*`** naming and **enterprise-scale data (405,050 rows across Bronze, Silver, and Gold)** plus a **brand-new Microsoft Foundry account (`zava-enterprise-foundry`)** running **`gpt-5.5`** and **`gpt-5.4-pro`**:

### A. Azure Databricks (`dbrx-mirroring-pe-fabric`) — 405,050 Enterprise Rows
- **Workspace URL:** [https://adb-7405607060119348.8.azuredatabricks.net/explore/data?o=7405607060119348](https://adb-7405607060119348.8.azuredatabricks.net/explore/data?o=7405607060119348)
- **Serverless SQL Warehouse:** `serverless` (`4a57219370b180ea`)

| Catalog Name | Catalog Type | Schema | Tables & Row Counts | Purpose in Demo |
| :--- | :--- | :--- | :--- | :--- |
| **`zava_enterprise_uc`** | `MANAGED_CATALOG` (ADLS Gen2 `sadatabrickslab01`) | `bronze_ingestion` | `raw_order_events` (**250,000 rows**) | **Act 1 (Medallion Bronze):** Raw ingested order & telemetry events |
| **`zava_enterprise_uc`** | `MANAGED_CATALOG` | `silver_curated` | `dim_products` (**50 rows**) | **Act 1 (Medallion Silver):** Curated product & margin master across 5 categories |
| **`zava_enterprise_uc`** | `MANAGED_CATALOG` | `gold_analytics` | `regional_sales_performance` (**120,000 rows**)<br/>`customer_churn_risk` (**25,000 rows**)<br/>`campaign_bounce_metrics` (**10,000 rows**) | **Act 1 (Medallion Gold — Inbound to Fabric):** Mirrored zero-copy into Microsoft Fabric OneLake |
| **`zava_fabric_onelake_catalog`** | `FOREIGN_CATALOG` (OneLake Connection `dbrx1lake`) | `dbo` | `dim_region_targets` (**4 regions, $425M annual target**) | **Act 1 (Outbound Federation from Fabric):** Reads Fabric `Zava_Enterprise_Warehouse` directly inside Databricks without copying data |

---

### B. Microsoft Fabric (`ws_1_copilotdemo`)
- **Workspace URL:** [https://app.fabric.microsoft.com/groups/8b72677f-f882-4123-93bd-6da6856677be/list?experience=fabric-developer](https://app.fabric.microsoft.com/groups/8b72677f-f882-4123-93bd-6da6856677be/list?experience=fabric-developer)

| Fabric Item Name | Item Type | Item ID | What's Inside |
| :--- | :--- | :--- | :--- |
| **`Zava_Mirrored_Databricks_UC`** | `MirroredAzureDatabricksCatalog` | `19ebb1e0-bfd8-42ff-8058-681ed813d97a`<br/>*(SQL Endpoint: `c5083167-d2e7-4b0d-bfb7-b4604710a8a6`)* | **Act 1 (Inbound Zero-Copy Mirror):** Automatically mirrors all **405,050 rows** (`bronze_ingestion.raw_order_events`, `silver_curated.dim_products`, `gold_analytics.regional_sales_performance`, `gold_analytics.customer_churn_risk`, and `gold_analytics.campaign_bounce_metrics`) from `zava_enterprise_uc`. |
| **`Zava_Unified_Lakehouse`** | `Lakehouse` | `014e8d94-1f30-45b2-a732-18ef9873f027`<br/>*(SQL Endpoint: `4260e545-4aef-4e71-b027-16267b85153a`)* | **Act 1 (OneLake Shortcuts):** Contains 5 zero-copy OneLake shortcuts pointing to `Zava_Mirrored_Databricks_UC`:<br/>• `dbo.gold_regional_sales_performance` (**120,000 rows**)<br/>• `dbo.gold_customer_churn_risk` (**25,000 rows**)<br/>• `dbo.gold_campaign_bounce_metrics` (**10,000 rows**)<br/>• `dbo.silver_dim_products` (**50 rows**)<br/>• `dbo.bronze_raw_order_events` (**250,000 rows**) |
| **`Zava_Enterprise_Warehouse`** | `Warehouse` | `768bae7f-8ca1-44ba-b4d0-061177d0fe22` | **Act 1 (Outbound Federation Source):** Contains `dbo.dim_region_targets` (Regional VPs, $425M annual revenue targets, and strategic priorities)—federated into Databricks as `zava_fabric_onelake_catalog`. |
| **`Zava_Enterprise_Ontology_IQ`** | `Ontology` *(Fabric IQ)* | `cc9b99a3-e222-493c-9273-d2b033baf6a2`<br/>*(GraphModel: `a65aa491-f780-4df7-8890-d21f633abad8`)* | **Act 2 (Fabric IQ Semantic Layer):** Enterprise Ontology & Graph Model for Zava's business entities. |
| **`Zava_Insights_DataAgent`** | `DataAgent` | `2bd3427a-d55a-4064-8f10-86c1eb9c02c7` | **Act 2 (Fabric Data Agent):** Conversational Data Agent for Zava's unified lakehouse data. |

---

### C. Brand-New Microsoft Foundry (`zava-enterprise-foundry` → `zava-enterprise-project`)
- **Resource Group:** `lumen-rg` (`eastus2`)
- **Foundry Account Resource ID:** `/subscriptions/9e114e9d-1e81-4b56-9ddd-55bae9226770/resourceGroups/lumen-rg/providers/Microsoft.CognitiveServices/accounts/zava-enterprise-foundry`
- **Foundry Project Resource ID:** `/subscriptions/9e114e9d-1e81-4b56-9ddd-55bae9226770/resourceGroups/lumen-rg/providers/Microsoft.CognitiveServices/accounts/zava-enterprise-foundry/projects/zava-enterprise-project`
- **Project Endpoint:** `https://zava-enterprise-foundry.services.ai.azure.com/api/projects/zava-enterprise-project`

| Foundry Resource Name | Type | Model / Details | Purpose in Demo |
| :--- | :--- | :--- | :--- |
| **`gpt-5.5`** & **`gpt-5.4-pro`** | Frontier Model Deployments | `gpt-5.5` (`2026-04-24`) & `gpt-5.4-pro` (`2026-03-05`) | Latest 5.5-generation frontier reasoning models deployed on `zava-enterprise-foundry` *(Note: Azure internal/MCAPS sandbox policy blocks paid 3rd-party Marketplace billing required by Anthropic `claude-opus-5-5` / `claude-sonnet-5-5`, while first-party `gpt-5.5` and `gpt-5.4-pro` run natively at $0 sandbox quota).* |
| **`Zava_Insights_DataAgent_Conn`** | Project Connection (`fabric_dataagent`) | Connected to `Zava_Insights_DataAgent` (`2bd3427a-d55a-4064-8f10-86c1eb9c02c7`) | **Act 2 → Act 3 Bridge:** Links `zava-enterprise-project` to the Fabric Data Agent in `ws_1_copilotdemo`. |
| **`Zava-Enterprise-Insights-Agent`** | Foundry Agent (`gpt-5.5` + `code_interpreter`) | `Zava-Enterprise-Insights-Agent:1` (`eec220b5-334f-42c2-bd7a-cd44e16fa5f9`) | **Act 2 & Act 3 Agent:** Grounded in Zava's 405,050-row Databricks + Fabric + Fabric IQ data with Code Interpreter enabled. |

---

## 2. Step-by-Step Live Customer Demo Script (With Exact Queries to Run)

### ACT 1 — DATA (1/3): Bidirectional Zero-Copy Interoperability over 405,050 Rows

#### Step 1.1: Show `zava_enterprise_uc` & `zava_fabric_onelake_catalog` in Azure Databricks
1. Open [Azure Databricks Catalog Explorer](https://adb-7405607060119348.8.azuredatabricks.net/explore/data?o=7405607060119348).
2. Expand **`zava_enterprise_uc`** and show the three Medallion schemas:
   - `bronze_ingestion` (`raw_order_events` — **250,000 rows**)
   - `silver_curated` (`dim_products` — **50 rows**)
   - `gold_analytics` (`regional_sales_performance` — **120,000 rows**, `customer_churn_risk` — **25,000 rows**, `campaign_bounce_metrics` — **10,000 rows**)
3. Next, expand **`zava_fabric_onelake_catalog`** → `dbo` → `dim_region_targets` to show **OneLake Catalog Federation** reading `Zava_Enterprise_Warehouse` from Microsoft Fabric.
4. Open the **Databricks SQL Editor** and run this **cross-platform zero-copy JOIN** combining **Fabric OneLake (`zava_fabric_onelake_catalog`)** with **120,000 rows in Databricks Unity Catalog (`zava_enterprise_uc`)**:

```sql
-- Run in Azure Databricks SQL Editor: Cross-Platform Zero-Copy Join over 120,000 Sales Transactions!
SELECT
  t.region,
  t.regional_vp,
  t.annual_revenue_target,
  COUNT(s.transaction_id) AS total_transactions,
  ROUND(SUM(s.total_revenue), 2) AS actual_revenue,
  ROUND(SUM(s.total_revenue) - t.annual_revenue_target, 2) AS target_variance,
  SUM(CASE WHEN s.return_flag = 'Yes' THEN 1 ELSE 0 END) AS return_transactions
FROM zava_fabric_onelake_catalog.dbo.dim_region_targets t
JOIN zava_enterprise_uc.gold_analytics.regional_sales_performance s
  ON t.region = s.region
GROUP BY t.region, t.regional_vp, t.annual_revenue_target
ORDER BY target_variance ASC;
```

---

#### Step 1.2: Show `Zava_Mirrored_Databricks_UC` & `Zava_Unified_Lakehouse` in Microsoft Fabric
1. Switch to your [Microsoft Fabric Workspace (`ws_1_copilotdemo`)](https://app.fabric.microsoft.com/groups/8b72677f-f882-4123-93bd-6da6856677be/list?experience=fabric-developer) and filter the item list by typing **`Zava_`**.
2. Click on **`Zava_Mirrored_Databricks_UC`** to show all 3 schemas (`bronze_ingestion`, `silver_curated`, `gold_analytics`) and 5 tables (**405,050 total rows**) mirrored automatically from Azure Databricks without moving data.
3. Open **`Zava_Unified_Lakehouse`** and show the 5 OneLake shortcuts (`gold_regional_sales_performance`, `gold_customer_churn_risk`, `gold_campaign_bounce_metrics`, `silver_dim_products`, `bronze_raw_order_events`).
4. Open the **SQL analytics endpoint** of **`Zava_Unified_Lakehouse`** and run this T-SQL query across the **25,000 mirrored customer accounts**:

```sql
-- Run in Microsoft Fabric SQL Analytics Endpoint (Zava_Unified_Lakehouse)
SELECT
  region,
  COUNT(*) AS total_customers,
  SUM(CASE WHEN churn_status = 'Yes' THEN 1 ELSE 0 END) AS high_risk_churn_customers,
  ROUND(AVG(website_bounce_rate_pct), 1) AS avg_mobile_bounce_rate_pct,
  ROUND(SUM(CASE WHEN churn_status = 'Yes' THEN annualized_revenue ELSE 0 END), 2) AS total_annual_revenue_at_risk
FROM dbo.gold_customer_churn_risk
GROUP BY region
ORDER BY total_annual_revenue_at_risk DESC;
```

---

### ACT 2 & ACT 3 — INTELLIGENCE & EXPERIENCE: Fabric IQ, Data Agent & `zava-enterprise-foundry` (`gpt-5.5`)

1. In the Fabric workspace filtered to **`Zava_`**, show:
   - **`Zava_Enterprise_Ontology_IQ`** (Fabric IQ Ontology & Graph Model)
   - **`Zava_Insights_DataAgent`** (Fabric Data Agent)
2. In **Microsoft Foundry** (`zava-enterprise-foundry` → `zava-enterprise-project`), open **Agents** and select **`Zava-Enterprise-Insights-Agent`** (running on **`gpt-5.5`** and connected to `Zava_Insights_DataAgent_Conn`), or run the automated end-to-end live POC runner from your terminal:

```powershell
python .\poc\run_zava_live_poc.py
```
