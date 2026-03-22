import strawberry
from fast_app.modules.mobile.graphql.mobile_queries import MobileQuery
from fast_app.modules.demo.graphql.demo_queries import DemoQuery
from fast_app.modules.demoform.graphql.demo_form_queries import DemoFormQuery

@strawberry.type
class Query(
    # add queries here
    DemoQuery,
    DemoFormQuery,
    MobileQuery,
):
    pass