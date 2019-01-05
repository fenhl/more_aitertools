import aioitertools
import asyncio
import builtins
import concurrent.futures
import heapq

class Queue(asyncio.Queue):
    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.get()

async def collate(*iterables, key=lambda x: x):
    iters = [
        aioitertools.iter(iterable)
        for iterable in iterables
    ]
    heap = []
    nexts = []
    for i, iterable in enumerate(iters):
        try:
            item = await aioitertools.next(iterable)
            heapq.heappush(heap, (key(item), item, i))
        except StopAsyncIteration:
            nexts.append(None)
        else:
            nexts.append(asyncio.create_task(aioitertools.next(iterable)))
    while any(fut is not None for fut in nexts):
        k, item, i = heapq.heappop(heap)
        yield item
        if nexts[i] is not None:
            try:
                item = await nexts[i]
                heapq.heappush(heap, (key(item), item, i))
            except StopAsyncIteration:
                nexts[i] = None
            else:
                nexts[i] = asyncio.create_task(aioitertools.next(iters[i]))

async def consume(aiter, n=float('inf')):
    aiter = aioitertools.iter(aiter)
    if n == float('inf'):
        async for item in aiter:
            pass
    else:
        for i in range(n):
            try:
                await aioitertools.next(aiter)
            except StopAsyncIteration:
                return

async def merge(aiters):
    aiters = aioitertools.iter(aiters)
    iters = [None]
    nexts = [asyncio.create_task(aioitertools.next(aiters))]
    while len(iters) > 0:
        await asyncio.wait(nexts, return_when=asyncio.FIRST_COMPLETED)
        new_iters = []
        completed_iters = set()
        for i, future in enumerate(nexts):
            if future.done():
                try:
                    if iters[i] is None:
                        # new iterator
                        new_iters.append(aioitertools.iter(future.result()))
                    else:
                        # new item
                        yield future.result()
                    nexts[i] = asyncio.create_task(aioitertools.next(aiters if iters[i] is None else iters[i]))
                except StopAsyncIteration:
                    completed_iters.add(i)
                except concurrent.futures.CancelledError:
                    raise concurrent.futures.CancelledError('Future {!r} was cancelled'.format(future)) from e
        for i in sorted(completed_iters, reverse=True):
            del iters[i]
            del nexts[i]
        iters += new_iters
        nexts += [asyncio.create_task(aioitertools.next(new_iter)) for new_iter in new_iters]

async def tuple(aiter):
    return builtins.tuple(item async for item in aioitertools.iter(aiter))

async def wait(aiter):
    aiter = aioitertools.iter(aiter)
    items = []
    next_future = asyncio.create_task(aioitertools.next(aiter))
    while True:
        if next_future.done() or not items:
            try:
                items.append(asyncio.create_task(await next_future))
                next_future = asyncio.create_task(aioitertools.next(aiter))
            except StopAsyncIteration:
                break
        await asyncio.wait([items[0], next_future], return_when=asyncio.FIRST_COMPLETED)
        while items and items[0].done():
            yield items.pop(0).result()
    for item in items:
        yield await item

async def never():
    await asyncio.Future()
    yield
