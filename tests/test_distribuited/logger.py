import asyncio
from nats.aio.client import Client as NATS

async def run(loop):
    nc = NATS()

    await nc.connect("0.0.0.0:4222", loop=loop)

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("DEBUG: subject: '{subject}'\n data:{data}\n".format(
            subject=subject, data=data))

    sid = await nc.subscribe(">", cb=message_handler)


    await asyncio.wait_for(asyncio.Future(),None)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))