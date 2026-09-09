"""
pipeline/transformer.py — Data Normalization & Flattening Engine
Author: Aria (Lead Developer)
"""

from typing import Dict, Any, List

class DataTransformer:
    """
    Transforms heterogeneous ingested payloads into clean, normalized formats.
    Flattens nested dictionaries and computes summary statistics.
    """
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
        """Flattens nested dictionary keys with dot-notation."""
        items: List[tuple] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, dict):
                items.extend(DataTransformer.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Represent array length and first element if simple
                items.append((f"{new_key}.count", len(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def extract_summary_metrics(flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates statistical summary of numerical values in flat dataset."""
        nums = [v for v in flat_data.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if not nums:
            return {"numeric_fields": 0}
        return {
            "numeric_fields": len(nums),
            "min_val": round(min(nums), 2),
            "max_val": round(max(nums), 2),
            "sum_val": round(sum(nums), 2),
            "avg_val": round(sum(nums) / len(nums), 2)
        }
