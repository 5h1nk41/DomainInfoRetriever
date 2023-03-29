
import streamlit as st
import dns.resolver
import subprocess
import openai
import pandas as pd
import os

# GPT-3 APIキーを設定します。環境変数から取得してください。
openai.api_key = os.environ["OPENAI_API_KEY"]

# WHOIS情報の取得
@st.cache_data
def get_whois_info(domain):
    try:
        command = f"whois {domain}"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return output.decode()
    except Exception as e:
        st.error(f"WHOIS情報の取得中にエラーが発生しました: {e}")
        return ""

# WHOIS情報の結果をパースして辞書→Pandas DataFrameに変換
@st.cache_data
def parse_whois_data(whois_raw):
    whois_data = {}
    desired_keys = [
        "Domain Name",
        "Registrar",
        "Registrar URL",
        "Registrar Abuse Contact",
        "Registrar Abuse Contact",
        "Updated Date",
        "Creation Date",
        "Registrar Registration Expiration Date",
        "Domain Status",
        "Registrant Email",
        "Admin Email",
        "DNSSEC",
    ]

    for line in whois_raw.split("\n"):
        if ":" in line:
            key, value = [part.strip() for part in line.split(":", 1)]
            if key in desired_keys:
                whois_data[key] = value
    return whois_data

# DNS情報の取得
@st.cache_data
def get_dns_info(domain):
    dns_info = {}
    try:
        a_records = dns.resolver.resolve(domain, "A")
        dns_info["A"] = [str(record) for record in a_records]
    except dns.resolver.NoAnswer:
        dns_info["A"] = []

    try:
        aaaa_records = dns.resolver.resolve(domain, "AAAA")
        dns_info["AAAA"] = [str(record) for record in aaaa_records]
    except dns.resolver.NoAnswer:
        dns_info["AAAA"] = []

    try:
        cname_records = dns.resolver.resolve(domain, "CNAME")
        dns_info["CNAME"] = [str(record) for record in cname_records]
    except dns.resolver.NoAnswer:
        dns_info["CNAME"] = []

    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        dns_info["MX"] = [(str(record.exchange), record.preference) for record in mx_records]
    except dns.resolver.NoAnswer:
        dns_info["MX"] = []

    try:
        ns_records = dns.resolver.resolve(domain, "NS")
        dns_info["NS"] = [str(record) for record in ns_records]
    except dns.resolver.NoAnswer:
        dns_info["NS"] = []

    try:
        txt_records = dns.resolver.resolve(domain, "TXT")
        dns_info["TXT"] = [str(record) for record in txt_records]
    except dns.resolver.NoAnswer:
        dns_info["TXT"] = []

    return dns_info


# GPT-3を使って情報を解説する
@st.cache_data
def get_gpt3_summary(whois_info, dns_info):
    formatted_whois = "\n".join([f"{key}: {value}" for key, value in whois_info.items()])
    formatted_dns = "\n".join([f"{key}: {value}" for key, value in dns_info.items()])

    prompt = (
        f"WHOIS情報とDNS情報の要約と解説を日本語で提供してください。\n\n"
        f"WHOIS情報:\n{formatted_whois}\n\n"
        f"DNS情報:\n{formatted_dns}\n\n"
    )

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.1,
    )

    return response.choices[0].text.strip()

st.title("Domain Information Retriever")

domain = st.text_input("Enter a domain name:")

if domain:
    with st.spinner("Retrieving WHOIS information..."):
        whois_raw = get_whois_info(domain)
        whois_data = parse_whois_data(whois_raw)
        whois_df = pd.DataFrame(whois_data.items(), columns=["Key", "Value"])

    with st.spinner("Retrieving DNS information..."):
        dns_info = get_dns_info(domain)

    with st.spinner("Generating summary and explanation..."):
        summary = get_gpt3_summary(whois_data, dns_info)

    st.header("WHOIS Information")
    st.write(whois_df)

    st.header("DNS Information")
    st.write(dns_info)

    st.header("Summary and Explanation")
    st.markdown(f"> {summary}")