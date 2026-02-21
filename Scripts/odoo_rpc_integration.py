#!/usr/bin/env python3
"""
Odoo ERP Integration - Gold Tier Business Intelligence
Connects to self-hosted Odoo Community via JSON-RPC API for accounting and revenue tracking.
"""

import json
import requests
import logging
from Scripts.retry_handler import with_retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Odoo Configuration
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo_db"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"  # Change after first login


class OdooRPCClient:
    """Client for interacting with Odoo via JSON-RPC API."""

    def __init__(self, url=ODOO_URL, db=ODOO_DB, username=ODOO_USERNAME, password=ODOO_PASSWORD):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.session_id = None

    @with_retry(max_attempts=3, base_delay=2, max_delay=10)
    def _call_jsonrpc(self, service, method, *args):
        """
        Make a JSON-RPC call to Odoo.

        Args:
            service (str): Service name ('common' or 'object')
            method (str): Method to call
            *args: Arguments to pass to the method

        Returns:
            Response data from Odoo

        Raises:
            requests.RequestException: If connection fails
            ValueError: If Odoo returns an error
        """
        endpoint = f"{self.url}/jsonrpc"

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args
            },
            "id": 1
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()

        if "error" in result:
            error_msg = result["error"].get("data", {}).get("message", "Unknown error")
            raise ValueError(f"Odoo RPC Error: {error_msg}")

        return result.get("result")

    @with_retry(max_attempts=3, base_delay=2, max_delay=10)
    def authenticate(self):
        """
        Authenticate with Odoo and obtain user ID.

        Returns:
            int: User ID if successful, None otherwise
        """
        try:
            logger.info(f"[ODOO] Authenticating as {self.username}...")

            self.uid = self._call_jsonrpc(
                "common",
                "authenticate",
                self.db,
                self.username,
                self.password,
                {}
            )

            if self.uid:
                logger.info(f"[ODOO] Authentication successful. User ID: {self.uid}")
                return self.uid
            else:
                logger.error("[ODOO] Authentication failed. Invalid credentials.")
                return None

        except Exception as e:
            logger.error(f"[ODOO] Authentication error: {e}")
            raise

    def _execute_kw(self, model, method, args=None, kwargs=None):
        """
        Execute a method on an Odoo model.

        Args:
            model (str): Model name (e.g., 'account.move')
            method (str): Method to execute (e.g., 'search_read')
            args (list): Positional arguments
            kwargs (dict): Keyword arguments

        Returns:
            Result from Odoo
        """
        if not self.uid:
            raise ValueError("Not authenticated. Call authenticate() first.")

        args = args or []
        kwargs = kwargs or {}

        return self._call_jsonrpc(
            "object",
            "execute_kw",
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs
        )

    @with_retry(max_attempts=3, base_delay=2, max_delay=10)
    def create_invoice(self, partner_name, amount, description="Service Invoice"):
        """
        Create an invoice in Odoo.

        Args:
            partner_name (str): Customer name
            amount (float): Invoice amount
            description (str): Invoice description

        Returns:
            int: Invoice ID if successful, None otherwise
        """
        try:
            if not self.uid:
                self.authenticate()

            logger.info(f"[ODOO] Creating invoice for {partner_name}: ${amount}")

            # Search for partner (customer)
            partner_ids = self._execute_kw(
                'res.partner',
                'search',
                [[['name', '=', partner_name]]],
                {'limit': 1}
            )

            if not partner_ids:
                # Create partner if not exists
                logger.info(f"[ODOO] Partner '{partner_name}' not found. Creating...")
                partner_id = self._execute_kw(
                    'res.partner',
                    'create',
                    [{
                        'name': partner_name,
                        'customer_rank': 1
                    }]
                )
            else:
                partner_id = partner_ids[0]

            # Create invoice
            invoice_id = self._execute_kw(
                'account.move',
                'create',
                [{
                    'partner_id': partner_id,
                    'move_type': 'out_invoice',
                    'invoice_line_ids': [(0, 0, {
                        'name': description,
                        'quantity': 1,
                        'price_unit': amount
                    })]
                }]
            )

            logger.info(f"[ODOO] Invoice created successfully. ID: {invoice_id}")
            return invoice_id

        except Exception as e:
            logger.error(f"[ODOO] Error creating invoice: {e}")
            return None

    @with_retry(max_attempts=3, base_delay=2, max_delay=10)
    def get_revenue_metrics(self):
        """
        Retrieve revenue metrics from Odoo accounting system.

        Returns:
            dict: Revenue metrics including total revenue, invoice count, etc.
        """
        try:
            if not self.uid:
                self.authenticate()

            logger.info("[ODOO] Fetching revenue metrics...")

            # Search for posted invoices (state = 'posted')
            invoices = self._execute_kw(
                'account.move',
                'search_read',
                [[['move_type', '=', 'out_invoice'], ['state', '=', 'posted']]],
                {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'state']}
            )

            total_revenue = sum(inv['amount_total'] for inv in invoices)
            invoice_count = len(invoices)

            metrics = {
                'total_revenue': total_revenue,
                'invoice_count': invoice_count,
                'invoices': invoices,
                'source': 'odoo_erp'
            }

            logger.info(f"[ODOO] Revenue metrics retrieved: ${total_revenue:.2f} from {invoice_count} invoices")
            return metrics

        except Exception as e:
            logger.error(f"[ODOO] Error fetching revenue metrics: {e}")
            raise


# Convenience functions for direct use
def authenticate():
    """Authenticate with Odoo and return client instance."""
    client = OdooRPCClient()
    client.authenticate()
    return client


def create_invoice(partner_name, amount, description="Service Invoice"):
    """Create an invoice in Odoo."""
    client = OdooRPCClient()
    client.authenticate()
    return client.create_invoice(partner_name, amount, description)


def get_revenue_metrics():
    """Get revenue metrics from Odoo."""
    client = OdooRPCClient()
    client.authenticate()
    return client.get_revenue_metrics()


# Example usage and testing
if __name__ == '__main__':
    print("Testing Odoo RPC Integration...\n")

    try:
        # Test authentication
        client = OdooRPCClient()
        uid = client.authenticate()

        if uid:
            print(f"✓ Authentication successful (UID: {uid})\n")

            # Test get revenue metrics
            print("Fetching revenue metrics...")
            metrics = client.get_revenue_metrics()
            print(f"✓ Total Revenue: ${metrics['total_revenue']:.2f}")
            print(f"✓ Invoice Count: {metrics['invoice_count']}\n")

            # Test create invoice (commented out to avoid creating test data)
            # invoice_id = client.create_invoice("Test Client", 1500.00, "Consulting Services")
            # print(f"✓ Invoice created: {invoice_id}\n")

        else:
            print("✗ Authentication failed\n")

    except Exception as e:
        print(f"✗ Error: {e}\n")
        print("Note: Make sure Odoo is running (docker-compose up -d)")
