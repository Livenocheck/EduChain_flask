import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# === Настройки ===
RPC_URL = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
WALLET_ADDRESS = Web3.to_checksum_address(WALLET_ADDRESS)

# Проверяем, что ключи заданы
assert PRIVATE_KEY, "Ошибка: PRIVATE_KEY не задан в .env"
assert WALLET_ADDRESS, "Ошибка: WALLET_ADDRESS не задан в .env"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("❌ Не удалось подключиться к Sepolia")

print(f"✅ Подключено к Sepolia")

# === Загружаем ABI и Bytecode ===
with open("EduNFT.abi", "r") as f:
    abi = json.load(f)

with open("EduNFT.bin", "r") as f:
    bytecode = f.read().strip()

# Проверяем, что bytecode начинается с 0x (если нет — добавляем)
if not bytecode.startswith("0x"):
    bytecode = "0x" + bytecode

# === Создаём контракт ===
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# === Готовим транзакцию деплоя ===
nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
tx = Contract.constructor().build_transaction({
    'chainId': 11155111,  # Sepolia
    'gas': 3000000,       # Достаточно для ERC721
    'gasPrice': w3.eth.gas_price,
    'nonce': nonce,
})

# === Подписываем и отправляем ===
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"⏳ Деплой запущен: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")

# === Ждём подтверждения ===
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
if receipt.status != 1:
    raise Exception("❌ Транзакция деплоя отклонена")

contract_address = receipt.contractAddress
print(f"✅ Контракт успешно задеплоен: {contract_address}")
print(f"🔍 Посмотреть в Etherscan: https://sepolia.etherscan.io/address/{contract_address}")

# === Сохраняем адрес для последующих скриптов ===
with open(".env", "w") as f:
    f.write(f'ETH_NFT_CONTRACT_ADDRESS={contract_address}')

print("\n✨ Готово! Теперь можно ментить NFT через mint_nft.py")