import aiohttp
import asyncio
import itertools

from sqlalchemy import create_engine, Column, Text, Boolean, DateTime,  Integer
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

import pathlib


Base = declarative_base()


class Host(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True)
    addr = Column(Text)
    traceback_status = Column(Integer)


class IPV4Addr:
    def __init__(self, a=0, b=0, c=0, d=0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    @classmethod
    def parse_from_string(cls, string: str):
        a, b, c, d = string.split(".")
        return IPV4Addr(a, b, c, d)

    def __repr__(self):
        """
        переводит объект в строку
        :return:
        """
        def repr_unit(val) -> str:
            # проверка значения на range
            if not val in range(0, 256):
                raise ValueError(f"Value of ip chunk is {val}. Should be in range 0 <= x <= 255")

            string_repr = str(val)
            return string_repr

        return "".join(f"{repr_unit(val)}." for val in [self.a, self.b, self.c, self.d])[:-1]

    def __iter__(self):
        # перебор всех возможных значений IPv4
        for val in itertools.combinations_with_replacement(list(range(0, 256)), 4):
            if len(val) < 4:
                continue

            for mutation in itertools.permutations(val, 4):
                self.a, self.b, self.c, self.d = mutation
                yield repr(self)

        raise StopIteration()


class WWWCrawler:
    session: aiohttp.ClientSession

    @classmethod
    async def handle(cls, addr: str) -> None:
        host_obj = session.query(Host).filter_by(addr=addr).all()
        if host_obj:
            return
        host_obj = host_obj[0] if host_obj else Host(addr=addr)
        session.add(host_obj)

        # print(f"requesting {addr}")
        try:
            async with cls.session.get(addr) as resp:
                print(f"{resp.status} from {addr}")
                host_obj.traceback_status = resp.status

        except aiohttp.client_exceptions.ClientConnectorError:
            # print(f"requesting {addr}... aiohttp.client_exceptions.ClientConnectorError")
            pass
        except asyncio.exceptions.TimeoutError:
            # print(f"requesting {addr}... asyncio.exceptions.TimeoutError")
            pass

        except aiohttp.client_exceptions.ClientOSError:
            # print(f"requesting {addr}... aiohttp.client_exceptions.ClientOSError")
            pass

        except aiohttp.client_exceptions.ServerDisconnectedError:
            # print(f"requesting {addr}... aiohttp.client_exceptions.ServerDisconnectedError")
            pass

        except Exception as ex:
            # print(f"requesting {addr}... {ex}")
            pass


    @classmethod
    async def start(cls):
        timeout = aiohttp.ClientTimeout(total=5)
        client_session = aiohttp.ClientSession(timeout=timeout)
        cls.session = client_session

        tasks = []

        for IP in IPV4Addr():
            http_addr = "http://" + IP + ":80"
            https_addr = "https://" + IP + ":443"

            if len(tasks) == 100:
                await asyncio.gather(
                    *tasks
                )
                tasks = []
                cls.session.commit()

            tasks.append(cls.handle(http_addr))
            tasks.append(cls.handle(https_addr))

        cls.session.close()


def start():
    engine = create_engine("postgresql://postgres:homohomozek@161.35.63.104:5432/siteindexer")

    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    globals().update({"session": session})

    loop = asyncio.get_event_loop()
    loop.run_until_complete(WWWCrawler.start())


if __name__ == "__main__":
    # engine = create_engine("sqlite:///db.sqlite3")
    start()



