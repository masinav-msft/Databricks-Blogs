"""
Live End-to-End 3-Act POC Demo Runner:
Act 1 (DATA):        Azure Databricks (Unity Catalog) <-> Microsoft Fabric (Mirrored UC + OneLake Federation)
Act 2 (INTELLIGENCE): Fabric IQ Semantic Context + Fabric Data Agent + Microsoft Foundry (GPT-4o)
Act 3 (EXPERIENCE):   Executive Business Q&A Grounded in Live Zero-Copy Enterprise Data

Sandbox Environment:
- Tenant:                 MngEnvMCAP927255.onmicrosoft.com (admin@MngEnvMCAP927255.onmicrosoft.com)
- Subscription:           ME-MngEnvMCAP927255-masinav-1 (9e114e9d-1e81-4b56-9ddd-55bae9226770)
- Azure Databricks:       dbrx-mirroring-pe-fabric (https://adb-7405607060119348.8.azuredatabricks.net)
- Unity Catalogs:         fabric_mirror_catalog (Managed UC) & fabric_onelake_federation (OneLake Foreign Catalog)
- Microsoft Fabric WS:    ws_1_copilotdemo (8b72677f-f882-4123-93bd-6da6856677be)
- Mirrored UC Item:       fabric_mirror_catalog (473edebe-1fe3-451a-88ad-9831f4e3c62e)
- Fabric Lakehouse:       LH_IQDemo (f36c92a3-76c8-4a49-a57f-f12c1f251ee2)
- Fabric Data Agent:      mirror agent (682f5859-088d-4713-9d4d-28a4f5cbe3e8)
- Microsoft Foundry:      aishu-ai-foundry (https://aishu-ai-foundry.cognitiveservices.azure.com/ | gpt-4o)
"""

import json
import subprocess
import urllib.request

DBX_HOST = "https://adb-7405607060119348.8.azuredatabricks.net"
DBX_WAREHOUSE_ID = "4a57219370b180ea"
FABRIC_WORKSPACE_ID = "8b72677f-f882-4123-93bd-6da6856677be"
FABRIC_MIRROR_ID = "473edebe-1fe3-451a-88ad-9831f4e3c62e"
FABRIC_LAKEHOUSE_ID = "f36c92a3-76c8-4a49-a57f-f12c1f251ee2"
FABRIC_SQL_ENDPOINT = "twe2nl2gvkjeti7llsablks5d4-p5txfc4c7arude55nwtikztxxy.datawarehouse.fabric.microsoft.com"
FOUNDRY_ENDPOINT = "https://aishu-ai-foundry.cognitiveservices.azure.com"
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
        "You are the Zava Enterprise Insights Agent running in Microsoft Foundry. "
        "You are grounded in live enterprise data from Azure Databricks Unity Catalog (`fabric_mirror_catalog.sales_schema`) "
        "mirrored zero-copy into Microsoft Fabric OneLake (`LH_IQDemo`), governed by Fabric IQ Ontology & Semantic rules:\n"
        "- Business Rule 1: 'Top selling products' or 'regional performance' must be evaluated by total_revenue and return rates.\n"
        "- Business Rule 2: 'Revenue at risk' is defined as annualized_revenue where churn_status = 'Yes'.\n"
        "- Always cite exact numbers, customer names, product names, bounce rates, and recommended retention actions from the live Fabric/Databricks data."
    )
    user_prompt = (
        f"Business Question: {question}\n\n"
        f"Live Zero-Copy Data Retrieved from Microsoft Fabric OneLake & Mirrored Azure Databricks Unity Catalog:\n"
        f"{json.dumps(fabric_context, indent=2)}"
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
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
    print("=" * 92)
    print(" THE MODERN AZURE JOURNEY: LIVE E2E POC DEMO (DATA -> INTELLIGENCE -> EXPERIENCE)")
    print(" Environment: admin@MngEnvMCAP927255.onmicrosoft.com")
    print("=" * 92)

    dbx_token = get_az_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d")
    foundry_token = get_az_token("https://cognitiveservices.azure.com")

    # -------------------------------------------------------------------------
    # ACT 1: DATA (1/3) — Bidirectional Zero-Copy Interoperability
    # -------------------------------------------------------------------------
    print("\n[ACT 1 — DATA (1/3)] Validating Bidirectional Zero-Copy Interoperability...")

    print("  1A. Outbound (Fabric OneLake -> Azure Databricks via OneLake Catalog Federation):")
    fed_res = run_databricks_sql(
        dbx_token,
        "SELECT COUNT(*) AS total_rows FROM fabric_onelake_federation.dbo.customer",
    )
    fed_count = fed_res["result"]["data_array"][0][0]
    print(f"      -> Queried `fabric_onelake_federation.dbo.customer` from Databricks Serverless SQL: {int(fed_count):,} rows (Zero-Copy!)")

    print("  1B. Inbound (Azure Databricks Unity Catalog -> Microsoft Fabric via Mirrored UC & OneLake Shortcuts):")
    regional_summary = run_fabric_tsql(
        "LH_IQDemo",
        """
        SELECT
          region,
          product_name,
          customer_segment,
          SUM(units_sold) AS total_units,
          ROUND(SUM(total_revenue), 2) AS total_revenue,
          SUM(CASE WHEN return_flag = 'Yes' THEN 1 ELSE 0 END) AS return_transactions,
          ROUND(AVG(discount_pct) * 100, 1) AS avg_discount_pct
        FROM dbo.dbrx_regional_sales_performance
        GROUP BY region, product_name, customer_segment
        ORDER BY region, total_revenue DESC;
        """,
    )
    for row in regional_summary:
        print(
            f"      -> [LH_IQDemo.dbo.dbrx_regional_sales_performance] {row['region']:10s} | "
            f"{row['product_name']:22s} | Rev: ${row['total_revenue']:9,.2f} | Returns: {row['return_transactions']}"
        )

    churn_details = run_fabric_tsql(
        "LH_IQDemo",
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
        FROM dbo.dbrx_customer_churn_risk
        WHERE churn_status = 'Yes'
        ORDER BY annualized_revenue DESC;
        """,
    )
    print(f"      -> Retrieved {len(churn_details)} high-risk churn accounts from `LH_IQDemo.dbo.dbrx_customer_churn_risk`.")

    # -------------------------------------------------------------------------
    # ACT 2 & ACT 3: INTELLIGENCE (2/3) & EXPERIENCE (3/3)
    # -------------------------------------------------------------------------
    print("\n[ACT 2 & 3 — INTELLIGENCE & EXPERIENCE] Grounding Microsoft Foundry Agent (GPT-4o) with Live Fabric Data...")
    question = (
        "Why is the Southwest region experiencing high product returns and customer churn risk compared to Northeast and Northwest, "
        "how much annualized revenue is at risk in Southwest, and what specific actions should we take for each at-risk customer?"
    )
    print(f"\n  Executive Question: \"{question}\"\n")

    answer = ask_foundry_agent(
        foundry_token,
        question,
        {
            "source_unity_catalog": "fabric_mirror_catalog.sales_schema",
            "fabric_lakehouse": "LH_IQDemo (ws_1_copilotdemo)",
            "regional_sales_summary": regional_summary,
            "high_risk_churn_customers": churn_details,
        },
    )
    print("-" * 92)
    print(answer)
    print("-" * 92)


if __name__ == "__main__":
    main()
