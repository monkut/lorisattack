from typing import List
from pathlib import Path

from .models import StaticSite


def instantiate_staticsite(staticsite: StaticSite, directory: Path) -> List[dict]:
    """Generate staticsites to the target directory"""
    instantiated_pages = []
    for page in staticsite.pages():
        instantiated_assets = [(abs_filepath, rel_filepath) for abs_filepath, rel_filepath in page.prepare_assets(directory)]
        asset_absolute_filepaths = [abs_fp for abs_fp, _ in instantiated_assets]
        asset_relative_filepaths = [rel_fp for _, rel_fp in instantiated_assets]

        instantiated_page_data = page.instantiate(directory)
        page_data = {
            'id': page.id,
            'type': page.type,
            'data': [],
            'asset_absolute_filepaths': asset_absolute_filepaths,
            'asset_relative_filepaths': asset_relative_filepaths
        }
        if instantiated_page_data:
            page_data['data'].extend(instantiated_page_data)
        instantiated_pages.append(page_data)

    return instantiated_pages
