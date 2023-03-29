import streamlit as st
import dns.resolver
import requests
import openai
import pandas as pd
import os
import re

# GPT-3 APIキーを設定します。環境変数から取得してください。
openai.api_key = os.environ["OPENAI_API_KEY"]

# WHOIS情報の取得
@st.cache_data
def get_whois_info(api_key, domain):
    try:
        url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={api_key}&domainName={domain}&outputFormat=JSON"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        st.error(f"WHOIS情報の取得中にエラーが発生しました: {e}")
        return {}
    
# WHOIS情報の結果をパースしてステータスを取得し、Pandas DataFrameに変換
def parse_whois_data(whois_data):
    desired_keys = [
        "domainName",
        "createdDateNormalized",
        "updatedDateNormalized",
        "expiresDateNormalized",
        "status",
    ]

    whois_info = {}
    if 'WhoisRecord' in whois_data and 'registryData' in whois_data['WhoisRecord']:
        registry_data = whois_data['WhoisRecord']['registryData']

        for key in desired_keys:
            if key in registry_data:
                value = registry_data[key]
                whois_info[key] = value

    return pd.DataFrame(whois_info.items(), columns=["Key", "Value"])

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
def get_gpt3_summary(whois_raw, dns_info):
    formatted_dns = "\n".join([f"{key}: {value}" for key, value in dns_info.items()])

    prompt = (
        f"ドメインのWHOISステータスとDNS情報の要約と解説を日本語で提供してください。\n\n"
        f"WHOISステータス:\n{whois_raw}\n\n"
        f"DNS情報:\n{formatted_dns}\n\n"
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

# メイン
st.title("Domain Information Retriever")

domain = st.text_input("Enter a domain name:")

if domain:
    api_key = "at_BW8qU6pHDtKEqGbPU4DFMkZEkHiqf"
    with st.spinner("Retrieving WHOIS information..."):
        whois_data = get_whois_info(api_key, domain)
        whois_status_df = parse_whois_data(whois_data)

    with st.spinner("Retrieving DNS information..."):
        dns_info = get_dns_info(domain)

    with st.spinner("Generating summary and explanation..."):
        summary = get_gpt3_summary(whois_status_df.to_string(index=False, header=False), dns_info)

    st.header("WHOIS Status")
    st.write(whois_status_df)

    st.header("DNS Information")
    st.write(dns_info)

    st.header("Summary and Explanation")
    st.markdown(f"{summary}")
