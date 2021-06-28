{
    "name": "KOKO MRP",
    "version": "1.0",
    "category": "Manufacturing",
    "sequence": 30,
    "author": "Ben",
    "summary": "MRP customizations for KOKO",
    "description": """
Customizations to MRP(base)
""",
    "website": "",
    "depends": [
        "mrp",
        "product"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/koko_mrp_data.xml",
        "views/koko_mrp_log.xml",
    ],
    "installable": True,
    "auto_install": False
}
