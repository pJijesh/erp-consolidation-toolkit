"""Account concepts for the two fictional charts and the target chart.

Each concept is one line in the target chart. It may exist in ERP A (one account),
in ERP B (one or more accounts, because ERP B is more granular), or both.
Names are written the way each chart's owners might plausibly write them, so the
mapping tool has realistic wording differences to deal with.

Format: (group, target name, ERP A name or None, [ERP B names] or None)
"""

CONCEPTS = [
    # Fixed assets
    ("FA", "Freehold land and buildings", "Freehold Property", ["Land and buildings"]),
    ("FA", "Plant and machinery at cost", "Plant & Machinery - Cost", ["Technical equipment cost"]),
    ("FA", "Plant and machinery accumulated depreciation", "Plant & Machinery - Acc Depn", ["Technical equipment accumulated depreciation"]),
    ("FA", "Motor vehicles at cost", "Motor Vehicles - Cost", ["Vehicles cost"]),
    ("FA", "Motor vehicles accumulated depreciation", "Motor Vehicles - Acc Depn", ["Vehicles accumulated depreciation"]),
    ("FA", "Fixtures and fittings at cost", "Fixtures & Fittings - Cost", ["Office equipment cost"]),
    ("FA", "Fixtures and fittings accumulated depreciation", "Fixtures & Fittings - Acc Depn", ["Office equipment accumulated depreciation"]),
    ("FA", "Computer equipment at cost", "IT Equipment - Cost", ["IT hardware cost"]),
    ("FA", "Computer equipment accumulated depreciation", "IT Equipment - Acc Depn", ["IT hardware accumulated depreciation"]),
    ("FA", "Capitalised software", "Software Licences", ["Capitalised software"]),
    # Current assets
    ("CA", "Raw materials inventory", "Stock - Raw Materials", ["Inventory raw materials"]),
    ("CA", "Work in progress inventory", "Stock - Work in Progress", ["Inventory work in progress"]),
    ("CA", "Finished goods inventory", "Stock - Finished Goods", ["Inventory finished goods"]),
    ("CA", "Inventory provision", None, ["Inventory write-down reserve"]),
    ("CA", "Trade receivables", "Trade Debtors Control", ["Trade receivables domestic", "Trade receivables EU", "Trade receivables non-EU"]),
    ("CA", "Allowance for doubtful debts", "Provision for Bad Debts", ["Bad debt allowance"]),
    ("CA", "Other receivables", None, ["Other receivables"]),
    ("CA", "Prepayments", "Prepayments", ["Prepaid expenses"]),
    ("CA", "Accrued income", None, ["Accrued income"]),
    ("CA", "Input VAT recoverable", "VAT Input", ["Input tax 19 percent"]),
    ("CA", "Bank current accounts", "Bank Current Account", ["Bank 1 main account"]),
    ("CA", "Bank foreign currency accounts", None, ["Bank USD account"]),
    ("CA", "Petty cash", None, ["Cash on hand"]),
    ("CA", "Intercompany receivables", "Intercompany Receivable", ["Receivables from affiliated companies"]),
    ("CA", "Rent and other deposits", None, ["Security deposits paid"]),
    # Current liabilities
    ("CL", "Trade payables", "Trade Creditors Control", ["Trade payables domestic", "Trade payables foreign"]),
    ("CL", "Accruals", "Accruals", ["Accrued expenses"]),
    ("CL", "Goods received not invoiced", "GRNI Accrual", ["Goods receipt invoice receipt clearing"]),
    ("CL", "Output VAT", "VAT Output", ["Output tax 19 percent"]),
    ("CL", "VAT settlement", None, ["VAT settlement account"]),
    ("CL", "Payroll taxes and social security payable", "PAYE & NI Control", ["Wage tax payable", "Social security payable"]),
    ("CL", "Pensions payable", None, ["Pension fund payable"]),
    ("CL", "Corporate income tax payable", "Corporation Tax Payable", ["Corporate income tax payable"]),
    ("CL", "Short term loans", "Bank Loan - Current", ["Short-term loans"]),
    ("CL", "Finance lease liabilities, current", "HP Creditors - Current", ["Finance lease liabilities current"]),
    ("CL", "Intercompany payables", "Intercompany Payable", ["Payables to affiliated companies"]),
    ("CL", "Deferred income", "Deferred Income", ["Deferred income"]),
    ("CL", "Customer deposits", None, ["Customer prepayments received"]),
    ("CL", "Warranty provision", None, ["Warranty provision"]),
    ("CL", "Holiday pay accrual", None, ["Accrued holiday pay"]),
    ("CL", "Suspense and clearing", "Suspense", ["Clearing account"]),
    # Long term liabilities
    ("LL", "Long term loans", "Bank Loan - Long Term", ["Long-term loans"]),
    ("LL", "Finance lease liabilities, non-current", "HP Creditors - Long Term", ["Finance lease liabilities non-current"]),
    ("LL", "Shareholder and director loans", "Directors Loan Account", None),
    ("LL", "Deferred tax liability", "Deferred Tax Liability", ["Deferred tax liability"]),
    # Equity
    ("EQ", "Share capital", "Called Up Share Capital", ["Subscribed capital"]),
    ("EQ", "Share premium", "Share Premium Account", ["Capital reserve"]),
    ("EQ", "Retained earnings", "Profit & Loss Reserve", ["Retained earnings brought forward"]),
    ("EQ", "Revaluation reserve", "Revaluation Reserve", None),
    # Revenue
    ("REV", "Revenue, castings domestic", "Sales - Castings UK", ["Revenue domestic"]),
    ("REV", "Revenue, castings export", "Sales - Castings Export", ["Revenue EU", "Revenue non-EU"]),
    ("REV", "Revenue, tooling", "Sales - Tooling", ["Revenue tooling"]),
    ("REV", "Revenue, spares and services", "Sales - Spares", ["Revenue spare parts"]),
    ("REV", "Sales returns and discounts", "Sales Returns & Allowances", ["Sales deductions"]),
    ("REV", "Carriage income", None, ["Freight income"]),
    ("REV", "Other operating income", "Other Income", ["Other operating income"]),
    ("REV", "Scrap sales", None, ["Proceeds from scrap"]),
    # Cost of sales
    ("COS", "Raw materials consumed", "Purchases - Raw Materials", ["Material costs"]),
    ("COS", "Direct labour", "Direct Wages", ["Production wages"]),
    ("COS", "Subcontract processing", "Subcontract Processing", ["External processing"]),
    ("COS", "Carriage inwards", "Carriage Inwards", ["Freight-in"]),
    ("COS", "Production consumables", "Consumables - Production", ["Operating supplies production"]),
    ("COS", "Production energy", "Gas & Electric - Production", ["Energy production"]),
    ("COS", "Tooling expensed", "Tooling Costs", ["Tools expensed"]),
    ("COS", "Change in inventories", "Stock Movement", ["Change in inventories"]),
    ("COS", "Purchase price variance", "PPV", ["Price differences"]),
    ("COS", "Scrap and rework", None, ["Scrap and rework costs"]),
    ("COS", "Inventory write-offs", None, ["Inventory write-offs"]),
    # Overheads
    ("OH", "Indirect labour", "Indirect Wages", ["Indirect labour"]),
    ("OH", "Salaries", "Salaries - Admin", ["Salaries administration"]),
    ("OH", "Employer social security", "Employers NI", ["Employer social security"]),
    ("OH", "Pension costs", "Pension Costs", ["Pension expense"]),
    ("OH", "Rent", "Rent", ["Rent"]),
    ("OH", "Business rates and property taxes", "Business Rates", ["Property tax"]),
    ("OH", "Utilities, offices", "Utilities", ["Utilities offices"]),
    ("OH", "Repairs and maintenance", "R&M - Machinery", ["Maintenance machinery"]),
    ("OH", "Insurance", "Insurance", ["Insurance"]),
    ("OH", "Motor expenses", "Motor Expenses", ["Vehicle costs"]),
    ("OH", "Travel and subsistence", "Travel & Subsistence", ["Travel expenses"]),
    ("OH", "Telephone and internet", "Telephone & Internet", ["Telecommunications"]),
    ("OH", "IT costs and subscriptions", "IT Costs", ["IT services", "Software subscriptions"]),
    ("OH", "Legal fees", None, ["Legal fees"]),
    ("OH", "Audit and accountancy", "Audit & Accountancy", ["Audit and tax advisory"]),
    ("OH", "Bank charges", "Bank Charges", ["Bank fees"]),
    ("OH", "Marketing and advertising", "Advertising", ["Marketing"]),
    ("OH", "Training", None, ["Training and education"]),
    ("OH", "Office supplies and printing", "Stationery & Printing", ["Office supplies"]),
    ("OH", "Depreciation, plant and machinery", "Depreciation - P&M", ["Depreciation technical equipment"]),
    ("OH", "Depreciation, vehicles", None, ["Depreciation vehicles"]),
    ("OH", "Depreciation, other", "Depreciation - Other", ["Depreciation office equipment", "Amortisation software"]),
    ("OH", "Bad debt expense", None, ["Bad debt expense"]),
    ("OH", "Warranty costs", None, ["Warranty expense"]),
    ("OH", "Health and safety", None, ["Occupational safety"]),
    ("OH", "Sundry expenses", "Sundry Expenses", ["Other operating expenses"]),
    # Finance and tax
    ("FINE", "Interest payable", "Loan Interest", ["Interest expense"]),
    ("FINE", "Exchange losses", "Exchange Losses", ["Realised exchange losses"]),
    ("FINE", "Corporate income tax expense", "Corporation Tax Charge", ["Income tax expense", "Trade tax expense"]),
    ("FINE", "Deferred tax expense", None, ["Deferred tax expense"]),
    ("FINI", "Interest receivable", "Bank Interest Received", ["Interest income"]),
    ("FINI", "Exchange gains", "Exchange Gains", ["Realised exchange gains"]),
]

# Accounts that exist in only one system and have no obvious home in the target chart.
# (group, name, truth target name or None when the target chart needs a new account)
A_EXTRAS = [
    ("COS", "Foundry Sand Reclamation", None),
    ("OH", "Old Site Closure Costs", None),
    ("CA", "Mould Tooling Deposits", None),
]
B_EXTRAS = [
    ("CL", "Investment grants deferred", "Deferred income"),
    ("OH", "Packaging disposal levy", None),
    ("CA", "Emissions certificates", None),
    ("OH", "Works council costs", None),
]

GROUP_TARGET = {
    # group: (target header code, target header name, target type)
    "FA": (11000, "Fixed assets", "asset"),
    "CA": (12000, "Current assets", "asset"),
    "CL": (21000, "Current liabilities", "liability"),
    "LL": (22000, "Long term liabilities", "liability"),
    "EQ": (31000, "Equity", "equity"),
    "REV": (41000, "Revenue", "revenue"),
    "COS": (51000, "Cost of sales", "expense"),
    "OH": (61000, "Overheads", "expense"),
    "FINE": (71000, "Finance costs and tax", "expense"),
    "FINI": (72000, "Finance income", "revenue"),
}

A_BASE = {"FA": 1000, "CA": 1200, "CL": 2000, "LL": 2500, "EQ": 3000, "REV": 4000, "COS": 5000, "OH": 7000, "FINE": 8000, "FINI": 8500}
B_BASE = {"FA": 100000, "CA": 200000, "CL": 400000, "LL": 450000, "EQ": 300000, "REV": 500000, "COS": 600000, "OH": 700000, "FINE": 900000, "FINI": 910000}

A_TYPE_LABEL = {"FA": "Fixed Asset", "CA": "Current Asset", "CL": "Current Liability", "LL": "Long Term Liability",
                "EQ": "Equity", "REV": "Sales", "COS": "Cost of Sales", "OH": "Overhead", "FINE": "Overhead", "FINI": "Other Income"}
B_TYPE_LABEL = {"FA": "Fixed assets", "CA": "Current assets", "CL": "Provisions and liabilities", "LL": "Provisions and liabilities",
                "EQ": "Equity", "REV": "Income", "COS": "Expenses", "OH": "Expenses", "FINE": "Financial result", "FINI": "Financial result"}
