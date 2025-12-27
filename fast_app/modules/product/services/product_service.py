from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.product.models.product_model import Product
from fast_app.modules.product.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
)
from fast_app.defaults.common_enums import StatusEnum
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_products(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
) -> Tuple[List[dict], Dict[str, Any]]:

    pipeline = []
    match_stage: Dict[str, Any] = {"is_deleted": False}

    if search:
        match_stage["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
        ]

    if filters and "status" in filters:
        match_stage["status"] = filters["status"]

    pipeline.append({"$match": match_stage})

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
            Product.model_validate(product).model_dump(by_alias=True, mode="json")
            for product in products
        ],
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_product_by_id(product_id: str) -> Optional[dict]:
    try:
        product = await Product.get(PydanticObjectId(product_id))
        return product.model_dump(by_alias=True, mode="json") if product else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_product(data: ProductCreate):

    if await Product.find_one(Product.name == data.name, Product.is_deleted == False):
        raise ValueError("Product already exists")
    
    if data.image:
        upload_result = await upload_files([data.image], "product-images")
        image_data = upload_result[0]
    
    product = Product(
        name=data.name,
        image=image_data.get("path","")
    )

    await product.create()
    return product.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_product(product_id: str, data: ProductUpdate):

    product = await Product.get(PydanticObjectId(product_id))
    if not product:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    if data.image:
        upload_result = await upload_files([data.image], "product-images")
        image_data = upload_result[0]
        update_data["image"]=image_data.get("path","")
    
    update_data["updated_at"] = datetime.utcnow()
    await product.set(update_data)

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
