-- Fabric Warehouse Gold layer: logical model for a governed data-product directory.
CREATE TABLE gold.dim_domain (
    domain_key VARCHAR(50) NOT NULL PRIMARY KEY,
    domain_name VARCHAR(200) NOT NULL,
    owner_upn VARCHAR(320) NOT NULL
);

CREATE TABLE gold.dim_data_product (
    product_key VARCHAR(50) NOT NULL PRIMARY KEY,
    domain_key VARCHAR(50) NOT NULL,
    product_name VARCHAR(300) NOT NULL,
    description VARCHAR(4000) NULL,
    owner_upn VARCHAR(320) NOT NULL,
    purview_url VARCHAR(2048) NULL,
    powerbi_app_url VARCHAR(2048) NULL,
    quality_report_url VARCHAR(2048) NULL
);

CREATE TABLE gold.dim_glossary_term (
    term_key VARCHAR(50) NOT NULL PRIMARY KEY,
    term_name VARCHAR(300) NOT NULL,
    definition VARCHAR(4000) NULL
);

CREATE TABLE gold.bridge_product_term (
    product_key VARCHAR(50) NOT NULL,
    term_key VARCHAR(50) NOT NULL
);

CREATE TABLE gold.fact_data_quality (
    product_key VARCHAR(50) NOT NULL,
    assessed_at DATETIME2 NOT NULL,
    quality_score DECIMAL(5,2) NULL,
    quality_status VARCHAR(30) NULL
);

-- This bridge is the source for Power BI RLS. Populate it only through an
-- approved entitlement workflow; glossary-term searches do not grant access.
CREATE TABLE gold.bridge_user_domain_entitlement (
    user_principal_name VARCHAR(320) NOT NULL,
    domain_key VARCHAR(50) NOT NULL,
    granted_at DATETIME2 NOT NULL,
    grant_source VARCHAR(100) NOT NULL
);

CREATE VIEW gold.v_data_product_directory AS
SELECT
    product.product_key,
    product.product_name,
    domain.domain_name,
    product.description,
    product.owner_upn,
    product.purview_url,
    product.powerbi_app_url,
    product.quality_report_url,
    quality.quality_score,
    quality.quality_status
FROM gold.dim_data_product AS product
JOIN gold.dim_domain AS domain ON domain.domain_key = product.domain_key
LEFT JOIN gold.fact_data_quality AS quality ON quality.product_key = product.product_key;
