from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.product.models.product_model import Product
from fast_app.modules.product.schemas.product_schema import (
    ProductCreateForm,
    ProductResponse,
    ProductUpdateForm,
)
from fast_app.defaults.common_enums import StatusEnum
from fast_app.utils.common_utils import escape_regex, exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger
import inspect



# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_products(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
    category_filter: List[Optional[str|PydanticObjectId]] = []
) -> Tuple[List[dict], Dict[str, Any]]:

    pipeline = []
    match_stage: Dict[str, Any] = {"is_deleted": False}

    if search:
        safe_search=escape_regex(search)
        match_stage["$or"] = [
            {"name": {"$regex": safe_search, "$options": "i"}},
        ]

    if filters and "status" in filters:
        match_stage["status"] = filters["status"]
        
    if len(category_filter):
        match_stage["category_id"]={"$in":category_filter}

    pipeline.append({"$match": match_stage})
    
    # category lookup
    pipeline.append({
        "$lookup": {
            "from": "categories",
            "localField": "category_id",
            "foreignField": "_id",
            "as": "category",
        }
    })
    pipeline.append({
        "$unwind": {
            "path": "$category",
            "preserveNullAndEmptyArrays": True
        }
    })

    sort_field = sort.lstrip("-") if sort else "created_at"
    sort_dir = -1 if sort and sort.startswith("-") else 1

    products, pagination = await Product.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )
    
    return (
        [
            ProductResponse.model_validate(product).model_dump(by_alias=True, mode="json")
            for product in products
        ],
        pagination,
    )
    
async def get_products_group_by_category(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    filters: Optional[Dict] = None,
    category_filter: List[Optional[str|PydanticObjectId]] = []
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:

    pipeline = []
    match_stage: Dict[str, Any] = {"is_deleted": False}

    if search:
        safe_search=escape_regex(search)
        match_stage["$or"] = [
            {"name": {"$regex": safe_search, "$options": "i"}},
        ]

    if filters and "status" in filters:
        match_stage["status"] = filters["status"]
        
    if len(category_filter):
        match_stage["category_id"]={"$in":category_filter}

    pipeline.append({"$match": match_stage})
    
    # category lookup
    pipeline.append({
        "$lookup": {
            "from": "categories",
            "localField": "category_id",
            "foreignField": "_id",
            "as": "category",
        }
    })
    pipeline.append({
        "$unwind": {
            "path": "$category",
            "preserveNullAndEmptyArrays": True
        }
    })

    sort_field = "category.name"
    sort_dir = 1

    products, pagination = await Product.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )
    
    product_list=[ProductResponse.model_validate(product).model_dump(by_alias=True, mode="json")
            for product in products]

    grouped: dict[str, list] = {}

    for product in product_list:
        category_name = product.get("category", {}).get("name", "Unknown")

        grouped.setdefault(category_name, []).append(product)

    data = [
        {
            "title": category,
            "data": products
        }
        for category, products in grouped.items()
    ]
    
    return (
        data,
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_product_by_id(product_id: str):
    try:
        collection = Product.get_pymongo_collection()
        match_stage = {
            "$match": {
                "_id": PydanticObjectId(product_id),
                "is_deleted": False
            },
        }
        
        result = collection.aggregate([
            match_stage,
            # category lookup
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "category_id",
                    "foreignField": "_id",
                    "as": "category",
                }
            },
            {
                "$unwind": {
                    "path": "$category",
                    "preserveNullAndEmptyArrays": True
                }
            }
        ])
        cursor = await result if inspect.isawaitable(result) else result

        products = await cursor.to_list(length=1)
        if not products:
            return None

        product = products[0]
        return ProductResponse.model_validate(product).model_dump(by_alias=True, mode="json")
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_product(data: ProductCreateForm):

    if await Product.find_one(Product.name == data.name, Product.is_deleted == False):
        raise ValueError("Product already exists")
    
    image_data={}
    if data.image:
        upload_result = await upload_files([data.image], "product-images")
        image_data = upload_result[0]
    
    product = Product(
        name=data.name,
        image=image_data.get("path",""),
        category_id=PydanticObjectId(data.category_id)
    )

    await product.create()
    return product.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_product(product_id: str, data: ProductUpdateForm):

    product = await Product.get(PydanticObjectId(product_id))
    if not product:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    image_data={}
    if data.image:
        upload_result = await upload_files([data.image], "product-images")
        image_data = upload_result[0]
        update_data["image"]=image_data.get("path","")
    
    if update_data.get("category_id"):
        update_data["category_id"] = PydanticObjectId(update_data.get("category_id"))

    update_data["updated_at"] = datetime.utcnow()
    await product.set(exclude_unset(update_data))

    return product.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# CHANGE STATUS
# -----------------------------------------------------
async def change_product_status(product_id: str, status: StatusEnum):

    product = await Product.get(PydanticObjectId(product_id))
    if not product:
        return None

    await product.set({
        "status": status,
        "updated_at": datetime.utcnow(),
    })

    return product.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_product(product_id: str) -> bool:

    product = await Product.get(PydanticObjectId(product_id))
    if not product:
        return False

    await product.set({
        "is_deleted": True,
        "updated_at": datetime.utcnow(),
    })

    return True
