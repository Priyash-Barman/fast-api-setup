from typing import Any, Dict, List, Optional, Tuple

from beanie import Document


class BaseDocument(Document):
    """Base document class with common utility methods"""
    
    class Settings:
        use_state_management = True
        use_revision = False
    
    @classmethod
    async def aggregate_with_pagination(
        cls,
        pipeline: List[Dict[str, Any]],
        page: int = 1,
        limit: int = 10,
        sort_field: str = "created_at",
        sort_dir: int = -1,
    ) -> Tuple[List[Dict], Dict]:
        """
        Execute aggregation with pagination and return results with metadata.
        
        Args:
            pipeline: MongoDB aggregation pipeline (without pagination stages)
            page: Page number (1-indexed)
            limit: Items per page
            sort_field: Field to sort by
            sort_dir: Sort direction (1 for ascending, -1 for descending)
            
        Returns:
            Tuple of (data_list, pagination_dict)
        """
        skip = (page - 1) * limit
        
        # Add facet stage for count and data
        full_pipeline = pipeline + [
            {
                "$facet": {
                    "metadata": [{"$count": "total"}],
                    "data": [
                        {"$sort": {sort_field: sort_dir}},
                        {"$skip": skip},
                        {"$limit": limit}
                    ]
                }
            }
        ]
        
        # Execute aggregation using motor collection directly
        collection = cls.get_pymongo_collection()
        cursor = collection.aggregate(full_pipeline)
        result = await cursor.to_list(length=None)  # type: ignore

        # Handle empty results
        if not result:
            return [], {
                "current_page": page,
                "next_page": None,
                "total_pages": 0,
                "total_items": 0,
            }
        
        # Extract results
        metadata = result[0]["metadata"]
        data = result[0]["data"]
        
        total = metadata[0]["total"] if metadata else 0
        total_pages = (total + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        
        pagination = {
            "current_page": page,
            "next_page": next_page,
            "total_pages": total_pages,
            "total_items": total,
        }
        
        return data, pagination
    
    @classmethod
    async def aggregate_list(cls, pipeline: List[Dict[str, Any]]) -> List[Dict] | Any:
        """
        Execute aggregation and return all results as a list.
        
        Args:
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            List of documents
        """
        collection = cls.get_pymongo_collection()
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)  # type: ignore
        return result
    
    @classmethod
    async def aggregate_one(cls, pipeline: List[Dict[str, Any]]) -> Optional[Dict]:
        """
        Execute aggregation and return first result.
        
        Args:
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            First document or None
        """
        collection = cls.get_pymongo_collection()
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)  # type: ignore
        return result[0] if result else None

