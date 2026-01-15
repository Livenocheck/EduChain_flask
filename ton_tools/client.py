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
    print(f"DEBUG: Sending {jetton_amount} to {to_address}")
    print(f"DEBUG: PROJECT_WALLET_ADDRESS={os.getenv('PROJECT_WALLET_ADDRESS')}")
    print(f"DEBUG: JETTON_MASTER_ADDRESS={os.getenv('JETTON_MASTER_ADDRESS')}")
    
    mnemonics = os.getenv("PROJECT_WALLET_SEED", "").split()
    private_key = mnemonic_to_private_key(mnemonics)
    wallet_address = os.getenv("PROJECT_WALLET_ADDRESS")
    jetton_master = os.getenv("JETTON_MASTER_ADDRESS")
    
    client = TonlibClient()
    await client.init()
    print("DEBUG: Client initialized")
    
    try:
        # Получаем Jetton-кошелёк получателя
        result = await client.raw_run_method(
            address=jetton_master,
            method="get_wallet_address",
            stack=[["tvm.Slice", to_address]]
        )
        jetton_wallet = result["stack"][0][1]
        print(f"DEBUG: Jetton wallet={jetton_wallet}")
        
        # Отправляем транзакцию
        await client.raw_create_and_send_message(
            sender=wallet_address,
            destination=jetton_wallet,
            amount=int(0.02 * 10**9),
            payload={"body": ""},
            secret=private_key
        )
        print("DEBUG: Transaction sent!")
        
    except Exception as e:
        print(f"ERROR in send_jetton: {str(e)}")
        raise e
    finally:
        await client.close()