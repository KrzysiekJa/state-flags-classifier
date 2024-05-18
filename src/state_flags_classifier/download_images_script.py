import os
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image


async def fetch(session, urls):
    async with session.get(urls['wiki_url']) as response:
        return await response.text()

async def create_img_path(urls, country_name, session):
    img_path = os.path.join(urls['imgs_dir'] + f'/{country_name}/', 'flag_00.png')
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    return img_path

async def download_png(image_url, img_path, session):
    async with session.get(image_url) as response:
        with open(img_path, 'wb') as file:
            file.write(await response.read())

async def process_flag(image_url, urls, country_name, session):
    img_path = await create_img_path(urls, country_name, session)
    await download_png(image_url, img_path, session)
    print(f"Downloaded {country_name}'s flag to {img_path}")

async def main(urls):
    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, urls)
        soup = BeautifulSoup(page_content, 'html.parser')

        flag_tasks = []

        for div in soup.find_all('div', class_='thumb'):
            link = div.find('img')
            if link:
                country_name = re.findall(r'Flag_of_(.*?).svg', link['src'])[0]
                url_parts = '/'.join(re.findall(r'thumb/(.)/(..)/Flag_of_', link['src'])[0])
                image_url = urls['wiki_upload_url'] + url_parts
                image_url += f'/Flag_of_{country_name}.svg/640px-Flag_of_{country_name}.svg.png']
                flag_tasks.append(
                    process_flag(image_url, urls, country_name.replace('_', ' '), session)
                )

        await asyncio.gather(*flag_tasks)

if __name__ == '__main__':
    urls = {
        'wiki_url': 'https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags',
        'wiki_upload_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/',
        'imgs_dir': 'data/country_flag',
    }
    os.makedirs('data', exist_ok=True)
    os.makedirs(urls['imgs_dir'], exist_ok=True)
    asyncio.run(main(urls))
