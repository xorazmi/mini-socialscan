import requests
import sys
import phonenumbers
import socket
from phonenumbers import carrier   # Tel. operatorini topish uchun
from phonenumbers import geocoder  # Geografik joylashuvni topish uchun

# ----------------------------------------------------
# ASCII Art Banner
# ----------------------------------------------------

banner = """
  /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$  /$$$$$$  /$$        /$$$$$$   /$$$$$$   /$$$$$$  /$$   /$$
 /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/ /$$__  $$| $$       /$$__  $$ /$$__  $$ /$$__  $$| $$$ | $$
| $$  \__/| $$  \ $$| $$  \__/  | $$  | $$  \ $$| $$      | $$  \__/| $$  \__/| $$  \ $$| $$$$| $$
|  $$$$$$ | $$  | $$| $$        | $$  | $$$$$$$$| $$      |  $$$$$$ | $$      | $$$$$$$$| $$ $$ $$
 \____  $$| $$  | $$| $$        | $$  | $$__  $$| $$       \____  $$| $$      | $$__  $$| $$  $$$$
 /$$  \ $$| $$  | $$| $$    $$  | $$  | $$  | $$| $$       /$$  \ $$| $$    $$| $$  | $$| $$\  $$$
|  $$$$$$/|  $$$$$$/|  $$$$$$/ /$$$$$$| $$  | $$| $$$$$$$$|  $$$$$$/|  $$$$$$/| $$  | $$| $$ \  $$
 \______/  \______/  \______/ |______/|__/  |__/|________/ \______/  \______/ |__/  |__/|__/  \__/


telegram chanel: https://t.me/cybersecattack
"""

# ----------------------------------------------------
# 1. Username Tekshirish Funksiyasi (01)
# ----------------------------------------------------
# ----------------------------------------------------
# 1. Username Tekshirish Funksiyasi (01) - OPTIMALLASHGAN
# ----------------------------------------------------
def check_user(username, platform_url):
    """Berilgan platformada foydalanuvchi nomini tekshiradi."""
    
    platform_name = platform_url.split('//')[1].split('.')[0].upper()
    found_urls = []
    
    # 1. Mutatsiyalarni yaratish
    usernames_to_check = generate_mutations(username)

    # 2. Har bir variantni tekshirish
    for target_name in usernames_to_check:
        full_url = platform_url + target_name
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(full_url, headers=headers, timeout=8)
            
            # --- TELEGRAM VA MURAKKAB SAYTLAR UCHUN MAXSUS LOGIKA ---
            if platform_name == 'T' or platform_name == 'TELEGRAM':
                # Telegramda 200 status kodi ham bor yoki yo'qligini aniq ko'rsatmaydi.
                # Uning sahifasida 'Username not found' so'zi borligini tekshiramiz.
                if 'Username not found' in response.text or 'Sorry, this link is invalid' in response.text:
                    continue # Tekshirishni davom ettirish
                else:
                    found_urls.append((platform_name, full_url))
                    break # Topildi, keyingi mutatsiyaga o'tish shart emas

            # --- Qolgan saytlar uchun odatiy 200/404 tekshiruvi ---
            elif response.status_code == 200:
                # Kichik tekshiruv: agar sahifa butunlay bo'sh bo'lmasa
                if len(response.text) > 50: 
                    found_urls.append((platform_name, full_url))
                    break # Topildi, keyingi mutatsiyaga o'tish shart emas
            
            # Agar 404 bo'lsa, davom etish
            elif response.status_code == 404:
                continue

        except requests.exceptions.RequestException:
            continue # Xatolik bo'lsa, boshqa mutatsiyani tekshirish

    # 3. Natijani qaytarish
    if found_urls:
        platform, url = found_urls[0] # Birinchi topilgan variantni olamiz
        return f"[+] {platform}: Topildi! (Variant: {url.split(platform_url)[1]})"
    else:
        return f"[-] {platform_name}: Topilmadi (Barcha {len(usernames_to_check)} variant tekshirildi)."

# ----------------------------------------------------
# 2. Google Orqali YouTube Kanalni Tekshirish
# ----------------------------------------------------
def search_youtube_channel(username):
    """Google orqali berilgan username asosida YouTube kanalini qidiradi."""
    
    # Qidiruv so'rovi (faqat youtube.com sayti ichida)
    search_query = f"site:youtube.com @{username}"
    
    # Google'ga so'rov yuborish (bu joyda API kerak emas, oddiy link yetarli)
    google_url = f"https://www.google.com/search?q={search_query}"
    
    try:
        # Boshqa saytlar kabi tekshirish. Google odatda 200 (OK) qaytaradi.
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(google_url, headers=headers, timeout=10)
        
        # Google qidiruv natijalarida kanal sarlavhasi (yoki profil nomi) borligini tekshiramiz.
        # Bu juda oddiy va barqaror bo'lmagan usul, ammo hozircha ishonchli
        if username.lower() in response.text.lower() and "youtube.com/@" in response.text:
            return f"[+] YOUTUBE: Topildi! (Google orqali: {username})"
        else:
            return f"[-] YOUTUBE: Topilmadi (Google orqali tekshirildi)."

    except requests.exceptions.RequestException:
        return "[X] YOUTUBE: Aloqa uzildi yoki vaqt tugadi."

# ----------------------------------------------------
# 3. Username Variantlarini Yaratish Funksiyasi
# ----------------------------------------------------
def generate_mutations(username):
    """Kiritilgan username'dan turli variantlarni (mutatsiyalarni) yaratadi."""
    mutations = set()
    
    # 1. Asl nomi (Katta/Kichik harf emas, saytlar buni odatda e'tiborsiz qoldiradi)
    mutations.add(username)
    
    # 2. Pastki chiziqsiz variant (eldormatmurodov)
    no_underscore = username.replace('_', '')
    mutations.add(no_underscore)
    
    # 3. Oldiga/orqasiga pastki chiziq qo'shish (eldor_matmurodov_ yoki _eldor_matmurodov)
    if not username.startswith('_'):
        mutations.add('_' + username)
    if not username.endswith('_'):
        mutations.add(username + '_')

    # 4. So'zlar orasiga pastki chiziq qo'shish (EldorMatmurodov -> Eldor_Matmurodov)
    import re
    words = re.findall('[A-Z][a-z]*', username.replace('_', ''))
    if len(words) > 1:
        mutated_username = '_'.join([w.lower() for w in words])
        mutations.add(mutated_username)

    # 5. Kichik harf variantlari
    mutations.add(username.lower())
    mutations.add(no_underscore.lower())

    # Takrorlanishni tozalash va to'g'ri ro'yxat qaytarish
    return sorted(list(mutations))

# ----------------------------------------------------
# 4. Telefon Raqamni Tekshirish Funksiyasi (02)
# ----------------------------------------------------
def check_phone(phone_number):
    """Berilgan raqam haqida bazaviy ma'lumotlarni topadi."""

    try:
        # Raqamni tahlil qilish
        parsed_number = phonenumbers.parse(phone_number)
        
        if not phonenumbers.is_valid_number(parsed_number):
            return "[X] Xato: Berilgan raqam to'g'ri (valid) emas."
        
        # Ma'lumotlarni chiqarish
        is_possible = phonenumbers.is_possible_number(parsed_number)
        country = phonenumbers.region_code_for_number(parsed_number)
        
        # Alohida import qilingan 'carrier' va 'geocoder' ishlatilmoqda
        operator = carrier.name_for_number(parsed_number, "en")       
        location = geocoder.description_for_number(parsed_number, "en")
        
        # Natijalarni birlashtirish
        result = f"\n[i] Tekshiruv natijalari: {phone_number}\n"
        result += f"    - Mumkin bo'lgan raqammi: {is_possible}\n"
        result += f"    - Mamlakat kodi (Region): {country}\n"
        result += f"    - Operator (Carrier): {operator}\n"
        result += f"    - Geografik mintaqa: {location}\n"
        return result

    except phonenumbers.phonenumberutil.NumberParseException:
        return f"[X] Xato: Raqamni tahlil qilib bo'lmadi. (+998YYXXXXXXX kabi to'liq yozing)."


# ----------------------------------------------------
# 5. Local IP ni Topish Funksiyasi
# ----------------------------------------------------
def get_local_ip():
    """Tizimning ichki (Local) IP manzilini topadi."""
    try:
        # Haqiqiy tashqi aloqa o'rnatmasdan, faqat socket yordamida manzildan so'raymiz
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS serveriga ulanishga urinish
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "NOMA'LUM (Aloqa yo'q)"

# ----------------------------------------------------
# 6. IP Manzilni Tekshirish Funksiyasi (03)
# ----------------------------------------------------
def check_ip(target_ip):
    """Berilgan IP yoki Domen nomini tekshirib, geolokatsiyasini topadi."""

    # Local IP diapazonlari (RFC 1918)
    local_ranges = (
        '10.',
        '192.168.',
        '172.16.', '172.17.', '172.18.', '172.19.', 
        '172.20.', '172.21.', '172.22.', '172.23.', 
        '172.24.', '172.25.', '172.26.', '172.27.', 
        '172.28.', '172.29.', '172.30.', '172.31.',
        '127.0.0.1' # Loopback
    )

    # 1. LOCAL IP Tekshiruvi
    if target_ip.startswith(local_ranges):
        return f"\n[!] OGOHLANTIRISH: {target_ip} - Bu **Local (Ichki) IP Manzil**.\n    Global joylashuv ma'lumotlari mavjud emas."


    # 2. PUBLIC IP/DOMEN Tekshiruvi
    api_url = f"http://ip-api.com/json/{target_ip}?fields=status,message,country,city,lat,lon,isp,query"
    
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'success':
            result = f"\n[i] IP Geolocation Natijalari: {data['query']}\n"
            result += f"    - Mamlakat: {data['country']}\n"
            result += f"    - Shahar: {data['city']}\n"
            result += f"    - Internet Provayder (ISP): {data['isp']}\n"
            result += f"    - Koordinatalar (Lat/Lon): {data['lat']}, {data['lon']}\n"
            result += f"    - Google Maps: https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}\n"
            return result
        else:
            return f"[X] Xato: IP manzil topilmadi yoki noto'g'ri. ({data.get('message')})"
            
    except requests.exceptions.RequestException:
        return "[X] Xatolik: API bilan aloqa uzildi. Internetni tekshiring."

# ----------------------------------------------------
# 7. Asosiy Menyu Funktsiyasi
# ----------------------------------------------------
def main_menu():
    print(banner) # Banner'ni chop etish
    
    while True:
        print("\n--- Xizmatlar Ro'yxati ---")
        print("01: Username orqali tekshirish (Socialscan)")
        print("02: Tel. nomer orqali bazaviy tekshirish [Tayyor!]")
        print("03: IP manzil geolokatsiyasini topish [Yangi!]")
        print("00: Dasturdan chiqish")
        print("-------------------------")

        choice = input("Kerakli xizmatni tanlang (01-03, 00:Chiqish): ")

        # --- 01 Tanlov Logikasi ---
        # --- 01 Tanlov Logikasi ---
        if choice == '01':
            username_target = input("Nishon username'ni kiriting: ")
            
            # YouTube URL'ini olib tashlaymiz, chunki uni Google orqali tekshiramiz
            platforms = [
                "https://instagram.com/",
                "https://t.me/", # Telegram uchun maxsus logika bor
                "https://github.com/",
                "https://twitter.com/",
                "https://www.tiktok.com/@",
                "https://www.snapchat.com/add/",
            ]
            
            print(f"\n--- Nishon {username_target} tekshirilmoqda... ---")
            
            # 1. Boshqa platformalarni tekshirish
            for platform in platforms:
                result = check_user(username_target, platform)
                print(result)

            # 2. Maxsus YouTube (Google) tekshiruvini qo'shish <<<<<<< BU YERGA
            youtube_result = search_youtube_channel(username_target)
            print(youtube_result)
            
            print("--- Tekshiruv yakunlandi. ---\n")

        # --- 02 Tanlov Logikasi ---
        elif choice == '02':
            print("\n--- Tel. Nomer Tekshirish ---")
            phone_target = input("Tekshiruv uchun raqamni kiriting (Masalan, +998901234567): ")
            
            if phone_target.startswith('+'):
                info = check_phone(phone_target)
                print(info)
            else:
                print("[X] Xato: Iltimos, raqamni mamlakat kodi bilan (+ belgisi) kiriting.")

        # --- 03 Tanlov Logikasi ---
        # --- 03 Tanlov Logikasi ---
        elif choice == '03':
            # Local IP ni topish va chop etish
            local_ip = get_local_ip()
            print(f"\n[i] Sizning Local IP manzilingiz: {local_ip}")
            print("\n--- IP Geolokatsiya ---")
            
            # Qolgan kod o'zgarishsiz qoladi
            ip_target = input("Tekshiruv uchun IP manzil yoki Domen nomini kiriting (Masalan, 8.8.8.8 yoki google.com): ")
            
            info = check_ip(ip_target) 
            print(info)

        # --- Qolgan Tanlov Logikasi ---
        elif choice == '00':
            print("Dastur yakunlandi. Ko'rishguncha!")
            sys.exit(0)
        
        else:
            print("[XATO] Noto'g'ri tanlov. Iltimos, raqamni kiriting.")
# ----------------------------------------------------
# 8. Dastur Ishga Tushiruvchi Bosh Qism
# ----------------------------------------------------
if __name__ == "__main__":
    main_menu()
