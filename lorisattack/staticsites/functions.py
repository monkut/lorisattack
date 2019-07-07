from pathlib import Path

from .models import StaticSite


def instantiate_staticsite(staticsite: StaticSite, directory: Path):
    """Generate staticsites to the target directory"""
    for page in staticsite.pages():
        page.prepare_assets(directory)
        page.instantiate(directory)

