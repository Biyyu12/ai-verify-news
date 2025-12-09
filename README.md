## Getting Started

1. **Clone Repository**

    ```bash
    git clone https://github.com/Biyyu12/ai-verify-news.git
    cd ai-verify-news
    ```

2. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Buat file .env**

    Membuat file `.env` di root project untuk menyimpan API Key:

    ```
    EXA_API_KEY=your-exa-api-key-here
    ```

    atau bisa memasukkan API key langsung ke app.py

    ```Python
    # Replace with your actual EXA API key
    # exa_tool = ExaSearchResults(exa_api_key="Your-EXA-API-Key-Here")
    ```

4. **Jalankan Aplikasi**

    ``` bash
    streamlit run app.py
    ```

### Tentang API Key
**API key tidak disimpan di repository**


