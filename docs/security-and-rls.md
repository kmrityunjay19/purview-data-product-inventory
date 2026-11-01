# Security and RLS design

## Discovery versus data access

The directory uses RLS to control which product entries appear in the Power BI report. It does not replace data-plane access checks:

1. The Purview catalog and resource permissions determine which metadata and assets a person can discover.
2. The Power BI semantic model applies RLS to the directory using the user-to-domain entitlement bridge.
3. Source-system and Fabric permissions control whether the person can use the linked data asset after discovery.

## Semantic-model role

Create a `DirectoryConsumer` role with this filter on `bridge_user_domain_entitlement`:

```DAX
[user_principal_name] = USERPRINCIPALNAME()
```

Use a single-direction relationship from the entitlement bridge to `dim_domain`, then to `dim_data_product`. Product, term, quality, and link data should inherit that filter path.

## Operational controls

- Reconcile entitlements with the identity-management process on a schedule.
- Audit changes to product ownership, quality links, and published URLs.
- Flag products with no domain owner, no glossary association, no quality assessment, or stale deep links.
- Expose a request-access route; do not expose direct raw data solely because a catalog item is visible.
