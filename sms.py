from colorama import Fore, Style
from time import sleep
from os import system
from sms import SendSms
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import signal
import sys

servisler_sms = []
for attribute in dir(SendSms):
    attribute_value = getattr(SendSms, attribute)
    if callable(attribute_value):
        if attribute.startswith('__') == False:
            servisler_sms.append(attribute)

MAX_WORKERS = 50  # Aynı anda çalışacak maksimum thread
durduruldu = threading.Event()

def cikis_sinyali(sig, frame):
    print(Fore.RED + "\n\n[!] Durduruluyor...")
    durduruldu.set()
    sys.exit(0)

signal.signal(signal.SIGINT, cikis_sinyali)

def turbo_gonder(send_sms):
    """Tüm servisleri aynı anda paralel fırlatır, sonuç beklemez"""
    threads = []
    for fonk in servisler_sms:
        if durduruldu.is_set():
            break
        t = threading.Thread(target=getattr(send_sms, fonk), daemon=True)
        threads.append(t)
        t.start()
    return threads

def turbo_suresiz(send_sms):
    """Bitmeyen turbo döngüsü - her servisi sürekli paralel fırlatır"""
    print(Fore.YELLOW + "[*] Turbo mod: Sonsuz döngü. Ctrl+C ile durdurun.\n")
    print(Fore.GREEN + f"[*] {len(servisler_sms)} servis x {MAX_WORKERS} thread = patlatma modu\n" + Style.RESET_ALL)
    
    while not durduruldu.is_set():
        # Tüm servisleri aynı anda fırlat
        threads = []
        for fonk in servisler_sms:
            if durduruldu.is_set():
                break
            for _ in range(3):  # Her servisten 3 paralel thread
                if durduruldu.is_set():
                    break
                t = threading.Thread(target=getattr(send_sms, fonk), daemon=True)
                threads.append(t)
                t.start()
        
        # Thread'lerin bitmesini bekleme - hemen sonraki tura geç
        # Ama çok hızlı davranmaması için küçük bir bekleme
        sleep(0.1)

def turbo_belirli(send_sms, adet):
    """Belirli sayıda SMS gönder, mümkün olan en hızlı şekilde"""
    print(Fore.YELLOW + f"[*] Turbo mod: {adet} SMS hedefi\n")
    print(Fore.GREEN + f"[*] {len(servisler_sms)} servis x {MAX_WORKERS} thread\n" + Style.RESET_ALL)
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        while send_sms.adet < adet and not durduruldu.is_set():
            # Her servis için bir future ekle
            for fonk in servisler_sms:
                if send_sms.adet >= adet or durduruldu.is_set():
                    break
                futures.append(executor.submit(getattr(send_sms, fonk)))
            
            # Kısa bir bekleme ile sonuçları topla
            sleep(0.05)
            
            # Tamamlananları işaretle
            done = []
            for f in futures:
                if f.done():
                    done.append(f)
            for f in done:
                futures.remove(f)

while True:
    system("cls||clear")
    print("""{}
     ______                         _     
    |  ____|                       | |    
    | |__   _ __   ___  _   _  __ _| |__  
    |  __| | '_ \ / _ \| | | |/ _` | '_ \ 
    | |____| | | | (_) | |_| | (_| | | | |
    |______|_| |_|\___/ \__,_|\__, |_| |_|
                               __/ |      
                              |___/      
    
    Sms: {}           {}by {}@tingirifistik\n  
    """.format(Fore.LIGHTCYAN_EX, len(servisler_sms), Style.RESET_ALL, Fore.LIGHTRED_EX))
    
    try:
        menu = input(Fore.LIGHTMAGENTA_EX + " 1- SMS Gönder (Normal)\n\n 2- SMS Gönder (Turbo - Sonsuz)\n\n 3- SMS Gönder (Turbo - Sayılı)\n\n 4- Çıkış\n\n" + Fore.LIGHTYELLOW_EX + " Seçim: ")
        if menu == "":
            continue
        menu = int(menu)
    except ValueError:
        system("cls||clear")
        print(Fore.LIGHTRED_EX + "Hatalı giriş. Tekrar deneyin.")
        sleep(2)
        continue
    
    if menu == 1:  # NORMAL MOD
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Telefon numarası (başında +90 olmadan, 10 hane): " + Fore.LIGHTGREEN_EX, end="")
        tel_no = input()
        try:
            int(tel_no)
            if len(tel_no) != 10:
                raise ValueError
        except ValueError:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı telefon numarası.")
            sleep(2)
            continue
        
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Mail (boş = random): " + Fore.LIGHTGREEN_EX, end="")
        mail = input()
        
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "SMS adedi (boş = sonsuz): " + Fore.LIGHTGREEN_EX, end="")
        kere = input()
        kere = int(kere) if kere.strip() else None
        
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Aralık (saniye): " + Fore.LIGHTGREEN_EX, end="")
        aralik = float(input())
        
        system("cls||clear")
        sms = SendSms(tel_no, mail)
        print(Fore.GREEN + f"\n[*] Normal mod başladı - {kere if kere else 'SONSUZ'} SMS\n" + Style.RESET_ALL)
        
        try:
            while (kere is None or sms.adet < kere) and not durduruldu.is_set():
                for fonk in servisler_sms:
                    if (kere is not None and sms.adet >= kere) or durduruldu.is_set():
                        break
                    getattr(sms, fonk)()
                    sleep(aralik)
        except KeyboardInterrupt:
            pass
        
        print(Fore.CYAN + f"\n[*] Gönderilen: {sms.adet} SMS")
        print(Fore.LIGHTRED_EX + "\nMenüye dönmek için 'enter'...")
        input()
    
    elif menu == 2:  # TURBO - SONSUZ
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Telefon numarası (10 hane): " + Fore.LIGHTGREEN_EX, end="")
        tel_no = input()
        try:
            int(tel_no)
            if len(tel_no) != 10:
                raise ValueError
        except ValueError:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı telefon numarası.")
            sleep(2)
            continue
        
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Mail (boş = random): " + Fore.LIGHTGREEN_EX, end="")
        mail = input()
        
        system("cls||clear")
        durduruldu.clear()
        send_sms = SendSms(tel_no, mail)
        
        try:
            turbo_suresiz(send_sms)
        except KeyboardInterrupt:
            durduruldu.set()
            system("cls||clear")
            print(Fore.RED + f"\n[!] Durduruldu. Toplam: {send_sms.adet} SMS")
            print(Fore.LIGHTRED_EX + "\nMenüye dönmek için 'enter'...")
            input()
    
    elif menu == 3:  # TURBO - SAYILI
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Telefon numarası (10 hane): " + Fore.LIGHTGREEN_EX, end="")
        tel_no = input()
        try:
            int(tel_no)
            if len(tel_no) != 10:
                raise ValueError
        except ValueError:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı telefon numarası.")
            sleep(2)
            continue
        
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Mail (boş = random): " + Fore.LIGHTGREEN_EX, end="")
        mail = input()
        
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX + "Kaç SMS: " + Fore.LIGHTGREEN_EX, end="")
        adet = int(input())
        
        system("cls||clear")
        durduruldu.clear()
        send_sms = SendSms(tel_no, mail)
        
        try:
            turbo_belirli(send_sms, adet)
        except KeyboardInterrupt:
            durduruldu.set()
        
        system("cls||clear")
        print(Fore.CYAN + f"\n[*] Tamamlandı. Gönderilen: {send_sms.adet} SMS")
        print(Fore.LIGHTRED_EX + "\nMenüye dönmek için 'enter'...")
        input()
    
    elif menu == 4:
        system("cls||clear")
        print(Fore.LIGHTRED_EX + "Çıkış yapılıyor...")
        break
