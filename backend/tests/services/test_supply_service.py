import pytest
from app.services.supply_service import SupplyService
from app.schemas.inventory import SupplyResponse


@pytest.fixture
def service() -> SupplyService:
    return SupplyService(supplier_url="https://supplier.example.com", api_key="sk-test-123456")


@pytest.mark.asyncio
async def test_request_restock_returns_supply_response(service: SupplyService):
    result = await service.request_restock(
        tenant_name="Acme Corp",
        product_sku="ELEC-LP15",
        product_name="Laptop Pro 15",
        quantity=50,
    )

    assert isinstance(result, SupplyResponse)


@pytest.mark.asyncio
async def test_request_restock_status_is_success(service: SupplyService):
    result = await service.request_restock(
        tenant_name="Acme Corp",
        product_sku="ELEC-LP15",
        product_name="Laptop Pro 15",
        quantity=50,
    )

    assert result.status == "success"


@pytest.mark.asyncio
async def test_request_restock_message_contains_details(service: SupplyService):
    result = await service.request_restock(
        tenant_name="Globex Industries",
        product_sku="FURN-SD01",
        product_name="Standing Desk",
        quantity=10,
    )

    assert "Globex Industries" in result.message
    assert "10" in result.message
    assert "Standing Desk" in result.message
    assert "FURN-SD01" in result.message


@pytest.mark.asyncio
async def test_request_restock_returns_reference_id(service: SupplyService):
    result = await service.request_restock(
        tenant_name="Wayne Enterprises",
        product_sku="NET-WR06",
        product_name="Wi-Fi Router",
        quantity=5,
    )

    assert result.external_reference_id == "MOCK-REQ-999"


@pytest.mark.asyncio
async def test_service_stores_config():
    svc = SupplyService(supplier_url="https://custom.url", api_key="my-key")

    assert svc.supplier_url == "https://custom.url"
    assert svc.api_key == "my-key"


@pytest.mark.asyncio
async def test_request_restock_logs_message(service: SupplyService, caplog):
    with caplog.at_level("INFO", logger="app.services.supply_service"):
        await service.request_restock(
            tenant_name="Acme Corp",
            product_sku="ELEC-LP15",
            product_name="Laptop Pro 15",
            quantity=25,
        )

    assert len(caplog.records) == 1
    log = caplog.records[0].message
    assert "https://supplier.example.com" in log
    assert "sk-t***" in log
    assert "Acme Corp requested 25 of product: Laptop Pro 15" in log
