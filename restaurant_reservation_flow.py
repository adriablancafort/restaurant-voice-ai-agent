from pipecat_flows import FlowArgs, FlowResult, FlowsFunctionSchema, NodeConfig
from reservation_system import ReservationSystem


reservation_system = ReservationSystem()


class PartySizeResult(FlowResult):
    size: int
    status: str


class TimeResult(FlowResult):
    status: str
    time: str
    available: bool
    alternative_times: list[str]


async def collect_party_size(args: FlowArgs) -> tuple[PartySizeResult, NodeConfig]:
    """Process party size collection."""
    size = args["size"]
    result = PartySizeResult(size=size, status="success")
    next_node = create_time_selection_node()
    return result, next_node


async def check_availability(args: FlowArgs) -> tuple[TimeResult, NodeConfig]:
    """Check reservation availability and return result."""
    time = args["time"]
    party_size = args["party_size"]

    is_available, alternative_times = await reservation_system.check_availability(party_size, time)

    result = TimeResult(
        status="success", time=time, available=is_available, alternative_times=alternative_times
    )

    if is_available:
        next_node = create_confirmation_node()
    else:
        next_node = create_no_availability_node(result["alternative_times"])

    return result, next_node


async def end_conversation(args: FlowArgs) -> tuple[None, NodeConfig]:
    """Handle conversation end."""
    return None, create_end_node()


party_size_schema = FlowsFunctionSchema(
    name="collect_party_size",
    description="Record the number of people in the party",
    properties={"size": {"type": "integer", "minimum": 1, "maximum": 12}},
    required=["size"],
    handler=collect_party_size,
)

availability_schema = FlowsFunctionSchema(
    name="check_availability",
    description="Check availability for requested time",
    properties={
        "time": {
            "type": "string",
            "pattern": "^([5-9]|10):00 PM$",
            "description": "Reservation time (e.g., '6:00 PM')",
        },
        "party_size": {"type": "integer"},
    },
    required=["time", "party_size"],
    handler=check_availability,
)

end_conversation_schema = FlowsFunctionSchema(
    name="end_conversation",
    description="End the conversation",
    properties={},
    required=[],
    handler=end_conversation,
)


def create_initial_node(wait_for_user: bool = False) -> NodeConfig:
    """Create initial node for party size collection."""
    return {
        "name": "initial",
        "role_messages": [
            {
                "role": "system",
                "content": "You are a restaurant reservation assistant for La Maison, an upscale French restaurant. Be casual and friendly. This is a voice conversation, so avoid special characters and emojis.",
            }
        ],
        "task_messages": [
            {
                "role": "system",
                "content": "Warmly greet the customer and ask how many people are in their party. This is your only job for now; if the customer asks for something else, politely remind them you can't do it.",
            }
        ],
        "functions": [party_size_schema],
        "respond_immediately": not wait_for_user,
    }


def create_time_selection_node() -> NodeConfig:
    """Create node for time selection and availability check."""
    return {
        "name": "get_time",
        "task_messages": [
            {
                "role": "system",
                "content": "Ask what time they'd like to dine. Restaurant is open 5 PM to 10 PM.",
            }
        ],
        "functions": [availability_schema],
    }


def create_confirmation_node() -> NodeConfig:
    """Create confirmation node for successful reservations."""
    return {
        "name": "confirm",
        "task_messages": [
            {
                "role": "system",
                "content": "Confirm the reservation details and ask if they need anything else.",
            }
        ],
        "functions": [end_conversation_schema],
    }


def create_no_availability_node(alternative_times: list[str]) -> NodeConfig:
    """Create node for handling no availability."""
    times_list = ", ".join(alternative_times)
    return {
        "name": "no_availability",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    f"Apologize that the requested time is not available. "
                    f"Suggest these alternative times: {times_list}. "
                    "Ask if they'd like to try one of these times."
                ),
            }
        ],
        "functions": [availability_schema, end_conversation_schema],
    }


def create_end_node() -> NodeConfig:
    """Create the final node."""
    return {
        "name": "end",
        "task_messages": [
            {
                "role": "system",
                "content": "Thank them and end the conversation.",
            }
        ],
        "post_actions": [{"type": "end_conversation"}],
    }
