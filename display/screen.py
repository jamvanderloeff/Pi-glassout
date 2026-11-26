#!/usr/bin/env python3

import asyncio
from websockets.asyncio.client import connect
import pygame
import json
import io
import os
import sys
import re

host = "10.1.1.90:8787"

myname = "cdu"

templates = []
panels = []
fragments = []


async def main():
    os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
    os.environ["SDL_KMSDRM_DEVICE_INDEX"] = "0"

    pygame.display.init()
    pygame.font.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    font = pygame.font.SysFont("Arial", 20)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            text_surface = font.render(f"Connecting Glassout at: {host}", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(320, 240))
            pygame.draw.rect(screen, (0, 0, 0), text_rect)
            screen.blit(text_surface, text_rect)

            pygame.display.flip()

            async with connect("ws://10.1.1.90:8787/ws?name=demo&appKey=demo&connectionType=viewer") as ws:
                print("connected")
                welcome = json.loads(await (ws.recv()))
                if welcome['type'] == "welcome":
                    print("welcome received")
                    # print(welcome)

                    if not welcome['state']['msfsDetected']:
                        print("MSFS not loaded")
                        sys.exit(1)

                    for profile in welcome['configs'][0]['profiles']:
                        print('checking profile')
                        if re.search(profile['aircraftPattern'], welcome['state']['aircraft']):
                            print("Matched aircraft")
                            templates.append(profile['templates'])
                    print(templates)

                    for template in templates:
                        print(template[0]['name'])
                        if template[0]['name'] == myname:
                            print('matching template found')
                            subscribeRequest = {'type': "subscribe.panel", 'panelId': template[0]['items'][0]['label']}
                            panelX = template[0]['items'][0]['x']
                            panelY = template[0]['items'][0]['y']
                            panelWidth = template[0]['items'][0]['width']
                            panelHeight = template[0]['items'][0]['height']

                    await ws.send(json.dumps(subscribeRequest))
                    async for message in ws:
                        if isinstance(message, str):
                            pass
                            # print(json.loads(message))
                        else:
                            print("binary received")
                            # print(type(message[0]))
                            surface = decode_binary(message)
                            print(panelX, panelY, panelWidth, panelHeight)
                            crop = pygame.Rect(panelX, panelY, panelWidth, panelHeight)
                            cropped = pygame.transform.smoothscale(surface, (panelWidth, panelHeight))

                            screen.blit(cropped, (panelX, panelY))
                            screen.blit(cropped, (panelX, panelY), special_flags=pygame.BLEND_RGB_ADD)

                            pygame.display.flip()

    except KeyboardInterrupt:
        print("exiting")
        pygame.quit()
        sys.exit()


def decode_binary(message):
    panelIdLen = message[0]
    panelId = message[1:1 + panelIdLen].decode('utf-8')
    frameNumber = int.from_bytes(message[1 + panelIdLen:1 + panelIdLen + 4], byteorder='little')
    w = int.from_bytes(message[1 + panelIdLen + 4:1 + panelIdLen + 4 + 2], byteorder='little')
    h = int.from_bytes(message[1 + panelIdLen + 6:1 + panelIdLen + 6 + 2], byteorder='little')
    # jpeg = buf.subarray(1 + panelIdLen + 16);
    imageStream = io.BytesIO(message[1 + panelIdLen + 16:])
    surface = pygame.image.load(imageStream, "JPG").convert()
    return surface


if __name__ == "__main__":
    asyncio.run(main())
