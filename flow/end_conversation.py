from pipecat_flows import FlowArgs, FlowsFunctionSchema, NodeConfig


async def end_conversation(args: FlowArgs) -> tuple[None, NodeConfig]:
    return None, {
        "name": "end",
        "task_messages": [
            {
                "role": "system",
                "content": "Thank them for calling La Maison and wish them a wonderful day.",
            }
        ],
        "post_actions": [{"type": "end_conversation"}],
    }


end_conversation_schema = FlowsFunctionSchema(
    name="end_conversation",
    description="End the conversation when the customer is done",
    properties={},
    required=[],
    handler=end_conversation,
)
