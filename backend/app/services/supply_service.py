import asyncio
import logging
from app.schemas.inventory import SupplyResponse

logger = logging.getLogger(__name__)

class SupplyService:
    def __init__(self, supplier_url: str, api_key: str):
        """
        Initialize the service with external configurations.
        """
        self.supplier_url = supplier_url
        self.api_key = api_key

    async def request_restock(self, tenant_name: str, product_sku: str, product_name: str, quantity: int) -> SupplyResponse:
        """
        Simulates sending a restock request to an external supplier API.
        """
        await asyncio.sleep(1.5) 
        
        message = f"{tenant_name} requested {quantity} of product: {product_name} (SKU: {product_sku})"
        
        logger.info(f"Sending to {self.supplier_url} using key {self.api_key[:4]}*** : {message}")
        
        return SupplyResponse(
            status="success",
            message=message,
            external_reference_id="MOCK-REQ-999"
        )