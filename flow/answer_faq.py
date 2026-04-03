from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig

RESTAURANT_INFO = {
    "location": "123 Main Street, Downtown. We're located right next to the historic city hall building.",
    "hours": "We're open Tuesday through Sunday from 5 PM to 10 PM. We're closed on Mondays.",
    "menu": "We serve upscale French cuisine including appetizers like escargot and foie gras, main courses like coq au vin, duck confit, and beef bourguignon, and desserts like creme brulee and tarte tatin. We also have an extensive wine list.",
    "prices": "Our appetizers range from $12 to $28, main courses from $32 to $65, and desserts from $10 to $15. We also offer a prix fixe menu for $85 per person.",
    "promotions": "We currently have a special early bird discount of 20% off if you dine before 6:30 PM on weekdays. We also offer a prix fixe menu on Sundays.",
}


class FAQResult(FlowResult):
    question: str
    answer: str


async def answer_question(args: FlowArgs) -> tuple[FAQResult, NodeConfig]:
    from flow.end_conversation import end_conversation_schema
    from flow.start_conversation import route_intent_schema

    question_type = args["question_type"]
    answer = RESTAURANT_INFO.get(question_type, "I don't have that information available.")
    result = FAQResult(question=question_type, answer=answer)
    return result, {
        "name": "faq_answered",
        "task_messages": [
            {
                "role": "system",
                "content": "You've provided the information. Ask if there's anything else you can help with.",
            }
        ],
        "functions": [route_intent_schema, end_conversation_schema],
    }


answer_question_schema = FlowsFunctionSchema(
    name="answer_question",
    description="Answer a question about the restaurant",
    properties={
        "question_type": {
            "type": "string",
            "enum": ["location", "hours", "menu", "prices", "promotions"],
            "description": "Type of question being asked",
        }
    },
    required=["question_type"],
    handler=answer_question,
)


def create_answer_faq_node() -> NodeConfig:
    return {
        "name": "faq",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Listen to the customer's question about the restaurant. Determine if it's about our "
                    "location, hours, menu, prices, or current promotions, then provide the answer."
                ),
            }
        ],
        "functions": [answer_question_schema],
    }
