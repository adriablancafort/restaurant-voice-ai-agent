from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig

from reservation_system import ReservationSystem


reservation_system = ReservationSystem()


class FindResult(FlowResult):
    found: bool
    reservation: dict | None = None


class RescheduleResult(FlowResult):
    confirmation_number: str
    details: dict


async def find_and_reschedule(args: FlowArgs) -> tuple[FindResult | RescheduleResult | None, NodeConfig]:
    from flow.end_conversation import end_conversation_schema
    from flow.start_conversation import route_intent_schema

    reservation = await reservation_system.find(
        confirmation_number=args.get("confirmation_number"),
        name=args.get("name"),
        phone=args.get("phone"),
    )
    if not reservation:
        return FindResult(found=False), {
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
            "functions": [find_and_reschedule_schema, route_intent_schema, end_conversation_schema],
        }
    new_date = args.get("new_date")
    new_time = args.get("new_time")
    if new_date or new_time:
        updated = await reservation_system.reschedule(
            confirmation_number=reservation["confirmation_number"],
            new_date=new_date,
            new_time=new_time,
        )
        if updated:
            result = RescheduleResult(
                confirmation_number=updated["confirmation_number"],
                details=updated,
            )
            return result, {
                "name": "reschedule_confirmed",
                "task_messages": [
                    {
                        "role": "system",
                        "content": (
                            "Confirm the reservation has been rescheduled with the new details. "
                            "Ask if there's anything else you can help with."
                        ),
                    }
                ],
                "functions": [route_intent_schema, end_conversation_schema],
            }
        return None, {
            "name": "reschedule_failed",
            "task_messages": [
                {
                    "role": "system",
                    "content": (
                        "Apologize that the rescheduling could not be processed "
                        "and offer to transfer them to a human."
                    ),
                }
            ],
            "functions": [route_intent_schema, end_conversation_schema],
        }
    return FindResult(found=True, reservation=reservation), {
        "name": "reschedule_options",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "You found their reservation. Ask what new date or time they'd like. "
                    "We're open 5 PM to 10 PM."
                ),
            }
        ],
        "functions": [find_and_reschedule_schema],
    }


find_and_reschedule_schema = FlowsFunctionSchema(
    name="find_and_reschedule",
    description="Find a reservation and optionally reschedule it",
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
        "new_date": {
            "type": "string",
            "description": "New date for the reservation",
        },
        "new_time": {
            "type": "string",
            "pattern": "^([5-9]|10):00 PM$",
            "description": "New time (5 PM to 10 PM)",
        },
    },
    required=[],
    handler=find_and_reschedule,
)


def create_reschedule_reservation_node() -> NodeConfig:
    return {
        "name": "find_and_reschedule",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Ask for their confirmation number, or their name or phone number "
                    "to look up the reservation they want to reschedule. If they mention "
                    "a new date or time, collect that too. We're open 5 PM to 10 PM."
                ),
            }
        ],
        "functions": [find_and_reschedule_schema],
    }
