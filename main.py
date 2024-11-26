import requests
import base64
import json


def get_transaction(api_key, address, lt, tx_hash):
    """Получить транзакцию через Toncenter API"""
    url = "https://toncenter.com/api/v2/getTransactions"
    params = {
        "address": address,
        "lt": lt,
        "hash": tx_hash,
        # "api_key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result.get("ok", False):
            return result["result"][0]
        else:
            print("Ошибка API:", result.get("error", "Неизвестная ошибка"))
            return None
    else:
        print("HTTP ошибка:", response.status_code, response.text)
        return None


def parse_transaction(raw_transaction):
    transaction = dict(address=raw_transaction['address']['account_address'],
                       timestamp=raw_transaction['utime'],
                       lt=raw_transaction['transaction_id']['lt'],
                       hash=raw_transaction['transaction_id']['hash'],
                       fee=int(raw_transaction['fee']),
                       storage_fee=int(raw_transaction['storage_fee']),
                       other_fee=int(raw_transaction['other_fee']),
                       value=int(raw_transaction['in_msg']['value']),
                       source=raw_transaction['in_msg']['source'],
                       destination=raw_transaction['in_msg']['destination'])
    # message=raw_transaction['in_msg']['message'])

    # Парсинг сообщений
    transaction["out_msgs"] = raw_transaction.get("out_msgs", [])

    return transaction


def get_swap_data(transaction):
    """Парсит транзакцию в удобный вид"""
    amount = json.loads(transaction)["value"]
    tr_address = json.loads(transaction)["address"]
    if json.loads(transaction)["address"] == json.loads(transaction)["destination"]:
        operation = "sell"
        token = json.loads(transaction)["source"]
    elif json.loads(transaction)["address"] == json.loads(transaction)["source"]:
        operation = "buy"
        token = json.loads(transaction)["destination"]
    else:
        operation = None
        token = None

    if str(amount).isdigit:
        amount = float(amount) / 1e9

    return {'operation': operation,
            'token': token,
            'value': amount,
            'address': tr_address}

if __name__ == "__main__":
    api_key = "ВАШ_API_KEY"  # API-ключ Toncenter, необязательно
    address = ""  # Адрес кошелька
    lt = ""  # Logical Time: int
    tx_hash = ""  # Хэш транзакции, можно без него

    # Получение транзакции
    raw_transaction = get_transaction(api_key, address, lt, tx_hash)

    if raw_transaction:
        # Парсинг транзакции
        parsed_transaction = parse_transaction(raw_transaction)
        parsed_transaction = json.dumps(parsed_transaction, indent=4)
        swap_data = get_swap_data(parsed_transaction)  # красивый вид
        operation = swap_data["operation"]
        token = swap_data["token"]
        value = swap_data["value"]
        address = swap_data["address"]
        print(f"Операция {operation}\n"
              f"Токен {token}\n"
              f"Количество {value}\n"
              f"Адрес {address}\n")

    else:
        print("Не удалось получить данные транзакции.")
