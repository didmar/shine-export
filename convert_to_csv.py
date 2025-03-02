import argparse
import csv
import json
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='Convert Shine transactions from JSONL to CSV')
    parser.add_argument('input_file', help='Input JSONL file (e.g., shine_transactions.jsonl)')
    parser.add_argument('--output', help='Output CSV file', default='shine_transactions.csv')
    args = parser.parse_args()

    print(f"Converting {args.input_file} to {args.output}...")
    count = convert_jsonl_to_csv(args.input_file, args.output)
    print(f"Done! Converted {count} transactions to CSV format.")


def convert_jsonl_to_csv(input_file, output_file):
    """Convert JSONL file to CSV format"""
    # Read the JSONL file
    transactions = []
    with open(input_file, 'r') as f:
        for line in f:
            transactions.append(json.loads(line.strip()))

    if not transactions:
        print(f"No transactions found in {input_file}")
        return 0

    # Define CSV headers.
    # Does not include all fields, only the ones that are relevant
    # to visualize in a spreadsheet, and put the most important ones first
    headers = [
        'transactionDate',
        'title',
        'description',
        'type',  # 'payin' or 'payout'
        'value',  # the amount of the transaction
        'currency',
        'fee',
        'feeType',
        'status',
        'category',
        'initiatorName',
        'paymentMethod',
        'isPersonal',
        'isRefund',
        'hasReceipts',
        'isOnAgentWallet',
        'expectedReleaseDate',
        'remainingAuthorized',
        'transferPayinSenderName',
    ]

    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for transaction in transactions:
            row = {}
            for column_name in headers:
                row[column_name] = transaction.get(column_name)
            
            # Add formatted dates
            row['transactionDate'] = convert_timestamp_to_date(transaction.get('transactionAt'))
            row['expectedReleaseDate'] = convert_timestamp_to_date(transaction.get('expectedReleaseDate'))
            
            writer.writerow(row)
    
    return len(transactions)


def convert_timestamp_to_date(timestamp):
    """Convert millisecond timestamp to YYYY-MM-DD format"""
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')


if __name__ == "__main__":
    main() 