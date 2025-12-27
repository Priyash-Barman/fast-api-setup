from fast_app.modules.chat.models.block_model import Block
from fast_app.modules.chat.models.message_model import Message
from fast_app.modules.chat.models.report_model import Report
from fast_app.modules.chat.models.room_model import Room
from fast_app.modules.demo.models.demo_model import Demo
from fast_app.modules.notification.models.notification_model import Notification
from fast_app.modules.product.models.product_model import Product
from fast_app.modules.user.models.user_device_model import UserDevice
from fast_app.modules.user.models.user_model import User

document_models = [
    # register models here
    User,
    Demo,
    UserDevice,
    Notification,
    Room,
    Message,
    Report,
    Block,
    Product,
]
