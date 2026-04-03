from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig

from reservation_system import ReservationSystem


reservation_system = ReservationSystem()


class AvailabilityResult(FlowResult):
    date: str
    time: str
    party_size: int
    available: bool
    alternative_times: list[str] | None = None


class BookingResult(FlowResult):
    confirmation_number: str
    details: dict


async def check_availability(args: FlowArgs) -> tuple[AvailabilityResult, NodeConfig]:
    from flow.end_conversation import end_conversation_schema
    from flow.start_conversation import route_intent_schema

    date = args["date"]
    time = args["time"]
    party_size = args["party_size"]
    available, alternatives = await reservation_system.check_availability(party_size, time, date)
    result = AvailabilityResult(
        date=date, time=time, party_size=party_size,
        available=available, alternative_times=alternatives,
    )
    if available:
        return result, {
            "name": "collect_contact",
            "task_messages": [
                {
                    "role": "system",
                    "content": (
                        "That time is available. Ask for their name to complete the reservation. "
                        "Phone number is optional."
                    ),
                }
            ],
            "functions": [confirm_booking_schema],
        }
    times_list = ", ".join(alternatives) if alternatives else "other times"
    return result, {
        "name": "no_availability",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    f"That time is not available. Suggest these alternatives: {times_list}. "
                    "Ask if they'd like one of these or need help with something else."
                ),
            }
        ],
        "functions": [check_availability_schema, route_intent_schema, end_conversation_schema],
    }


async def confirm_booking(args: FlowArgs) -> tuple[BookingResult, NodeConfig]:
    from flow.end_conversation import end_conversation_schema
    from flow.start_conversation import route_intent_schema

    reservation = await reservation_system.book(
        party_size=args["party_size"],
        time=args["time"],
        date=args["date"],
        name=args["name"],
        phone=args.get("phone"),
    )
    result = BookingResult(
        confirmation_number=reservation["confirmation_number"],
        details=reservation,
    )
    return result, {
        "name": "booking_confirmed",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Confirm the reservation with the confirmation number and details. "
                    "Ask if there's anything else you can help with."
                ),
            }
        ],
        "functions": [route_intent_schema, end_conversation_schema],
    }


check_availability_schema = FlowsFunctionSchema(
    name="check_availability",
    description="Check availability for a date, time, and party size",
    properties={
        "date": {
            "type": "string",
            "description": "Date for the reservation",
        },
        "time": {
            "type": "string",
            "pattern": "^([5-9]|10):00 PM$",
            "description": "Time between 5:00 PM and 10:00 PM",
        },
        "party_size": {
            "type": "integer",
            "minimum": 1,
            "maximum": 20,
            "description": "Number of people",
        },
    },
    required=["date", "time", "party_size"],
    handler=check_availability,
)

confirm_booking_schema = FlowsFunctionSchema(
    name="confirm_booking",
    description="Complete the booking with customer contact info",
    properties={
        "name": {
            "type": "string",
            "description": "Customer's name",
        },
        "phone": {
            "type": "string",
            "description": "Customer's phone number",
        },
        "party_size": {
            "type": "integer",
            "description": "Number of people",
        },
        "date": {
            "type": "string",
            "description": "Reservation date",
        },
        "time": {
            "type": "string",
            "description": "Reservation time",
        },
    },
    required=["name", "party_size", "date", "time"],
    handler=confirm_booking,
)


def create_book_reservation_node() -> NodeConfig:
    return {
        "name": "book_reservation",
        "task_messages": [
            {
                "role": "system",
                "content": "Ask for their desired date, time, and party size. We're open 5 PM to 10 PM.",
            }
        ],
        "functions": [check_availability_schema],
    }
