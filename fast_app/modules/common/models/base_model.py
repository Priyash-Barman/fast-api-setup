from typing import Any, Dict, List, Optional, Tuple

from beanie import Document


class BaseDocument(Document):
    """Base document class with common utility methods"""
    
    class Settings:
        use_state_management = True
        use_revision = False
        abstract = True
    
    @classmethod
    async def aggregate_with_pagination(
        cls,
        pipeline: List[Dict[str, Any]],
        page: int = 1,
        limit: int = 10,
        sort_field: str = "created_at",
        sort_dir: int = -1,
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Execute aggregation with pagination and return results
        in mongoose-paginate-v2 compatible format.
        """

        page = max(page, 1)
        limit = max(limit, 1)
        skip = (page - 1) * limit

        full_pipeline = pipeline + [
            {
                "$facet": {
                    "metadata": [{"$count": "total_docs"}],
                    "docs": [
                        {"$sort": {sort_field: sort_dir}},
                        {"$skip": skip},
                        {"$limit": limit},
                    ],
                }
            }
        ]

        collection = cls.get_pymongo_collection()
        cursor = collection.aggregate(full_pipeline)
        result = await cursor.to_list(length=1)  # type: ignore

        # -------------------------
        # Handle empty collection
        # -------------------------
        if not result:
            return [], {
                "total_docs": 0,
                "skip": skip,
                "page": page,
                "total_pages": 0,
                "limit": limit,
                "has_prev_page": False,
                "has_next_page": False,
                "prev_page": None,
                "next_page": None,
            }

        facet = result[0]
        docs = facet.get("docs", [])
        metadata = facet.get("metadata", [])

        total_docs = metadata[0]["total_docs"] if metadata else 0
        total_pages = (total_docs + limit - 1) // limit if total_docs else 0

        pagination = {
            "total_docs": total_docs,
            "skip": skip,
            "page": page,
            "total_pages": total_pages,
            "limit": limit,
            "has_prev_page": page > 1,
            "has_next_page": page < total_pages,
            "prev_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None,
        }

        return docs, pagination

    
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

