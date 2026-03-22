import strawberry
from fast_app.modules.mobile.graphql.mobile_mutations import MobileMutation
from fast_app.modules.demo.graphql.demo_mutations import DemoMutation
from fast_app.modules.demoform.graphql.demo_form_mutations import DemoFormMutation

@strawberry.type
class Mutation(
    # add mutations here
    DemoMutation,
    DemoFormMutation,
    MobileMutation,
):
    pass