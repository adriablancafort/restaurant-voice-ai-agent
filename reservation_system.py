import asyncio


class ReservationSystem:
    def __init__(self):
        self.booked_times = {"7:00 PM", "8:00 PM"}
        self.reservations = {}
        self.next_id = 1000

    async def check_availability(self, party_size: int, time: str, date: str) -> tuple[bool, list[str]]:
        await asyncio.sleep(0.3)
        available = time not in self.booked_times
        alternatives = []
        if not available:
            all_times = ["5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"]
            alternatives = [t for t in all_times if t not in self.booked_times]
        return available, alternatives

    async def book(self, party_size: int, time: str, date: str, name: str, phone: str = None) -> dict:
        await asyncio.sleep(0.3)
        confirmation = str(self.next_id)
        self.next_id += 1
        reservation = {
            "confirmation_number": confirmation,
            "name": name,
            "phone": phone,
            "party_size": party_size,
            "date": date,
            "time": time,
            "status": "confirmed",
        }
        self.reservations[confirmation] = reservation
        return reservation

    async def find(self, confirmation_number: str = None, name: str = None, phone: str = None) -> dict | None:
        await asyncio.sleep(0.3)
        if confirmation_number:
            return self.reservations.get(confirmation_number)
        for r in self.reservations.values():
            if name and r["name"].lower() == name.lower():
                return r
            if phone and r.get("phone") == phone:
                return r
        return None

    async def cancel(self, confirmation_number: str) -> bool:
        await asyncio.sleep(0.3)
        if confirmation_number in self.reservations:
            self.reservations[confirmation_number]["status"] = "cancelled"
            return True
        return False

    async def reschedule(self, confirmation_number: str, new_date: str = None, new_time: str = None) -> dict | None:
        await asyncio.sleep(0.3)
        if confirmation_number not in self.reservations:
            return None
        reservation = self.reservations[confirmation_number]
        if new_date:
            reservation["date"] = new_date
        if new_time:
            reservation["time"] = new_time
        return reservation
