import os
import asyncio
import hashlib
from pytonlib import TonlibClient

def mnemonic_to_private_key(mnemonic_words):
    """Конвертирует мнемонику в приватный ключ"""
    mnemonic = " ".join(mnemonic_words)
    salt = "mnemonic"
    seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode(), salt.encode(), 2048, 64)
    return seed[:32]

async def mint_nft_to(owner_address: str, metadata_url: str):
    """
    Минтит NFT через Collection Contract
    Использует стандартный метод mint для TEP-62 Collection
    """
    mnemonics = os.getenv("PROJECT_WALLET_SEED", "").split()
    if len(mnemonics) != 24:
        raise ValueError("SEED must contain 24 words")
    private_key = mnemonic_to_private_key(mnemonics)
    
    wallet_address = os.getenv("PROJECT_WALLET_ADDRESS")
    collection_address = os.getenv("NFT_COLLECTION_ADDRESS")
    
    if not wallet_address or not collection_address:
        raise ValueError("WALLET or COLLECTION address not set")
    
    client = TonlibClient()
    await client.init()
    
    try:
        # Вызываем метод mint напрямую через run_get_method
        # Стек для метода mint: [owner_address, metadata_url]
        stack = [
            ["tvm.Slice", owner_address],
            ["tvm.Slice", metadata_url]
        ]
        
        # Создаём внешнее сообщение для минтинга
        result = await client.raw_create_and_send_message(
            sender=wallet_address,
            destination=collection_address,
            amount=int(0.05 * 10**9),
            payload={"method": "mint", "params": stack},
            secret=private_key
        )
        
        await client.close()
        return result.get("transaction_hash", "success")
        
    except Exception as e:
        await client.close()
        raise e