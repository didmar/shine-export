# Export transaction data from Shine bank

Their export functionality never worked for me, so I made this script to download the data using the graphql API.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

To use this script, you need to:

1. Get your bearer token from Shine's webapp:
   - Go to https://app.shine.fr/
   - Open your browser's developer tools (F12)
   - Go to the Network tab
   - Look for requests to `https://api.shine.fr/v2/graphql`
   - In the request headers, find the `Authorization` header
   - Copy the token (it starts with "Bearer ", but only copy what comes after)

2. Get your bank account ID for the account you want to export:
   - Go to your bank account page in Shine
   - The ID is in the URL: `https://app.shine.fr/bank/overview?bankAccountId=<this-is-the-id>`

3. Run the script:

```bash
# Fetch all transactions
python main.py <your_bearer_token> --bank-account-id <your_bank_account_id>

# Fetch transactions until a specific date
python main.py <your_bearer_token> --bank-account-id <your_bank_account_id> --until 2024-01-01

# Specify a custom output file
python main.py <your_bearer_token> --bank-account-id <your_bank_account_id> --output my_transactions.jsonl
```

It will fetch all transactions (or up to the specified date) and save them to `shine_transactions.jsonl` by default.

## Converting to CSV

After exporting the transactions to JSONL, you can convert them to CSV format for easier analysis in spreadsheet software:

```bash
# Convert the default export file
python convert_to_csv.py shine_transactions.jsonl

# Specify a custom output file
python convert_to_csv.py shine_transactions.jsonl --output my_transactions.csv
```

The CSV file will include all transaction fields plus additional formatted date columns:
- `transactionDate`: Human-readable date (YYYY-MM-DD) from `transactionAt`
- `createdDate`: Human-readable date from `createdAt`
- `updatedDate`: Human-readable date from `updatedAt`

## Transaction Data Format

Each transaction in the JSONL file is a JSON object representing one transaction, which looks like this:

```json
{
  "categoryIds": ["b50fac41-6fa9-4627-a760-b609a968c600"],
  "category": "EQUIPMENT",
  "companyUserId": "00000000-0000-0000-0000-000000000000",
  "createdAt": 1737288616483,
  "expectedReleaseDate": null,
  "transactionId": "11111111-1111-1111-1111-111111111111",
  "currency": "EUR",
  "initiatorName": "Jean DUPONT",
  "isPersonal": false,
  "status": "VALIDATED",
  "fee": 1.23,
  "feeType": "CARD_PAYOUT_NON_EU",
  "title": "SOME TITLE",
  "description": "SOME DESCRIPTION",
  "type": "payout",
  "value": 19.99,
  "remainingAuthorized": 0,
  "transferPayinSenderName": "",
  "paymentMethod": "CARD",
  "transactionAt": 1737288616000,
  "updatedAt": 1737342052914,
  "isRefund": false,
  "hasReceipts": false,
  "isOnAgentWallet": false,
  "bankAccountId": "22222222-2222-2222-2222-222222222222",
  "foreignEntityId": null,
  "foreignEntityType": null,
  "bankTransferStatus": null,
  "__typename": "Transaction"
}
```