# Domain Information Retriever
This project is a Streamlit app that retrieves WHOIS status and DNS information for a given domain. Additionally, it provides a summary and explanation of the information retrieved, using OpenAI's GPT-3.

## Features
- Retrieve WHOIS status for a domain
- Retrieve DNS information for a domain
- Provide a summary and explanation of the retrieved data using OpenAI's GPT-3

## Installation
1.Clone the repository:

```bash
git clone https://github.com/5h1nk41/DomainInfoRetriever.git
```

2.Change to the project directory:
```bash
cd DomainInfoRetriever
```

3.Install the required dependencies:
```bash
pip install -r requirements.txt
```

4.Create a .env file to store your OpenAI API key and Whois API key:
```makefile
OPENAI_API_KEY=your_openai_api_key
WHOIS_API_KEY=your_whois_api_key
```
Replace `your_openai_api_key` and `your_whois_api_key` with your actual API keys.

5.Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage
1.Open the Streamlit app in your browser (usually at http://localhost:8501)
2.Enter a domain name in the input field
3.The app will display the WHOIS status, DNS information, and a summary and explanation of the data

## Dependencies
- streamlit
- dns.resolver
- requests
- openai
- pandas

## License
This project is open source under the MIT License. See LICENSE for more information.
