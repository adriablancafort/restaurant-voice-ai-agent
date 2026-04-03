from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig

from flow.answer_faq import create_answer_faq_node
from flow.book_reservation import create_book_reservation_node
from flow.cancel_reservation import create_cancel_reservation_node
from flow.reschedule_reservation import create_reschedule_reservation_node
from flow.transfer import create_transfer_node


class IntentResult(FlowResult):
    intent: str


async def route_by_intent(args: FlowArgs) -> tuple[IntentResult, NodeConfig]:
    intent = args["intent"]
    result = IntentResult(intent=intent)
    if intent == "book_reservation":
        return result, create_book_reservation_node()
    elif intent == "cancel_reservation":
        return result, create_cancel_reservation_node()
    elif intent == "reschedule_reservation":
        return result, create_reschedule_reservation_node()
    elif intent == "ask_question":
        return result, create_answer_faq_node()
    elif intent == "transfer_to_human":
        return result, create_transfer_node()
    else:
        return result, create_start_conversation_node()


route_intent_schema = FlowsFunctionSchema(
    name="route_by_intent",
    description="Determine what the customer wants to do",
    properties={
        "intent": {
            "type": "string",
            "enum": [
                "book_reservation",
                "cancel_reservation",
                "reschedule_reservation",
                "ask_question",
                "transfer_to_human",
            ],
            "description": "The customer's intent",
        }
    },
    required=["intent"],
    handler=route_by_intent,
)


def create_start_conversation_node() -> NodeConfig:
    return {
        "name": "initial_greeting",
        "role_messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful restaurant receptionist for La Maison, an upscale French restaurant. "
                    "Be professional yet warm and friendly. This is a voice conversation, so avoid special "
                    "characters and emojis. Keep responses concise and natural."
                ),
            }
        ],
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Greet the customer with 'Restaurant La Maison, how can I help you?' and listen to "
                    "understand what they need. Determine if they want to book a reservation, cancel a "
                    "reservation, reschedule a reservation, ask questions about the restaurant, or speak "
                    "to a human."
                ),
            }
        ],
        "functions": [route_intent_schema],
        "respond_immediately": True,
    }
