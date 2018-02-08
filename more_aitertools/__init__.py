import aitertools
import asyncio
import heapq

class Queue(asyncio.Queue):
    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.get()

async def collate(*iterables, key=lambda x: x, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    iters = [
        await aitertools.aiter(iterable)
        for iterable in iterables
    ]
    heap = []
    nexts = []
    empty_iters = set()
    for i, iterable in enumerate(iters):
        try:
            item = await aitertools.anext(iterable)
            heapq.heappush(heap, (key(item), item, i))
        except StopAsyncIteration:
            empty_iters.add(i)
        else:
            nexts.append(loop.create_task(aitertools.anext(iterable)))
    for i in sorted(empty_iters, reverse=True):
        del iters[i]
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
                nexts[i] = loop.create_task(aitertools.anext(iters[i]))

async def merge(aiters):
    aiters = await aitertools.aiter(aiters)
    iters = [None]
    nexts = [asyncio.ensure_future(aitertools.anext(aiters))]
    while len(iters) > 0:
        await asyncio.wait(nexts, return_when=asyncio.FIRST_COMPLETED)
        new_iters = []
        completed_iters = set()
        for i, future in enumerate(nexts):
            if future.done():
                try:
                    if iters[i] is None:
                        # new iterator
                        new_iters.append(await aitertools.aiter(future.result()))
                    else:
                        # new item
                        yield future.result()
                    nexts[i] = asyncio.ensure_future(aitertools.anext(aiters if iters[i] is None else iters[i]))
                except StopAsyncIteration:
                    completed_iters.add(i)
        for i in sorted(completed_iters, reverse=True):
            del iters[i]
            del nexts[i]
        iters += new_iters
        nexts += [asyncio.ensure_future(aitertools.anext(new_iter)) for new_iter in new_iters]
