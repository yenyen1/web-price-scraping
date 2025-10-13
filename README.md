# Amazon Price Check

Extracting the price of a specific product from a given Amazon URL and sending an email when the price below your expectation.

## How to use
```
# Clone the repo and change directory
git clone https://github.com/yenyen1/web-price-scraping.git && cd web-price-scraping && pip install .
# Run python
amazon_price_check -h
amazon_price_check -c {credentials_path} -t {token_path} --config {config_path}
```
## Config File Example
- Sending email when the price lower than the price point.
```json
{
    "urlname": "Product name",
    "price_point": {price_point}, 
    "url": "https://www.amazon.ca/*/dp/*",
    "receiver": "receiver@example.com",
    "sender": "sender@gmail.com"
}
```
## Gmail API
- `credentials.json`: This file is downloaded from the Google Cloud Console. It contains your OAuth 2.0 client credentials. 
- `token.json`: This file is generated automatically the first time you run the program and complete the OAuth consent flow. It stores your user's access and refresh tokens, so you don't have to log in every time.

## Price log
`check_price.log` is generated automatically to record the log.
### Example
```
# Date  Time    Type    ProductName    CurrentPrice AccessCount
2025-10-12 17:12:27,726 [INFO] Bioderma-DUO	37.480000	1
2025-10-12 17:15:31,263 [INFO] Bioderma-DUO	37.480000	1
2025-10-12 22:39:27,287 [INFO] Bioderma-DUO	37.480000	1
```