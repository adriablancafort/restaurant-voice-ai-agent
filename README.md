# Restaurant Voice AI Agent

[<img src="https://img.youtube.com/vi/L-L3xBnx0yw/sddefault.jpg" alt="Demo Video" style="width: 100%;">](https://www.youtube.com/watch?v=L-L3xBnx0yw "Watch the demo video")

A voice AI receptionist for a restaurant built with [Pipecat](https://docs.pipecat.ai/getting-started/quickstart) and [Pipecat Flows](https://docs.pipecat.ai/guides/features/pipecat-flows).

This project simulates a real restaurant phone assistant for **La Maison**, an upscale French restaurant. The agent can:

- book reservations
- reschedule reservations
- cancel reservations
- answer common restaurant FAQs
- transfer the caller to a human
- end the conversation naturally

It uses Pipecat's real-time voice pipeline for WebRTC audio conversations and Pipecat Flows to model the conversation as a set of task-oriented nodes.

## Stack

- **Pipecat** for the voice pipeline and transport runner
- **Pipecat Flows** for intent routing and multi-step conversation logic
- **Deepgram** for speech-to-text
- **OpenAI** for the LLM
- **Cartesia** for text-to-speech
- **Silero VAD** and **Local Smart Turn v3** for turn detection
- **WebRTC** for local browser-based voice sessions

## Conversation Flows

### 1. Start Conversation and Intent Routing

The conversation starts with:

> "Restaurant La Maison, how can I help you?"

The assistant then routes the caller into one of these intents:

- `book_reservation`
- `cancel_reservation`
- `reschedule_reservation`
- `ask_question`
- `transfer_to_human`

This is implemented in [`flow/start_conversation.py`](./flow/start_conversation.py).

### 2. Book Reservation

The booking flow:

- asks for the **date**, **time**, and **party size**
- checks availability
- suggests alternative times if the requested slot is unavailable
- collects the guest's **name**
- optionally collects a **phone number**
- confirms the reservation with a confirmation number

This is implemented in [`flow/book_reservation.py`](./flow/book_reservation.py).

### 3. Reschedule Reservation

The rescheduling flow:

- looks up an existing reservation by **confirmation number**, **name**, or **phone**
- asks for the new **date** and/or **time**
- confirms the updated reservation details

This is implemented in [`flow/reschedule_reservation.py`](./flow/reschedule_reservation.py).

### 4. Cancel Reservation

The cancellation flow:

- looks up the reservation by **confirmation number**, **name**, or **phone**
- confirms the reservation details with the caller
- asks for confirmation before canceling
- confirms the cancellation

This is implemented in [`flow/cancel_reservation.py`](./flow/cancel_reservation.py).

### 5. FAQ Flow

The FAQ flow answers common restaurant questions about:

- location
- hours
- menu
- prices
- promotions

This is implemented in [`flow/answer_faq.py`](./flow/answer_faq.py).

### 6. Human Transfer

If the caller asks to speak with a person, the assistant switches to a human transfer flow and ends the automated conversation.

This is implemented in [`flow/transfer.py`](./flow/transfer.py).

### 7. End Conversation

When the caller is done, the assistant thanks them and ends the call gracefully.

This is implemented in [`flow/end_conversation.py`](./flow/end_conversation.py).

## Reservation Backend

The reservation logic currently uses a simple in-memory demo backend in [`reservation_system.py`](./reservation_system.py).

It supports:

- availability checks
- booking reservations
- finding reservations
- canceling reservations
- rescheduling reservations

Important notes:

- This is a **mock reservation system**, not a production database.
- It simulates latency with `asyncio.sleep(...)`.
- FAQ content is also hard-coded for demo purposes.
- The current flow modules each instantiate their own `ReservationSystem`, so bookings are not shared across all flows yet. For a production-ready version, these flows should use one shared persistence layer.

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- a Deepgram API key
- an OpenAI API key
- a Cartesia API key

### Install Dependencies

```bash
uv sync
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

### Run Locally

Start the agent with Pipecat's WebRTC transport:

```bash
uv run agent.py
```

Then open:

```text
http://localhost:7860/client
```

Allow microphone access and click **Connect** to start speaking with the restaurant receptionist.
