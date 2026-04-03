from pipecat_flows import NodeConfig


def create_transfer_node() -> NodeConfig:
    return {
        "name": "transfer_to_human",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Let the customer know you're transferring them to a human agent. "
                    "Thank them for their patience."
                ),
            }
        ],
        "post_actions": [{"type": "end_conversation"}],
    }
