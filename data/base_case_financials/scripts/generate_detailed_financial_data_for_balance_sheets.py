from faker import Faker
import random
import csv
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

def generate_client_name():
    # Generate a fake company name
    company_name = fake.company()
    
    # Add a descriptive word that aligns with a company that would purchase manufacturing services
    industry_descriptor = fake.random_element(elements=["Automotive", "Aerospace", "Industrial", "Engineering", "Technologies", "Supplies", "Machinery", "Manufacturing"])

    # Combine the descriptor with the company name
    client_name = f"{company_name} {industry_descriptor}"
    
    return client_name

def generate_industry_specific_bs():
    # Get a generic business phrase from faker.bs()
    generic_bs = fake.bs()

    # Define a list of manufacturing-related terms
    industry_terms = [
        "supply chain",
        "production line",
        "inventory management",
        "quality control",
        "precision engineering",
        "machining",
        "fabrication",
        "manufacturing processes",
        "industrial solutions",
        "logistics"
    ]

    # Randomly select an industry term to incorporate
    industry_term = random.choice(industry_terms)

    # Optionally replace or append to the generic bs with the industry term
    modified_bs = f"{generic_bs} for {industry_term}"

    return modified_bs

# Function to generate detailed Bank Account Transactions with a running balance
def generate_bank_transactions(account_type, starting_balance=100000):
    transactions = []
    current_balance = starting_balance
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)  # Approx. 3 months

    for _ in range(random.randint(5, 15)):
        amount = round(random.uniform(-5000, 15000), 2)  # Negative for withdrawals, positive for deposits
        current_balance += amount
        transaction = {
            "Date": fake.date_between(start_date=start_date, end_date=end_date),
            "Description": generate_industry_specific_bs(),
            "Amount": amount,
            "Balance": round(current_balance, 2)  # Track running balance
        }
        transactions.append(transaction)
    return {"Account Type": account_type, "Transactions": transactions, "Balance": round(current_balance, 2)}


# Function to generate Accounts Receivable
def generate_accounts_receivable():
    invoices = []

    start_date = datetime.today()
    end_date = start_date + timedelta(days=90)  # Approx. 3 months

    for _ in range(random.randint(5, 10)):
        # Calculate the start date by subtracting one month (approximately 30 days) from today's date
        payment_start_date = datetime.today() - timedelta(days=30)
        payment_end_date = datetime.today()

        paid = round(random.uniform(0, 1), 2) > 0.5  # 50% chance of being paid

        if paid:
            payment_date = fake.date_between(start_date=payment_start_date, end_date=payment_end_date)
        else:
            payment_date = None

        invoice = {
            "Client": generate_client_name(),
            "Invoice Number": fake.uuid4(),
            "Amount": round(random.uniform(5000, 50000), 2),
            "Due Date": fake.date_between(start_date=start_date, end_date=end_date),
            "Paid": paid,
            "Payment Date": payment_date,
        }
        if invoice["Paid"]:
            invoice["Paid Amount"] = invoice["Amount"]
        else:
            invoice["Paid Amount"] = round(random.uniform(0, invoice["Amount"]), 2)
        invoices.append(invoice)
    return invoices

# Function to generate Short-Term Investments
def generate_short_term_investments():
    treasury_bills = []
    for _ in range(random.randint(3, 5)):
        end_date_purchase = datetime.today() - timedelta(days=90)  # 3 months ago
        start_date_purchase = end_date_purchase - timedelta(days=365)  # 1 year ago from 3 months ago

        start_date_maturity = datetime.today()
        end_date_maturity = start_date_maturity + timedelta(days=365)  # 1 year from today

        tbill = {
            "Note Style": random.choice(["3-month", "6-month", "1-year"]),
            "Purchase Date": fake.date_between(start_date=start_date_purchase, end_date=end_date_purchase),
            "Maturity Date": fake.date_between(start_date=start_date_maturity, end_date=end_date_maturity),
            "Interest Rate": round(random.uniform(0.5, 3.0), 2),
            "Amount Invested": round(random.uniform(10000, 50000), 2)
        }
        treasury_bills.append(tbill)
    
    money_market_funds = []
    for _ in range(random.randint(2, 4)):
        end_date_purchase = datetime.today() - timedelta(days=180)  # 6 months ago
        start_date_purchase = datetime.today() - timedelta(days=365)  # 1 year ago
        mmf = {
            "Fund Name": fake.company() + " Money Market Fund",
            "Purchase Date": fake.date_between(start_date=start_date_purchase, end_date=end_date_purchase),
            "Yield": round(random.uniform(1.0, 2.5), 2),
            "Amount Invested": round(random.uniform(10000, 50000), 2)
        }
        money_market_funds.append(mmf)

    return {"Treasury Bills": treasury_bills, "Money Market Funds": money_market_funds}

def generate_petty_cash_history(starting_balance=1000, months=6):
    transactions = []
    current_balance = starting_balance
    for _ in range(random.randint(10, 30)):  # Number of transactions over the period
        start_date = datetime.today() - timedelta(days=30 * months)
        end_date = datetime.today()
        date = fake.date_between(start_date=start_date, end_date=end_date)

        description = random.choice([
            "Office supplies", "Employee reimbursement", "Postage", 
            "Emergency repair", "Miscellaneous"
        ])
        amount = round(random.uniform(10, 150), 2)  # Small transactions
        current_balance -= amount
        transactions.append({
            "Date": date,
            "Description": description,
            "Amount": amount,
            "Balance": round(current_balance, 2)
        })
    
    # Add replenishments to the petty cash fund
    for _ in range(random.randint(2, 4)):  # Number of replenishments
        start_date = datetime.today() - timedelta(days=30 * months)
        end_date = datetime.today()
        date = fake.date_between(start_date=start_date, end_date=end_date)

        amount = starting_balance - current_balance
        current_balance += amount
        transactions.append({
            "Date": date,
            "Description": "Replenishment",
            "Amount": round(amount, 2),
            "Balance": round(current_balance, 2)
        })

    # Sort transactions by date
    transactions = sorted(transactions, key=lambda x: x['Date'])
    return transactions

# Updated function to include historical petty cash data
def generate_data():
    data = {
        "Company Name": fake.company(),
        "Checking Account": generate_bank_transactions("Checking"),
        "Savings Account": generate_bank_transactions("Savings"),
        "Petty Cash History": generate_petty_cash_history(),
        "Accounts Receivable": generate_accounts_receivable(),
        "Short-Term Investments": generate_short_term_investments()
    }
    return data

# Function to write bank account transactions to a CSV file
def write_bank_accounts(data, filename="bank_accounts.csv"):
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.writer(output_file)
        dict_writer.writerow(["Bank Accounts"])
        dict_writer.writerow(["Account Type", "Transaction Date", "Description", "Amount (USD)", "Running Balance (USD)"])
        for transaction in data["Checking Account"]["Transactions"]:
            dict_writer.writerow(["Checking", transaction["Date"], transaction["Description"], f"${transaction['Amount']:.2f}", f"${transaction['Balance']:.2f}"])

        for transaction in data["Savings Account"]["Transactions"]:
            dict_writer.writerow(["Savings", transaction["Date"], transaction["Description"], f"${transaction['Amount']:.2f}", f"${transaction['Balance']:.2f}"])

    print(f"Bank account data has been written to {filename}")

# Function to write petty cash transactions to a CSV file
def write_petty_cash(data, filename="petty_cash_transactions.csv"):
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.writer(output_file)
        dict_writer.writerow(["Petty Cash Transactions"])
        dict_writer.writerow(["Date", "Description", "Amount (USD)", "Running Balance (USD)"])
        for transaction in data["Petty Cash History"]:
            dict_writer.writerow([transaction["Date"], transaction["Description"], f"${transaction['Amount']:.2f}", f"${transaction['Balance']:.2f}"])
    
    print(f"Petty cash transactions have been written to {filename}")

# Function to write accounts receivable to a CSV file
def write_accounts_receivable(data, filename="accounts_receivable.csv"):
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.writer(output_file)
        dict_writer.writerow(["Accounts Receivable"])
        dict_writer.writerow(["Client", "Invoice Number", "Amount (USD)", "Due Date", "Paid", "Payment Date", "Paid Amount (USD)"])
        for invoice in data["Accounts Receivable"]:
            dict_writer.writerow([
                invoice["Client"], invoice["Invoice Number"], f"${invoice['Amount']:.2f}", 
                invoice["Due Date"], "Yes" if invoice["Paid"] else "No", 
                invoice.get("Payment Date", ""), f"${invoice.get('Paid Amount', 0):.2f}"
            ])
    
    print(f"Accounts receivable data has been written to {filename}")

# Function to write short-term investments to a CSV file
def write_short_term_investments(data, filename="short_term_investments.csv"):
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.writer(output_file)
        dict_writer.writerow(["Short-Term Investments"])
        dict_writer.writerow(["Treasury Bills"])
        dict_writer.writerow(["Note Style", "Purchase Date", "Maturity Date", "Interest Rate (%)", "Amount Invested (USD)"])
        for tbill in data["Short-Term Investments"]["Treasury Bills"]:
            dict_writer.writerow([
                tbill["Note Style"], tbill["Purchase Date"], tbill["Maturity Date"], 
                f"{tbill['Interest Rate']:.2f}", f"${tbill['Amount Invested']:.2f}"
            ])
    
    print(f"Treasury bills data has been written to {filename}")

# Function to write money market funds to a CSV file
def write_money_market_funds(data, filename="money_market_funds.csv"):
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.writer(output_file)
        dict_writer.writerow(["Money Market Funds"])
        dict_writer.writerow(["Fund Name", "Purchase Date", "Yield (%)", "Amount Invested (USD)"])
        for mmf in data["Short-Term Investments"]["Money Market Funds"]:
            dict_writer.writerow([
                mmf["Fund Name"], mmf["Purchase Date"], f"{mmf['Yield']:.2f}", f"${mmf['Amount Invested']:.2f}"
            ])
    
    print(f"Money market funds data has been written to {filename}")

# Generate the detailed data
financial_data_with_history = generate_data()

# Write the data into separate files
write_bank_accounts(financial_data_with_history)
write_petty_cash(financial_data_with_history)
write_accounts_receivable(financial_data_with_history)
write_short_term_investments(financial_data_with_history)
write_money_market_funds(financial_data_with_history)

print("Detailed financial data with petty cash history has been generated and written to detailed_financial_data_with_petty_cash.csv")
