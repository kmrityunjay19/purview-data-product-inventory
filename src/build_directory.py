"""Build an anonymised Gold-style data-product directory from Purview-like metadata."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a data-product directory from governance metadata.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)

    domains = source["domains"]
    products = source["data_products"]
    terms = source["glossary_terms"]
    domain_lookup = {domain["domain_key"]: domain for domain in domains}
    term_lookup = {term["term_key"]: term for term in terms}
    bridge_rows, directory_rows = [], []

    for product in products:
        domain = domain_lookup[product["domain_key"]]
        term_names = []
        for term_key in product["terms"]:
            bridge_rows.append({"product_key": product["product_key"], "term_key": term_key})
            term_names.append(term_lookup[term_key]["term_name"])
        directory_rows.append({
            "product_key": product["product_key"], "product_name": product["product_name"],
            "domain_key": product["domain_key"], "domain_name": domain["domain_name"],
            "owner": product["owner"], "description": product["description"],
            "glossary_terms": "; ".join(term_names), "quality_score": product["quality_score"],
            "purview_url": product["purview_url"], "powerbi_app_url": product["powerbi_app_url"],
            "quality_report_url": product["quality_report_url"], "asset_count": len(product["assets"]),
        })

    write_csv(args.output / "dim_domain.csv", domains, ["domain_key", "domain_name", "owner"])
    write_csv(args.output / "dim_glossary_term.csv", terms, ["term_key", "term_name", "definition"])
    write_csv(args.output / "bridge_product_term.csv", bridge_rows, ["product_key", "term_key"])
    write_csv(args.output / "bridge_user_domain_entitlement.csv", source["user_domain_entitlements"], ["user_principal_name", "domain_key"])
    write_csv(args.output / "data_product_directory.csv", directory_rows, list(directory_rows[0]))
    print(f"Wrote {len(directory_rows)} directory entries and {len(bridge_rows)} glossary associations")


if __name__ == "__main__":
    main()
