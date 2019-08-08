# Final Project - CompareRate

## Set-up

Source the requirements.txt file for the python libraries.  These are really important.  Then create 
a .env file in the /final/CompareRate (project parent folder) and fill in these parameters:

```bash
ZILLOW_API_KEY=''
SECRET_KEY = ''
```

SECRET_KEY is django's secret key that is used for sessions etc.  See Django docs on how to generate
a random secure variant.

ZILLOW_API_KEY is the zillow api key that you can get at the following url: 
https://www.zillow.com/howto/api/APIOverview.htm.  Sign-up for an account and get a 
Zillow API key called a: ZWSID.


## Overview

CompareRate is an website for forecasting and managing loans with a built-in Zillow Search for finding mortgages.
The app is split up into 3 different apps: Accounts, Liabilities and Houses.

* Accounts -> Sign-up and Login functionality, basically a copy-paste job from Project 3.
* Liabilities -> Loan management app where you can add, delete or modify a loan and see amortization schedules
as well as a summary of all your loans.  Auto-calculates things like monthly payment and interest owed.
* Houses -> A Zillow Search application that scans an open addresses database extract for addresses to use
against the Zillow API.  Open Addresses has 200k addresses for Cambridge, Ma (though you can get a few
million globally).

The website:
You start with a login screen with the option to sign-up.  Once you sign-up or login you are redirected
to a loan summary page.  If you are new to the website, it will prompt you to add a loan.  If you are not,
it will have 3 tables containing summaries of all your loans.  The tables are:

1. Loans -> the detail of all your loans including things like provider, interest and principal.
2. Cashflow -> the cash flow for a given loan in terms of monthly payment and the breakdown of interest and
principal paid in your last payment.
3. Loan Cost -> this is the total cost of the loan over the life of the loan.

Each table is broken down by loan and sum of important calculations for the entire account such as:
total principal, total interest paid over the life of the loan, the average interest rate across all
loans weighted by size of loan (sum-product).

The Loans table has global actions drop-down button and per loan actions drop down button to either modify 
your account or modify a specific loan.  For global actions, you can add a loan or search for a house.  
Add a loan button let's you add a new loan.  The search house button let's you search a local database
of addresses (for Cambridge, Ma) to use against the Zillow API to get information about house prices 
and features.  The action buttons for each loan allow you to modify them or delete them respectively.

The Cashflow table has global and per loan actions as well.  The global option will list all of the 
amortization tables for all loans as a large list.  The per loan options will allow you to see 
the amortization schedule for a single loan.

The Total Cost table currently has no options, but you could think up ones.  Eg fixed costs vs 
variable costs etc.

Two other pages are worth noting here.  When you click add loan or modify an existing loan, it brings
you to the loan details page.  The Loan button on this page has a drop down of all loans and also
short-cuts to adding a new loan or doing a house search.  When you add a loan or modify a loan, it redos
all calculations in the summary page for you and also re-creates the amortization table.  Soemthing to 
improve in the future is make sure you can accept integers instead of decimals for interest rate.

The House search is cool.  The first page is a search box, which scans address, city and state of 
the Open Addresses database to find addresses in an area.  Originally this was gong to include google 
maps, but I didn't have time to implement it.  When you search, you will get a list of addresses.  Clicking
on this causes a Zillow search to occur and will retrieve: a photo gallery, zillow housing estimates,
house features if present such as rooms, bathrooms, sqft.  Note: Zillow doesn't allow me to persist
data so this is why I split up the addresses and zillow search portions.  I also couldn't find an 
api to list all houses in a neighborhood.  Zillow search will only show houses that have an estimate
so it is possible that an address is listed in open addresses database, but the house has never
been on the market, listed on zillow or there is no daata on the house currently (quotes are too old).

See final/CompareRate/data/houses_to_keep.txt to find 5 example addresses that have both photos, more
details and zestimates.  I tried to handle cases where no photos exist, no info on rooms/bathrooms etc
So not all search results will be the same.

## Tables:

Feel free to use the below to check out table structures.  A quick explanation of each table:

HOUSE (ZILLOW SEARCH APP):
```python

# Open Addresses table that only includes 200k Cambridge, Ma addresses.
class Address(models.Model):
    longitude = models.DecimalField(max_digits=10,decimal_places=7)
    latitude = models.DecimalField(max_digits=9,decimal_places=7)
    street = models.CharField(max_length=512)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=2)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"

```

LIABILITIES (LOAN APP):
```python

# when you don't get a result for Zillow, this object is passed to it.  It's a generic object with
# no properties.
class NoResult(object):
    pass


# Just used for a drop-down of loan types to control for it.
class Loan_Type(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name}"


# There are a ton of calculations here.  This is the loan model I use. Properties include a ton of things
# computed on the fly.  There is a good chance that I would in the future convert this all into columns
# instead of using doing this on the fly.
# Global aggregates of certain measures are done on the fly in the views.  Another possible way to 
# convert memory intense task to disk if I max that out.

class Loan(models.Model):
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=256)
    loan_type = models.ForeignKey(Loan_Type,on_delete=models.DO_NOTHING)
    principal = models.DecimalField(max_digits=12, decimal_places=2,validators=[
        MinValueValidator(100)
    ])
    terms = models.IntegerField(validators=[
        MaxValueValidator(1000),
        MinValueValidator(6)
    ])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=5)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=256, default="active")

    def _get_latest_payment(self):
        return Payment.objects.filter(loan=self).filter(payment_date__gt=date.today()).order_by('installment').first()

    @property
    def is_paid_off(self):
        last_payment = self._get_latest_payment()
        if last_payment is None:
            return True
        else:
            return False

    @property
    def interest_rate_pct(self):
        return round(100 * self.interest_rate, 3)

    @property
    def periodic_interest_rate(self):
        return float(self.interest_rate) / 12.0

    @property
    def loan_cost(self):
        return (int(self.terms) * (float(self.principal) * self.periodic_interest_rate) / (
                1 - (1 + self.periodic_interest_rate) ** (-1 * int(self.terms)))) - float(self.principal)

    @property
    def monthly_payment(self):
        return float(self.principal) * (
                    self.periodic_interest_rate * (1 + self.periodic_interest_rate) ** int(self.terms)) / (
                           (1 + self.periodic_interest_rate) ** int(self.terms) - 1)

    @property
    def last_principal_payment(self):
        last_payment = self._get_latest_payment()
        if last_payment is None:
            return 0
        return last_payment.principal_paid + last_payment.addition_paid

    @property
    def last_interest_payment(self):
        last_payment = self._get_latest_payment()
        if last_payment is None:
            return 0
        return last_payment.interest_paid

    @property
    def current_principal(self):
        last_payment = self._get_latest_payment()
        if last_payment is None:
            return 0
        return last_payment.principal_base

    def __str__(self):
        return f"{self.user_fk.username} - {self.provider} - ${self.principal} - {self.terms} months"

# Payments for the amortization table.  This is called a lot in the loans table to get certain calculations.
class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE,related_name='payments')
    installment = models.IntegerField()
    payment_type = models.CharField(max_length=256)
    payment_date = models.DateField()
    principal_base = models.DecimalField(max_digits=12, decimal_places=2)
    principal_paid = models.DecimalField(max_digits=12, decimal_places=2)
    addition_paid = models.DecimalField(max_digits=12, decimal_places=2)
    interest_paid = models.DecimalField(max_digits=12, decimal_places=2)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.installment} - {self.loan}"

```

##File Structure

The below is a directory structure of the entire application with some basic notes.

```
C:.
│   .env -> set the secrets here...
│   db.sqlite3 -> database
│   manage.py -> django management utility
│
├───accounts -> This is just a Sign-up app
│   │   apps.py -> app file
│   │   forms.py -> Sign-up form
│   │   urls.py -> Sign-up url
│   │   views.py -> Sign-up function
│   │__  __init__.py
│
├───CompareRate -> This is just the global app
│   │   settings. -> settings, dotenv loads from master folder .env for secrets
│   │   urls.py -> master url set
│   │   wsgi.py -> wsgi gateway... not in use in project.
│   │____init__.py
│
├───data -> data I manually imported
│       cambridge_ma.csv -> open address extract used to load the table in SQLITE
│       extract.txt -> quick explanation on how I loaded the data
│       houses_to_keep.txt -> Some sample Zillow addresses that had complete information
│
├───houses -> Zillow house search app that let's you search zillow for listings.
│   │   admin.py -> register addresses to search for zillow app in the admin.
│   │   apps.py -> Zillow house app.
│   │   forms.py -> Search form for doing a Zillow search
│   │   models.py -> Model for Addresses representing addresses from Open Addresses database
│   │   urls.py -> url for searching addresses zipcode/ and getting a specific zillow result house/<int:house_id>.
│   │__ views.py -> function supporting search functionality
│
├───liabilities -> loan management app
│   │   admin.py -> register loan_type, loan and loan payments models.
│   │   apps.py -> loan app import statement
│   │   forms.py -> Loan update and create form.
│   │   models.py -> loan_type, loan and loan payments models.
│   │   urls.py -> CRUD operations for loans, getting a amortization table
│   │__ views.py -> CRUD operations for loans, getting a amortization functions.
│
├───static
│   ├───css
│   │   │   styles.css -> final styles.css (not much honestly)
│   │   │   styles.css.map -> sass mapping
│   │   │__ styles.scss -> final styles.scss
│   │   
│   └───js
│           details.js -> set-up date picker...
│           index.js -> delete loan AJAX call for the index page and also formatting 3 tables as Data Tables.
│           payment.js -> data tables applied to all payment schedules...
│
└───templates
    ├───accounts ->  templates for accounts...
    │       signup.html -> copied from project 3, the sign-up page.  Changed the template.
    │
    ├───houses -> Zillow templates for house searching
    │       house.html -> Zillow query showing house information
    │       search.html -> Search box with results from address database
    │
    ├───liabilities -> Loan management templates
    │       details.html -> update or create new loan form.
    │       index.html -> summary of loans template
    │       payment-schedule.html -> Amortization template
    │
    ├───registration -> templates for accounts...
    │       login.html -> Login templates
    │
    └───templates -> templates
            base.html -> the base template


```

## Improvements
The list of improvements are so long that I don't know where to begin.  So instead, I will just list the 
things I think would be cool to do:

1. Summaries should have a date filter that shows you your financial situation based on a given date.
2. The Amortization table should be editable so that you can deal with cent rounding errors (based on
banks choice on how they round this).
3. Detail page for loans should accept percent in integer + decimal format not just decimal format.
4.  Ton of aggregate information such as total cost of loan etc.

Other major ideas involve building out new apps from scratch including ones for income, investment and
other assets.  The idea being you can figure out your cashflow and future cashflow.  Use this app
to do things like inform your budget or see if you can handle an additonal loan.

IT would also be cool if I worked on the UI a bit more and made it easier for people right out of 
highschool to use it.  By adding some educational tooling around the app.

## Sources:
Zillow is the main source of housing data including all photos.  They are direct pulls from the API:
http://www.zillow.com/ 

You'll notice a ton of branding required on the page to use it on the website.  Including a ton of links
to Zillow and Zestimate.

OpenAddresses.io is the main source of Cambridge, Ma addresses.  See the below:
https://openaddresses.io/

The process to get Cambridge, Ma open address data is present in CompareRate/data/extract.txt.  Please 
note, I decided against using Python inserts and opted for just using SQLITE client tool to upload 
a CSV and do a one time upload.  I decided to use Sqlite3 so that you didn't have to do this yourself.
