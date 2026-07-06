import time
from collections import defaultdict
import asyncio


class TokenBucketRateLimiter:
    def __init__(self, max_tokens: int = 20, refill_rate: float = 1 / 3):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.refill_rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
                self.last_refill = time.monotonic()
            else:
                self.tokens -= 1


class InMemoryRateLimiter:
    def __init__(self):
        self._limiters: dict[str, TokenBucketRateLimiter] = {}

    def get_limiter(self, key: str, max_tokens: int = 20, refill_rate: float = 1 / 3) -> TokenBucketRateLimiter:
        if key not in self._limiters:
            self._limiters[key] = TokenBucketRateLimiter(max_tokens, refill_rate)
        return self._limiters[key]

    async def acquire(self, key: str = "default"):
        limiter = self.get_limiter(key)
        await limiter.acquire()


rate_limiter = InMemoryRateLimiter()
