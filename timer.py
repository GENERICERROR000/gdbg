import trio
from datetime import datetime


class Ticker:
    def __init__(self, time_step):
        # run timer every 10 seconds instead of every second
        self.time_step = time_step
        self.count = 0
        self.interval = 5

    def set_callback(self, callback):
        self.callback = callback

    async def exec_timer(self):
        while True:
            await trio.sleep(self.time_step)

            self.count += self.time_step

            if self.count >= self.interval:
                self.callback(self.interval)

                # self.interval += 1
                self.count = 0

    async def start_ticker(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.exec_timer)

    def run(self):
        if self.callback:
            trio.run(self.start_ticker)
        else:
            print("must set callback")


def catdog(interval):
    print(datetime.now())
    print("     " + str(interval))


if __name__ == "__main__":
    try:
        ticker = Ticker(5)
        ticker.set_callback(catdog)
        ticker.run()
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        print("Shutting down...")
