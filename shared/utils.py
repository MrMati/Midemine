async def first_n(agen, n):
    result = []
    async for item in agen:
        result.append(item)
        if len(result) >= n:
            break
    return result
