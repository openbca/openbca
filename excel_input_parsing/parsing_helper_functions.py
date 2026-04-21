import re

def clean_header(col: str) -> str:
    col = str(col).strip().lower()

    # Replace spaces, hyphens with underscore
    col = col.replace(" ", "_").replace("-", "_")

    # Remove parentheses
    col = re.sub(r"[()]", "", col)

    # Replace : and & with _
    col = col.replace(":", "_").replace("&", "_")

    # Replace $/ with _dollar_per_
    col = col.replace("$/", "_dollar_per_")

    # Replace $ with _dollar_
    col = col.replace("$", "_dollar_")

    # Delete adj._gross_ 
    col = col.replace("adj._gross_", "")

    # Collapse multiple underscores
    col = re.sub(r"__+", "_", col)

    # Strip trailing/leading underscores
    col = col.strip("_")

    return col