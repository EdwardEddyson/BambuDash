# backend/app/api/v1/endpoints/makerworld.py
import re
import json
import httpx
import logging
from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class MakerWorldSearchResult(BaseModel):
    title: str
    url: str
    image_url: str
    design_id: str

def find_designs_in_dict(obj, depth: int = 0, max_depth: int = 10) -> list:
    """
    Recursively search a nested dictionary or list for a list of design-like objects.
    A design-like object is a dictionary containing some form of 'id' and 'title'/'name'.
    """
    if depth > max_depth:
        return []

    if isinstance(obj, list):
        dicts = [item for item in obj if isinstance(item, dict)]
        if dicts:
            # Check if elements look like a design
            has_id = any("id" in item or "designId" in item or "design_id" in item for item in dicts[:5])
            has_title = any("title" in item or "name" in item for item in dicts[:5])
            if has_id and has_title:
                return dicts
        for item in obj:
            res = find_designs_in_dict(item, depth=depth + 1, max_depth=max_depth)
            if res is not None and len(res) > 0:
                return res
    elif isinstance(obj, dict):
        for val in obj.values():
            res = find_designs_in_dict(val, depth=depth + 1, max_depth=max_depth)
            if res is not None and len(res) > 0:
                return res
    return []

@router.get("/search", response_model=List[MakerWorldSearchResult])
def search_makerworld(q: str = Query(..., description="The query term to search MakerWorld models")):
    """
    Search MakerWorld designs by keyword using an API proxy with a scraper fallback.
    """
    results = []

    # Method 1: Fetch from API design/list
    try:
        response = httpx.get(
            f"https://makerworld.com/api/v1/design/list?keyword={q}",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=5.0
        )
        if response.status_code == 200:
            data = response.json()
            design_list = []
            if isinstance(data, list):
                design_list = data
            elif isinstance(data, dict):
                if "data" in data and isinstance(data["data"], dict) and "list" in data["data"]:
                    design_list = data["data"]["list"]
                elif "data" in data and isinstance(data["data"], list):
                    design_list = data["data"]
                else:
                    design_list = find_designs_in_dict(data)

            for item in design_list:
                design_id = str(item.get("id") or item.get("designId") or item.get("design_id") or "")
                if not design_id:
                    continue
                title = str(item.get("title") or item.get("name") or item.get("designName") or "Untitled")
                image_url = str(item.get("cover") or item.get("coverUrl") or item.get("imageUrl") or item.get("image_url") or item.get("thumbnail") or item.get("thumbnailUrl") or "")
                url = item.get("url") or f"https://makerworld.com/en/models/{design_id}"
                if url.startswith("/"):
                    url = "https://makerworld.com" + url
                results.append(
                    MakerWorldSearchResult(
                        title=title,
                        url=url,
                        image_url=image_url,
                        design_id=design_id
                    )
                )
    except Exception as e:
        logger.warning(f"Error querying MakerWorld API: {e}", exc_info=True)

    if results:
        return results

    # Method 2: Scrape fallback via __NEXT_DATA__
    try:
        response = httpx.get(
            f"https://makerworld.com/en/search/models?key={q}",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=5.0
        )
        if response.status_code == 200:
            html = response.text
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
            if match:
                json_data = json.loads(match.group(1))
                design_list = find_designs_in_dict(json_data)
                for item in design_list:
                    design_id = str(item.get("id") or item.get("designId") or item.get("design_id") or "")
                    if not design_id:
                        continue
                    title = str(item.get("title") or item.get("name") or item.get("designName") or "Untitled")
                    image_url = str(item.get("cover") or item.get("coverUrl") or item.get("imageUrl") or item.get("image_url") or item.get("thumbnail") or item.get("thumbnailUrl") or "")
                    url = item.get("url") or f"https://makerworld.com/en/models/{design_id}"
                    if url.startswith("/"):
                        url = "https://makerworld.com" + url
                    results.append(
                        MakerWorldSearchResult(
                            title=title,
                            url=url,
                            image_url=image_url,
                            design_id=design_id
                        )
                    )
    except Exception as e:
        logger.warning(f"Error querying MakerWorld API: {e}", exc_info=True)

    return results
