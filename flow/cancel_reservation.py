from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig

from reservation_system import ReservationSystem


reservation_system = ReservationSystem()


class FindResult(FlowResult):
    found: bool
    reservation: dict | None = None


async def find_reservation(args: FlowArgs) -> tuple[FindResult, NodeConfig]:
    from flow.end_conversation import end_conversation_schema
    from flow.start_conversation import route_intent_schema

    reservation = await reservation_system.find(
        confirmation_number=args.get("confirmation_number"),
        name=args.get("name"),
        phone=args.get("phone"),
    )
    result = FindResult(found=reservation is not None, reservation=reservation)
    if reservation:
        return result, {
            "name": "confirm_cancel",
            "task_messages": [
                {
                    "role": "system",
                    "content": (
                        "You found their reservation. Confirm the details and ask if they're sure "
                        "they want to cancel."
                    ),
                }
            ],
            "functions": [cancel_reservation_schema, route_intent_schema],
        }
    return result, {
        "name": "reservation_not_found",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Apologize that you couldn't find their reservation. "
                    "Ask if they'd like to try again with different information."
                ),
            }
        ],
        "functions": [find_reservation_schema, route_intent_schema, end_conversation_schema],
    }


async def cancel_reservation(args: FlowArgs) -> tuple[None, NodeConfig]:
    from flow.end_conversation import end_conversation_schema
    from flow.start_conversation import route_intent_schema

    success = await reservation_system.cancel(args["confirmation_number"])
    if success:
        return None, {
            "name": "cancellation_confirmed",
            "task_messages": [
                {
                    "role": "system",
                    "content": (
                        "Confirm the reservation has been cancelled. "
                        "Ask if there's anything else you can help with."
                    ),
                }
            ],
            "functions": [route_intent_schema, end_conversation_schema],
        }
    return None, {
        "name": "cancellation_failed",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Apologize that the cancellation could not be processed "
                    "and offer to transfer them to a human."
                ),
            }
        ],
        "functions": [route_intent_schema, end_conversation_schema],
    }


find_reservation_schema = FlowsFunctionSchema(
    name="find_reservation",
    description="Look up a reservation by confirmation number, name, or phone",
    properties={
        "confirmation_number": {
            "type": "string",
            "description": "Reservation confirmation number",
        },
        "name": {
            "type": "string",
            "description": "Name on the reservation",
        },
        "phone": {
            "type": "string",
            "description": "Phone number on the reservation",
        },
    },
    required=[],
    handler=find_reservation,
)

cancel_reservation_schema = FlowsFunctionSchema(
    name="cancel_reservation",
    description="Cancel the reservation",
    properties={
        "confirmation_number": {
            "type": "string",
            "description": "Confirmation number of reservation to cancel",
        },
    },
    required=["confirmation_number"],
    handler=cancel_reservation,
)


def create_cancel_reservation_node() -> NodeConfig:
    return {
        "name": "find_reservation_cancel",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Ask for their confirmation number, or their name or phone number "
                    "to look up the reservation they want to cancel."
                ),
            }
        ],
        "functions": [find_reservation_schema],
    }
