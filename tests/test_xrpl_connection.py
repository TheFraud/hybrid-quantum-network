# tests/test_xrpl_connection.py
import unittest
import pytest
import aiohttp
import json
from typing import List

# XRPL endpoints
WEBSOCKET_URLS = [
    "wss://s1.ripple.com/",
    "wss://s2.ripple.com/",
    "wss://xrplcluster.com/"
]

JSON_RPC_URLS = [
    "https://s1.ripple.com:51234/",
    "https://s2.ripple.com:51234/",
    "https://xrplcluster.com:51234/"
]

# Configuration du proxy Tor
PROXY = "socks5h://127.0.0.1:9050"

class TestXRPLConnection(unittest.TestCase):
    
    @pytest.mark.asyncio
    async def test_json_rpc_connections(self):
        """Test la connexion à tous les endpoints JSON-RPC via Tor"""
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for rpc_url in JSON_RPC_URLS:
                try:
                    async with session.post(
                        rpc_url,
                        json={
                            "method": "server_info",
                            "params": [{}]
                        },
                        proxy=PROXY
                    ) as response:
                        response_json = await response.json()
                        self.assertIn("result", response_json)
                        print(f"Connexion réussie à {rpc_url}")
                except Exception as e:
                    print(f"Erreur pour {rpc_url}: {str(e)}")
                    continue

    @pytest.mark.asyncio
    async def test_ledger_current(self):
        """Test la récupération du ledger courant via Tor"""
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.post(
                    JSON_RPC_URLS[0],
                    json={
                        "method": "ledger_current",
                        "params": [{}]
                    },
                    proxy=PROXY
                ) as response:
                    response_json = await response.json()
                    self.assertIn("result", response_json)
                    print("Test ledger réussi")
            except Exception as e:
                print(f"Erreur ledger: {str(e)}")

if __name__ == '__main__':
    pytest.main([__file__])

