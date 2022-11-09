from requests import get
from json import load, loads
from nextcord.ext import commands
from members import get_members

import nextcord
import time


def get_settings():  # Get all the data that is stored in settings.json
    with open('settings.json', 'r') as file:
        settings = load(file)
        file.close()

    return settings


def get_main_info(SKU):  # Gets all the other relavent information on the product
    url = f'https://www.adidas{COUNTRY_DOMAIN}/api/products/{SKU}'
    response = get(url=url, headers=HEADERS)
    content = loads(s=response.content)

    name = content['name']
    product_url = f"https:{content['meta_data']['canonical']}"
    image_url = content['view_list'][0]['image_url']
    price = content['pricing_information']['currentPrice']
    site_name = content['meta_data']['site_name']

    return name, product_url, image_url, price, site_name


def get_availability(SKU):  # Gets the sizes and there availability
    url = f'https://www.adidas{COUNTRY_DOMAIN}/api/products/{SKU}/availability'

    response = get(url=url, headers=HEADERS)
    content = loads(s=response.content)
    variation_list = content['variation_list']

    sizes = '\n'.join(
        [f"{SIZE_PREFIX}  {variation['size']}" for variation in variation_list])
    availability = '\n'.join([str(variation['availability'])
                              for variation in variation_list])
    total_stock = sum([int(variation['availability'])
                      for variation in variation_list])

    return sizes, availability, total_stock


def get_data(SKU):  # Gets all the relevent information and returns an embed
    name, product_url, image_url, price, site_name = get_main_info(SKU=SKU)
    price = CURRENCY+str(price)

    sizes, availability, total_stock = get_availability(SKU=SKU)

    embed = nextcord.Embed(title=name, url=product_url)
    embed.set_thumbnail(url=image_url)

    embed.add_field(name='SKU', value=SKU, inline=True)
    embed.add_field(name='Price', value=price, inline=True)
    embed.add_field(name='Site Name', value=site_name, inline=True)

    embed.add_field(name='Sizes', value=sizes, inline=True)
    embed.add_field(name='Availability', value=availability, inline=True)
    embed.add_field(name='Total Stock', value=total_stock, inline=True)

    return embed


if __name__ == '__main__':
    settings = get_settings()
    TOKEN = settings['Token']
    HEADERS = {'User-Agent': settings['User-Agent']}
    DELAY = settings['Delay']
    COMMAND_PREFIX = settings['Command Prefix']
    COMMAND_NAME = settings['Command Name']

    intents = nextcord.Intents.all()
    intents.message_content = True
    intents.members = True

    client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

    @client.event
    async def on_ready():
        print('------------------')
        print(' Bot is connected')
        print('------------------')
        #get_members(client=client)

    @client.command(name=COMMAND_NAME)
    async def adidas(ctx, *SKUS):
        settings = get_settings()[str(ctx.channel)]

        global SIZE_PREFIX, CURRENCY, COUNTRY_DOMAIN
        SIZE_PREFIX = settings['Size Prefix']
        currency = settings['Currency']
        CURRENCY = currency.replace('Â', '')
        COUNTRY_DOMAIN = settings['Country Domain']

        for SKU in SKUS:
            try:
                package = get_data(SKU=SKU)
                await ctx.send(embed=package)
            except:
                message = f'No data for {SKU} has been found'
                embed = nextcord.Embed(title=message)
                await ctx.send(embed=embed)
            time.sleep(DELAY)

    client.run(TOKEN)
