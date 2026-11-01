# Purview Data Product Inventory

A portfolio-safe reference architecture for an end-user data product directory built from Microsoft Purview governance metadata and Microsoft Fabric.

The solution gives data consumers a domain-based view of data products that they are authorised to discover. Each directory entry surfaces business context, glossary terms, ownership, quality status, and deep links to the relevant Purview data product, Power BI app, and data-quality report.

## Architecture

```text
Microsoft Purview Unified Catalog
  governance domains | data products | assets | glossary terms | quality metadata
                              |
                              v
Fabric Lakehouse (Bronze: raw governance metadata export)
                              |
                              v
Fabric Lakehouse (Silver: normalised domains, products, terms, assets, quality)
                              |
                              v
Fabric Warehouse (Gold: directory star schema + security bridge)
                              |
                              v
Power BI semantic model (RLS) -> Data Product Directory report / app
```

## What the project demonstrates

- A medallion pipeline from Purview governance metadata to a Power BI-ready Warehouse model
- Data-product discovery by governance domain, owner, glossary term, and quality status
- An entitlement bridge used by semantic-model RLS to filter the directory to the signed-in user's authorised domains
- Links from each data product to Purview, the published Power BI app, and an associated data-quality report
- A separately modelled business glossary so it can drive discovery without becoming a substitute for source-level access control

## Important security boundary

The directory is a discovery experience, not an access-control system for source data. RLS controls which directory entries a user can see; access to the underlying Fabric, Power BI, and Purview assets still has to be enforced by the relevant resource and catalog policies. This mirrors Purview's own discovery model, where visibility depends on catalog and resource permissions.

## Data model

| Gold table | Purpose |
| --- | --- |
| `dim_domain` | Governance domain and owner |
| `dim_data_product` | Product identity, description, ownership, deep links, and status |
| `dim_glossary_term` | Searchable business terminology |
| `bridge_product_term` | Many-to-many data product and glossary-term association |
| `fact_data_quality` | Latest product quality score and assessment link |
| `bridge_user_domain_entitlement` | Directory entitlement used by RLS |

## Local demonstration

```bash
python src/build_directory.py --input sample_data/purview_data_products.json --output outputs
```

The script writes anonymised Silver-style CSV extracts and a Gold-style `data_product_directory.csv`. The SQL in [`sql/gold_data_product_directory.sql`](sql/gold_data_product_directory.sql) shows how those tables are created in a Fabric Warehouse.

## Power BI semantic-model security

1. Import `dim_domain`, `dim_data_product`, `dim_glossary_term`, `bridge_product_term`, `fact_data_quality`, and `bridge_user_domain_entitlement`.
2. Relate `bridge_user_domain_entitlement[domain_key]` to `dim_domain[domain_key]`.
3. Create the `DirectoryConsumer` role with the filter below on `bridge_user_domain_entitlement`:

```DAX
[user_principal_name] = USERPRINCIPALNAME()
```

4. Configure relationships to propagate the permitted domains to data products and their details.
5. Keep the entitlement bridge maintained by a controlled onboarding process; do not grant access simply because a user searched for a glossary term.

## Report experience

The Power BI directory can provide:

- domain and glossary-term filters
- product cards with owner, description, key assets, and quality score
- a detail page with Purview, Power BI app, and quality-report links
- a "request access" route when the user has directory visibility but no resource permission
- an administrator view for missing owners, stale quality checks, and products without terms or assets

## Portfolio note

This is an independently designed demonstration based on general Purview and Fabric patterns. It contains only fictitious data and no employer, customer, tenant, workspace, or production configuration.

Microsoft Purview describes data products as curated groups of assets with business use, ownership, and governance context; its Unified Catalog can publish governance metadata to OneLake or ADLS Gen2 for analysis. See [data products](https://learn.microsoft.com/en-us/purview/unified-catalog-data-products) and [self-serve governance analytics](https://learn.microsoft.com/en-us/purview/unified-catalog-self-serve-analytics).
