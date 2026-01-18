from typing import Optional

from beanie import Document


class Banner(Document):
    title: str
    description: Optional[str] = ""
    image: Optional[str] = None