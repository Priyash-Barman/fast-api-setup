from fast_app.modules.category.models.category_model import Category
from fast_app.modules.chat.models.block_model import Block
from fast_app.modules.chat.models.message_model import Message
from fast_app.modules.chat.models.report_model import Report
from fast_app.modules.chat.models.room_model import Room
from fast_app.modules.cms.models.buyer_cms_model import BuyerCms
from fast_app.modules.cms.models.common_cms_model import Banner
from fast_app.modules.cms.models.seller_cms_model import SellerCms
from fast_app.modules.contact_us.models.contact_us_model import ContactUs
from fast_app.modules.demo.models.demo_model import Demo
from fast_app.modules.democms.models.democms_model import Democms
from fast_app.modules.demoform.models.demoform_model import Demoform
from fast_app.modules.notification.models.notification_model import Notification
from fast_app.modules.privacy_policy.models.privacy_policy_model import PrivacyPolicy
from fast_app.modules.product.models.product_model import Product
from fast_app.modules.terms_and_condition.models.terms_and_condition_model import TermsAndCondition
from fast_app.modules.user.models.user_device_model import UserDevice
from fast_app.modules.user.models.user_model import User
from fast_app.modules.user.models.user_otp_model import UserOtp

document_models = [
    # register models here
    User,
    Demo,
    Demoform,
    UserDevice,
    Notification,
    Room,
    Message,
    Report,
    Block,
    Product,
    Category,
    UserOtp,
    PrivacyPolicy,
    TermsAndCondition,
    ContactUs,
    Banner,
    BuyerCms,
    SellerCms,
    Democms,
]
