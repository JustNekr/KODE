from aiohttp import ClientSession


async def validate_text(text: str) -> str:

    async with ClientSession() as session:
        url = "https://speller.yandex.net/services/spellservice.json/checkText"
        data = {"text": text}
        async with session.post(url, data=data) as response:
            speller_data = await response.json()
        if speller_data:
            text = replace_text(text, speller_data)
        return text


def replace_text(text: str, speller_data: list) -> str:
    for mistake in speller_data:
        text = text.replace(mistake["word"], mistake["s"][0])
    return text
