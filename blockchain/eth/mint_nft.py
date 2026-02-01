import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

def minter(to_address: str, token_uri: str):

    # === Настройки ===
    RPC_URL = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    WALLET_ADDRESS = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))

    # Адрес получателя (может совпадать с WALLET_ADDRESS)
    RECIPIENT = to_address  # ← ЗАМЕНИ НА АДРЕС СТУДЕНТА, временно!!!

    # URL твоего metadata.json (должен быть доступен по HTTPS)
    TOKEN_URI = token_uri

    # === Подключение ===
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert w3.is_connected(), "❌ Не подключился к Sepolia"

    abi_file = os.path.join('blockchain', 'eth', 'EduNFT.abi')

    # === Загрузка ABI ===
    with open(abi_file, "r") as f:
        abi = json.load(f)

    # === Чтение адреса контракта ===
    contract_address = Web3.to_checksum_address(os.getenv('ETH_NFT_CONTRACT_ADDRESS'))

    contract = w3.eth.contract(address=contract_address, abi=abi)

    # === Проверка баланса ===
    balance = w3.eth.get_balance(WALLET_ADDRESS)
    print(f"💰 Баланс: {w3.from_wei(balance, 'ether')} ETH")

    # === Оценка газа (опционально) ===
    try:
        gas_estimate = contract.functions.mint(RECIPIENT, TOKEN_URI).estimate_gas({
            'from': WALLET_ADDRESS
        })
        gas_limit = gas_estimate + 20000
    except Exception as e:
        print("⚠️ Не удалось оценить газ, используем 200000")
        gas_limit = 200000

    # === Подготовка транзакции ===
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx = contract.functions.mint(RECIPIENT, TOKEN_URI).build_transaction({
        'chainId': 11155111,
        'gas': gas_limit,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })

    # === Подпись и отправка ===
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex()

    print(f"⏳ Минт запущен: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")

    # === Ожидание подтверждения ===
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status != 1:
        raise Exception("❌ Транзакция минта отклонена")

    print(f"✅ NFT успешно заминчен и отправлен на {RECIPIENT}")

    return tx_hash_hex
