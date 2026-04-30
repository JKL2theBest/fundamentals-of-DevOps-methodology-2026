import os
import time
import hvac
import sys


def wait_for_vault(client, max_retries=10):
    """Retry loop ожидания доступности Vault"""
    print("[*] Ожидание запуска Vault...")
    for i in range(max_retries):
        try:
            if client.is_authenticated():
                print(f"[+] Vault доступен (попытка {i+1})")
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    vault_addr = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")

    client = hvac.Client(url=vault_addr, token=vault_token)

    if not wait_for_vault(client):
        print("[!] Ошибка: Vault не ответил вовремя.")
        sys.exit(1)

    secret_path = "my_app_secrets"

    # Роль: АДМИН
    # В реальности приложение имеет права только на чтение
    # Секрет здесь исключительно для автоматизации проверки лабы одной командой docker compose up
    print("[Admin] Сохранение секрета в Vault...")
    client.secrets.kv.v2.create_or_update_secret(
        path=secret_path, secret=dict(db_password="SuperSecretPassword2026!")
    )

    # Роль: ПРИЛОЖЕНИЕ
    print("[App] Чтение секрета из Vault...")
    read_response = client.secrets.kv.v2.read_secret_version(path=secret_path, raise_on_deleted_version=True)
    password = read_response["data"]["data"]["db_password"]

    # App-level masking - чтобы предотвратить утечку в stdout/stderr.
    masked_password = password[:3] + "*" * (len(password) - 6) + password[-3:]

    print("========================================")
    print("Success! Приложение безопасно получило данные.")
    print(f"Пароль для использования в коде: {masked_password}")
    print("========================================")


if __name__ == "__main__":
    main()
