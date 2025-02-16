import argparse
import json
import sys
from datetime import datetime
from typing import Optional

import requests

GRAPHQL_URL = "https://api.shine.fr/v2/graphql"

def main():
    parser = argparse.ArgumentParser(description='Export Shine bank transactions')
    parser.add_argument('token', help='Bearer token from Shine webapp')
    parser.add_argument('--company-id', help='Company profile ID (optional, will be fetched if not provided)')
    parser.add_argument('--bank-account-id', required=True, help='Bank account ID')
    parser.add_argument('--until', help='Fetch transactions until this date (YYYY-MM-DD)', required=False)
    parser.add_argument('--output', help='Output file name', required=False, default="shine_transactions.jsonl")
    args = parser.parse_args()

    output_file = args.output
    until_timestamp = parse_date(args.until) if args.until else None

    # Get company profile ID if not provided
    company_profile_id = args.company_id
    if not company_profile_id:
        company_profile_id, company_name, account_status = get_company_info(args.token)
        print(f"Company: {company_name} (ID: {company_profile_id}, Status: {account_status})")

    if until_timestamp:
        print(f"Fetching transactions until {args.until}")
    else:
        print("Fetching all transactions")

    print(f"Saving to {output_file}")
    total = fetch_transactions(args.token, company_profile_id, args.bank_account_id, output_file, until_timestamp)
    print(f"Done! Saved {total} transactions")

def parse_date(date_str: str) -> int:
    """Convert YYYY-MM-DD to Unix timestamp in milliseconds"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

def get_company_info(token: str) -> tuple[str, str, str]:
    """Fetch company profile ID and name using the root query"""


    response = requests.post(
        GRAPHQL_URL,
        headers=get_headers(token),
        json=get_company_info_query()
    )

    if response.status_code != 200:
        print(f"Error fetching company info: {response.status_code}")
        print(response.text)
        sys.exit(1)

    data = response.json()
    company = data['data']['viewer']['companies'][0]
    return (
        company['companyProfileId'],
        company['profile']['legalName'],
        company['metadata']['accountStatus']
    )

def get_company_info_query() -> dict:
    return {
        "operationName": "root",
        "variables": {},
        "query": """
            query root {
                viewer {
                    uid
                    companies {
                        companyProfileId
                        profile {
                            companyProfileId
                            legalName
                            legalForm
                            __typename
                        }
                        metadata {
                            companyProfileId
                            accountStatus
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
        """
    }

def fetch_transactions(token: str, company_profile_id: str, bank_account_id: str, output_file: str, until_date: Optional[int] = None):
    cursor = None
    page = 0
    total_transactions = 0
    should_stop = False

    with open(output_file, 'w') as f:
        while not should_stop:
            response = requests.post(
                GRAPHQL_URL,
                headers=get_headers(token),
                json=get_transaction_search_query(company_profile_id, bank_account_id, cursor)
            )

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                break

            data = response.json()

            # Extract transactions
            transactions = data['data']['viewer']['company']['transactionsSearch']['edges']
            page_info = data['data']['viewer']['company']['transactionsSearch']['pageInfo']

            # Save transactions and check date filter
            for edge in transactions:
                transaction = edge['node']

                # Stop if we've reached transactions older than until_date
                if until_date and transaction['transactionAt'] < until_date:
                    should_stop = True
                    break

                f.write(json.dumps(transaction) + '\n')
                total_transactions += 1

            print(f"Saved {len(transactions)} transactions from page {page + 1}")

            # Check if there are more pages
            if not page_info['hasNextPage']:
                print("No more pages to fetch")
                break

            cursor = page_info['nextCursor']
            page += 1

    return total_transactions

def get_transaction_search_query(company_profile_id: str, bank_account_id: str, after: Optional[str] = None) -> dict:
    return {
        "operationName": "transactionsSearch",
        "variables": {
            "after": after,
            "companyProfileId": company_profile_id,
            "filters": {
                "bankAccountId": bank_account_id,
                "searchTerm": ""
            },
            "first": 50
        },
        "query": """
            query transactionsSearch($companyProfileId: UUIDv4!, $filters: TransactionsFilters!, $after: String, $first: Int) {
                viewer {
                    uid
                    company(companyProfileId: $companyProfileId) {
                        companyProfileId
                        transactionsSearch(after: $after, first: $first, filters: $filters) {
                            pageInfo {
                                hasNextPage
                                nextCursor
                                totalCount
                                __typename
                            }
                            edges {
                                node {
                                    categoryIds
                                    category
                                    companyUserId
                                    createdAt
                                    expectedReleaseDate
                                    transactionId
                                    currency
                                    initiatorName
                                    isPersonal
                                    status
                                    fee
                                    feeType
                                    title
                                    description
                                    type
                                    value
                                    remainingAuthorized
                                    transferPayinSenderName
                                    paymentMethod
                                    transactionAt
                                    updatedAt
                                    isRefund
                                    hasReceipts
                                    isOnAgentWallet
                                    bankAccountId
                                    foreignEntityId
                                    foreignEntityType
                                    bankTransferStatus
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }
        """
    }

def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "platform": "WEBAPP",
    }

if __name__ == "__main__":
    main()
