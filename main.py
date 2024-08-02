import pandas as pd

allowed_providers = [
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "yahoo.com",
    "protonmail.com",
    "icloud.com",
    "zoho.com",
    "aol.com",
    "gmx.com",
    "gmx.net",
    "yandex.com",
    "yandex.ru",
    "mail.com",
    "fastmail.com",
    "tutanota.com",
    "posteo.de",
    "hushmail.com",
    "runbox.com",
    "laposte.net",
    "web.de",
    "rediffmail.com",
    "qq.com",
    "seznam.cz",
    "mailfence.com",
    "startmail.com",
    "countermail.com",
    "kolabnow.com",
    "disroot.org",
    "riseup.net",
    "msn.com"
]

df = pd.read_csv("members_directory.csv")

def check_email(email):
    provider = email.split("@")[-1]
    if provider in allowed_providers:
        return '-'
    return provider

df['Website Urls'] = df['Email Address'].apply(check_email)

df.to_csv("members_directory.csv", index=False)