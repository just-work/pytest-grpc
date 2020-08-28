import pytest
import grpc
import threading
import asyncio

from .example_pb2 import EchoRequest, Empty
from .servicer import Servicer
from .example_pb2_grpc import add_EchoServiceServicer_to_server, EchoServiceStub


@pytest.fixture
def grpc_add_to_server():
    return add_EchoServiceServicer_to_server


@pytest.fixture
def grpc_servicer():
    return Servicer


@pytest.fixture
def grpc_stub_cls():
    yield EchoServiceStub


# Synchronous Stub and Synchronous Server

def test_some(grpc_stub, grpc_server):
    request = EchoRequest()
    response = grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'


def test_error(grpc_stub, grpc_server):
    request = EchoRequest()
    with pytest.raises(grpc.RpcError):
        grpc_stub.error_handler(request)


def test_blocking(grpc_stub, grpc_server):
    stream = grpc_stub.blocking(Empty())
    def call_unblock():
        grpc_stub.unblock(Empty())
        grpc_stub.unblock(Empty())
    t = threading.Thread(target=call_unblock)
    t.start()
    for resp in stream:
        pass
    t.join()


# Asynchronous Stub and Asynchronous Server

@pytest.mark.asyncio
async def test_some_async(aio_grpc_stub, aio_grpc_server):
    request = EchoRequest()
    response = await aio_grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'

@pytest.mark.asyncio
async def test_error_async(aio_grpc_stub, aio_grpc_server):
    request = EchoRequest()
    with pytest.raises(grpc.RpcError):
        response = await aio_grpc_stub.error_handler(request)

@pytest.mark.asyncio
async def test_blocking_async(event_loop, aio_grpc_stub, aio_grpc_server):
    async def call_unblock():
        await aio_grpc_stub.unblock(Empty())

    async def call_block():
        async for resp in aio_grpc_stub.blocking(Empty()):
            pass

    asyncio.gather(
        call_unblock(),
        call_unblock(),
        call_block(),
    )


# Incorrect fixtures requested

@pytest.mark.xfail(strict=True)
@pytest.mark.asyncio
async def test_sync_fixture_async_test(grpc_stub, grpc_server):
    pass


@pytest.mark.xfail(strict=True)
def test_async_fixture_sync_test(aio_grpc_stub, aio_grpc_server):
    pass
