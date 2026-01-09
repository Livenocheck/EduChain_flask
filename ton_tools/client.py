import os
import asyncio
import hashlib
from pytonlib import TonlibClient

def mnemonic_to_private_key(mnemonic_words):
    mnemonic = " ".join(mnemonic_words)
    salt = "mnemonic"
    seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode(), salt.encode(), 2048, 64)
    return seed[:32]

async def send_jetton(to_address: str, jetton_amount: int):
    """
    Отправляет Jetton через стандартный метод transfer
    """
    mnemonics = os.getenv("PROJECT_WALLET_SEED", "").split()
    private_key = mnemonic_to_private_key(mnemonics)
    wallet_address = os.getenv("PROJECT_WALLET_ADDRESS")
    jetton_master = os.getenv("JETTON_MASTER_ADDRESS")
    
    client = TonlibClient()
    await client.init()
    
    try:
        # Получаем адрес Jetton-кошелька получателя
        jetton_wallet_result = await client.raw_run_method(
            address=jetton_master,
            method="get_wallet_address",
            stack=[["tvm.Slice", to_address]]
        )
        
        # Парсим адрес из результата (формат зависит от контракта)
        jetton_wallet = jetton_wallet_result["stack"][0][1]
        
        # Отправляем transfer на Jetton-кошелёк
        transfer_payload = {
            "method": "transfer",
            "params": [
                ["num", jetton_amount],
                ["tvm.Slice", to_address],
                ["tvm.Slice", wallet_address],  # response_destination
                ["num", 1],  # forward_amount
                ["tvm.Cell", None]  # forward_payload
            ]
        }
        
        result = await client.raw_create_and_send_message(
            sender=wallet_address,
            destination=jetton_wallet,
            amount=int(0.02 * 10**9),
            payload=transfer_payload,
            secret=private_key
        )
        
        await client.close()
        return result.get("transaction_hash", "success")
        
    except Exception as e:
        await client.close()
        raise e