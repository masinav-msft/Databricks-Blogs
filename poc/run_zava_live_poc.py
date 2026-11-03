"""
Live End-to-End 3-Act POC Demo Runner (Dedicated Zava_* Nomenclature):
Act 1 (DATA):         Azure Databricks (`zava_enterprise_uc` & `zava_fabric_onelake_catalog`)
                      <-> Microsoft Fabric (`Zava_Mirrored_Databricks_UC`, `Zava_Unified_Lakehouse`, `Zava_Enterprise_Warehouse`)
Act 2 (INTELLIGENCE): Fabric IQ (`Zava_Enterprise_Ontology_IQ`) + Fabric Data Agent (`Zava_Insights_DataAgent`)
                      + Microsoft Foundry (`Zava-Enterprise-Insights-Agent` on `aishu-ai-foundry`)
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
FOUNDRY_ENDPOINT = "https://aishu-ai-foundry.cognitiveservices.azure.com"
FOUNDRY_AGENT_NAME = "Zava-Enterprise-Insights-Agent"
FOUNDRY_DEPLOYMENT = "gpt-4o"


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
    url = f"{FOUNDRY_ENDPOINT}/openai/deployments/{FOUNDRY_DEPLOYMENT}/chat/completions?api-version=2024-08-01-preview"
    system_prompt = (
        f"You are `{FOUNDRY_AGENT_NAME}` running in Microsoft Foundry (`aishu-foundry-project`). "
        "You are grounded in live enterprise data from Azure Databricks Unity Catalog (`zava_enterprise_uc`), "
        "mirrored zero-copy into Microsoft Fabric (`Zava_Mirrored_Databricks_UC` and `Zava_Unified_Lakehouse`), "
        "and governed by Fabric IQ (`Zava_Enterprise_Ontology_IQ`) and `Zava_Insights_DataAgent`:\n"
        "- Business Rule 1: Evaluate regional performance by comparing actual total_revenue against quarterly_revenue_target from `Zava_Enterprise_Warehouse.dbo.dim_region_targets`.\n"
        "- Business Rule 2: 'Revenue at risk' is defined as annualized_revenue where churn_status = 'Yes' in `gold_customer_churn_risk`.\n"
        "- Business Rule 3: Correlate churn with mobile website bounce rates in `gold_campaign_bounce_metrics`.\n"
        "- Always cite exact numbers, customer names, product names, bounce rates, and recommended retention actions."
    )
    user_prompt = (
        f"Business Question: {question}\n\n"
        f"Live Zero-Copy Data Retrieved from Azure Databricks (`zava_enterprise_uc`) & Microsoft Fabric (`Zava_Unified_Lakehouse`):\n"
        f"{json.dumps(fabric_context, indent=2)}"
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 750,
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
    print("=" * 96)
    print(" THE MODERN AZURE JOURNEY: BRAND-NEW ZAVA_* E2E POC (DATA -> INTELLIGENCE -> EXPERIENCE)")
    print(" Environment: admin@MngEnvMCAP927255.onmicrosoft.com")
    print("=" * 96)

    dbx_token = get_az_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d")
    foundry_token = get_az_token("https://cognitiveservices.azure.com")

    # -------------------------------------------------------------------------
    # ACT 1A: Outbound Zero-Copy (Fabric OneLake -> Azure Databricks Federation)
    # -------------------------------------------------------------------------
    print("\n[ACT 1A — OUTBOUND FEDERATION] Querying Fabric `Zava_Enterprise_Warehouse` from Azure Databricks...")
    fed_join_sql = """
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
    ORDER BY target_variance ASC
    """
    fed_res = run_databricks_sql(dbx_token, fed_join_sql)
    for row in fed_res["result"]["data_array"]:
        print(
            f"  -> [Databricks Cross-Platform Join] Region: {row[0]:10s} | VP: {row[1]:15s} | "
            f"Target: ${float(row[2]):10,.2f} | Actual: ${float(row[3]):10,.2f} | Variance: ${float(row[4]):11,.2f}"
        )

    # -------------------------------------------------------------------------
    # ACT 1B: Inbound Zero-Copy (Azure Databricks UC -> Fabric Mirrored UC & Lakehouse)
    # -------------------------------------------------------------------------
    print("\n[ACT 1B — INBOUND MIRRORING] Querying `Zava_Unified_Lakehouse` (Shortcuts to `Zava_Mirrored_Databricks_UC`)...")
    regional_summary = run_fabric_tsql(
        "Zava_Unified_Lakehouse",
        """
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
        """,
    )
    for row in regional_summary:
        print(
            f"  -> [Zava_Unified_Lakehouse] {row['region']:10s} | {row['product_name']:22s} "
            f"({row['brand_family']:11s}) | Rev: ${row['total_revenue']:9,.2f} | Returns: {row['return_transactions']}"
        )

    churn_details = run_fabric_tsql(
        "Zava_Unified_Lakehouse",
        """
        SELECT
          customer_id,
          customer_name,
          region,
          customer_segment,
          contract_type,
          primary_product,
          annualized_revenue,
          support_tickets_90d,
          website_bounce_rate_pct,
          churn_status,
          churn_reason,
          recommended_retention_action
        FROM dbo.gold_customer_churn_risk
        WHERE churn_status = 'Yes'
        ORDER BY annualized_revenue DESC;
        """,
    )
    print(f"  -> Retrieved {len(churn_details)} at-risk accounts from `Zava_Unified_Lakehouse.dbo.gold_customer_churn_risk`.")

    # -------------------------------------------------------------------------
    # ACT 2 & ACT 3: INTELLIGENCE & EXPERIENCE (`Zava-Enterprise-Insights-Agent`)
    # -------------------------------------------------------------------------
    print(f"\n[ACT 2 & 3 — INTELLIGENCE & EXPERIENCE] Invoking `{FOUNDRY_AGENT_NAME}` in Microsoft Foundry...")
    question = (
        "Why is the Southwest region missing its quarterly revenue target and experiencing high product returns and churn risk, "
        "how much annualized revenue is at risk in Southwest, and what specific actions should VP Elena Rostova take for each at-risk customer?"
    )
    print(f"\n  Executive Question: \"{question}\"\n")

    answer = ask_foundry_agent(
        foundry_token,
        question,
        {
            "databricks_unity_catalog": "zava_enterprise_uc (bronze_ingestion, silver_curated, gold_analytics)",
            "databricks_onelake_federated_catalog": "zava_fabric_onelake_catalog (Zava_Enterprise_Warehouse)",
            "fabric_mirrored_catalog_item": "Zava_Mirrored_Databricks_UC",
            "fabric_unified_lakehouse": "Zava_Unified_Lakehouse",
            "fabric_iq_ontology": "Zava_Enterprise_Ontology_IQ",
            "fabric_data_agent": "Zava_Insights_DataAgent",
            "foundry_agent": FOUNDRY_AGENT_NAME,
            "cross_platform_target_variance": fed_res["result"]["data_array"],
            "regional_sales_summary": regional_summary,
            "high_risk_churn_customers": churn_details,
        },
    )
    print("-" * 96)
    print(answer)
    print("-" * 96)


if __name__ == "__main__":
    main()
