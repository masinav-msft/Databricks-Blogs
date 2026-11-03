"""
Live End-to-End 3-Act POC Demo Runner (Large-Scale 405,050 Rows & Brand-New Zava_* Nomenclature):
Act 1 (DATA):         Azure Databricks (`zava_enterprise_uc` [405,050 rows] & `zava_fabric_onelake_catalog`)
                      <-> Microsoft Fabric (`Zava_Mirrored_Databricks_UC`, `Zava_Unified_Lakehouse`, `Zava_Enterprise_Warehouse`)
Act 2 (INTELLIGENCE): Fabric IQ (`Zava_Enterprise_Ontology_IQ`) + Fabric Data Agent (`Zava_Insights_DataAgent`)
                      + Brand-New Microsoft Foundry (`zava-enterprise-foundry` -> `zava-enterprise-project` -> `Zava-Enterprise-Insights-Agent` on `gpt-5.5` / `gpt-5.4-pro`)
Act 3 (EXPERIENCE):   Executive Business Q&A Grounded in Live Zero-Copy Enterprise Data
"""

import json
import subprocess
import urllib.request

DBX_HOST = "https://adb-7405607060119348.8.azuredatabricks.net"
DBX_WAREHOUSE_ID = "4a57219370b180ea"
FABRIC_WORKSPACE_ID = "8b72677f-f882-4123-93bd-6da6856677be"
FABRIC_MIRROR_ID = "19ebb1e0-bfd8-42ff-8058-681ed813d97a"       # Zava_Mirrored_Databricks_UC
FABRIC_LAKEHOUSE_ID = "014e8d94-1f30-45b2-a732-18ef9873f027"    # Zava_Unified_Lakehouse
FABRIC_WAREHOUSE_ID = "768bae7f-8ca1-44ba-b4d0-061177d0fe22"    # Zava_Enterprise_Warehouse
FABRIC_ONTOLOGY_ID = "cc9b99a3-e222-493c-9273-d2b033baf6a2"     # Zava_Enterprise_Ontology_IQ
FABRIC_DATA_AGENT_ID = "2bd3427a-d55a-4064-8f10-86c1eb9c02c7"   # Zava_Insights_DataAgent
FABRIC_SQL_ENDPOINT = "twe2nl2gvkjeti7llsablks5d4-p5txfc4c7arude55nwtikztxxy.datawarehouse.fabric.microsoft.com"

# Brand-New Dedicated Microsoft Foundry Account & Project
FOUNDRY_ACCOUNT = "zava-enterprise-foundry"
FOUNDRY_PROJECT = "zava-enterprise-project"
FOUNDRY_ENDPOINT = "https://zava-enterprise-foundry.cognitiveservices.azure.com"
FOUNDRY_AGENT_NAME = "Zava-Enterprise-Insights-Agent"
FOUNDRY_DEPLOYMENT = "gpt-5.5"


def get_az_token(resource: str) -> str:
    return subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", resource, "--query", "accessToken", "-o", "tsv"],
        text=True,
        shell=True,
    ).strip()


def run_databricks_sql(token: str, statement: str) -> dict:
    url = f"{DBX_HOST}/api/2.0/sql/statements"
    payload = {"warehouse_id": DBX_WAREHOUSE_ID, "statement": statement, "wait_timeout": "50s"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_fabric_tsql(database: str, query: str) -> list[dict]:
    ps_script = f"""
$sqlToken = az account get-access-token --resource "https://database.windows.net/" --query accessToken -o tsv
$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = "Server=tcp:{FABRIC_SQL_ENDPOINT},1433;Database={database};Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
$conn.AccessToken = $sqlToken
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = @"
{query}
"@
$r = $cmd.ExecuteReader()
$rows = @()
while ($r.Read()) {{
  $obj = [ordered]@{{}}
  for ($i=0; $i -lt $r.FieldCount; $i++) {{
    $obj[$r.GetName($i)] = $r.GetValue($i)
  }}
  $rows += [PSCustomObject]$obj
}}
$r.Close()
$conn.Close()
$rows | ConvertTo-Json -Depth 3 -Compress
"""
    out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_script], text=True).strip()
    if not out:
        return []
    parsed = json.loads(out)
    return parsed if isinstance(parsed, list) else [parsed]


def ask_foundry_agent(foundry_token: str, question: str, fabric_context: dict) -> str:
    url = f"{FOUNDRY_ENDPOINT}/openai/deployments/{FOUNDRY_DEPLOYMENT}/chat/completions?api-version=2025-04-01-preview"
    system_prompt = (
        f"You are `{FOUNDRY_AGENT_NAME}` running on `{FOUNDRY_DEPLOYMENT}` in Microsoft Foundry (`{FOUNDRY_ACCOUNT}` / `{FOUNDRY_PROJECT}`). "
        "You are grounded in live enterprise-scale data (405,050 rows across Bronze, Silver, and Gold) from Azure Databricks Unity Catalog (`zava_enterprise_uc`), "
        "mirrored zero-copy into Microsoft Fabric (`Zava_Mirrored_Databricks_UC` and `Zava_Unified_Lakehouse`), "
        "and governed by Fabric IQ (`Zava_Enterprise_Ontology_IQ`) and `Zava_Insights_DataAgent`:\n"
        "- Business Rule 1: Evaluate regional performance by comparing actual total_revenue across all 120,000 transactions against annual_revenue_target from `Zava_Enterprise_Warehouse.dbo.dim_region_targets`.\n"
        "- Business Rule 2: 'Revenue at risk' is defined as annualized_revenue where churn_status = 'Yes' across the 25,000 customer accounts in `gold_customer_churn_risk`.\n"
        "- Business Rule 3: Correlate churn with mobile website bounce rates across the 10,000 campaigns in `gold_campaign_bounce_metrics`.\n"
        "- Always cite exact numbers, regional totals, return transaction counts, and specific retention actions."
    )
    user_prompt = (
        f"Business Question: {question}\n\n"
        f"Live Zero-Copy Enterprise Data Retrieved from Azure Databricks (`zava_enterprise_uc`) & Microsoft Fabric (`Zava_Unified_Lakehouse`):\n"
        f"{json.dumps(fabric_context, indent=2)}"
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_completion_tokens": 4000,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {foundry_token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def main():
    print("=" * 98)
    print(" THE MODERN AZURE JOURNEY: ENTERPRISE-SCALE ZAVA_* E2E POC (405,050 ROWS | GPT-5.5)")
    print(f" Foundry: {FOUNDRY_ACCOUNT} -> {FOUNDRY_PROJECT} -> {FOUNDRY_AGENT_NAME} ({FOUNDRY_DEPLOYMENT})")
    print("=" * 98)

    dbx_token = get_az_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d")
    foundry_token = get_az_token("https://cognitiveservices.azure.com")

    # -------------------------------------------------------------------------
    # ACT 1A: Outbound Zero-Copy (Fabric OneLake -> Azure Databricks Federation)
    # -------------------------------------------------------------------------
    print("\n[ACT 1A — OUTBOUND FEDERATION] Cross-Platform Join in Databricks (`zava_fabric_onelake_catalog` x `zava_enterprise_uc` [120,000 sales rows])...")
    fed_join_sql = """
    SELECT
      t.region,
      t.regional_vp,
      t.annual_revenue_target,
      COUNT(s.transaction_id) AS total_txns,
      ROUND(SUM(s.total_revenue), 2) AS actual_revenue,
      ROUND(SUM(s.total_revenue) - t.annual_revenue_target, 2) AS target_variance,
      SUM(CASE WHEN s.return_flag = 'Yes' THEN 1 ELSE 0 END) AS return_txns
    FROM zava_fabric_onelake_catalog.dbo.dim_region_targets t
    JOIN zava_enterprise_uc.gold_analytics.regional_sales_performance s
      ON t.region = s.region
    GROUP BY t.region, t.regional_vp, t.annual_revenue_target
    ORDER BY target_variance ASC
    """
    fed_res = run_databricks_sql(dbx_token, fed_join_sql)
    for row in fed_res["result"]["data_array"]:
        print(
            f"  -> [Databricks Cross-Platform Join] Region: {row[0]:10s} | VP: {row[1]:15s} | "
            f"Txns: {int(row[3]):6,d} | Target: ${float(row[2]):13,.2f} | Actual: ${float(row[4]):13,.2f} | Returns: {int(row[6]):5,d}"
        )

    # -------------------------------------------------------------------------
    # ACT 1B: Inbound Zero-Copy (Azure Databricks UC -> Fabric Mirrored UC & Lakehouse)
    # -------------------------------------------------------------------------
    print("\n[ACT 1B — INBOUND MIRRORING] Querying 405,050 Mirrored Rows in Fabric `Zava_Unified_Lakehouse` via T-SQL...")
    churn_summary = run_fabric_tsql(
        "Zava_Unified_Lakehouse",
        """
        SELECT
          region,
          COUNT(*) AS total_customers,
          SUM(CASE WHEN churn_status = 'Yes' THEN 1 ELSE 0 END) AS high_risk_churn_customers,
          ROUND(AVG(website_bounce_rate_pct), 1) AS avg_mobile_bounce_rate_pct,
          ROUND(SUM(CASE WHEN churn_status = 'Yes' THEN annualized_revenue ELSE 0 END), 2) AS total_annual_revenue_at_risk
        FROM dbo.gold_customer_churn_risk
        GROUP BY region
        ORDER BY total_annual_revenue_at_risk DESC;
        """,
    )
    for row in churn_summary:
        print(
            f"  -> [Zava_Unified_Lakehouse] Region: {row['region']:10s} | Customers: {row['total_customers']:6,d} | "
            f"At-Risk: {row['high_risk_churn_customers']:5,d} | Avg Bounce: {row['avg_mobile_bounce_rate_pct']:4.1f}% | "
            f"Annual Rev at Risk: ${row['total_annual_revenue_at_risk']:13,.2f}"
        )

    top_accounts = run_fabric_tsql(
        "Zava_Unified_Lakehouse",
        """
        SELECT TOP 5
          customer_id,
          customer_name,
          region,
          customer_segment,
          primary_product,
          annualized_revenue,
          website_bounce_rate_pct,
          churn_reason,
          recommended_retention_action
        FROM dbo.gold_customer_churn_risk
        WHERE churn_status = 'Yes' AND region = 'Southwest' AND customer_name NOT LIKE 'Zava Enterprise Account%'
        ORDER BY annualized_revenue DESC;
        """,
    )

    # -------------------------------------------------------------------------
    # ACT 2 & ACT 3: INTELLIGENCE & EXPERIENCE (`zava-enterprise-foundry` / `gpt-5.5`)
    # -------------------------------------------------------------------------
    print(f"\n[ACT 2 & 3 — INTELLIGENCE & EXPERIENCE] Invoking `{FOUNDRY_AGENT_NAME}` ({FOUNDRY_DEPLOYMENT}) on `{FOUNDRY_ACCOUNT}`...")
    question = (
        "Based on our 120,000 sales transactions and 25,000 customer accounts mirrored from Azure Databricks into Fabric, "
        "why is the Southwest region missing its $55M annual target and suffering high product returns and churn risk, "
        "how much total annualized revenue is at risk across the 2,086 at-risk Southwest accounts, and what immediate actions should VP Elena Rostova execute?"
    )
    print(f"\n  Executive Question: \"{question}\"\n")

    answer = ask_foundry_agent(
        foundry_token,
        question,
        {
            "databricks_unity_catalog": "zava_enterprise_uc (405,050 total rows: 250k bronze_raw_order_events, 50 silver_dim_products, 120k gold_regional_sales_performance, 25k gold_customer_churn_risk, 10k gold_campaign_bounce_metrics)",
            "databricks_onelake_federated_catalog": "zava_fabric_onelake_catalog (Zava_Enterprise_Warehouse)",
            "fabric_mirrored_catalog_item": "Zava_Mirrored_Databricks_UC",
            "fabric_unified_lakehouse": "Zava_Unified_Lakehouse",
            "fabric_iq_ontology": "Zava_Enterprise_Ontology_IQ",
            "fabric_data_agent": "Zava_Insights_DataAgent",
            "foundry_account": FOUNDRY_ACCOUNT,
            "foundry_project": FOUNDRY_PROJECT,
            "foundry_agent": f"{FOUNDRY_AGENT_NAME} ({FOUNDRY_DEPLOYMENT})",
            "cross_platform_regional_sales_vs_targets": fed_res["result"]["data_array"],
            "regional_churn_and_bounce_summary_25k_customers": churn_summary,
            "spotlight_southwest_named_accounts": top_accounts,
        },
    )
    print("-" * 98)
    print(answer)
    print("-" * 98)


if __name__ == "__main__":
    main()
