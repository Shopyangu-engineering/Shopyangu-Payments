<p align="left"><a href="https://www.shopyangu.com/" target="_blank"><img src="assets/logo.png" width="140"></a></p>


# Shopyangu Payments  :kes: :dollar: :pound: :yen: :euro:

> Payment Library For Most Public Payment API's in Kenya and hopefully Africa.


## Table of contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Contributors](#contributors)
- [Licence](#licence)


## Features

- [x] Mpesa
  - [x] Mpesa Express (STK)
  - [x] Transaction Status


## Coming Soon Features
- [x] Mpesa
  - [x] STK Transaction Validation
  - [x] B2C
  - [x] B2B
  - [x] C2B
  - [x] Reversal
  - [x] Account Balance
- [x] JengaWS(Equity)
  - [ ] Send Money
  - [ ] Send Money Queries
  - [ ] Receive Money
  - [ ] Receive Money Queries
  - [ ] Buy Goods, Pay Bills, Get Airtime
  - [ ] Airtime
  - [ ] Reg Tech: KYC, AML, & CDD API
  - [ ] Account Services
  - [ ] Forex Rates
- [ ] Paypal
- [ ] Card
- [ ] iPay



## Installation
`pip install shopyangu-payments`


## Requirements 

- Python 3.6+
- Django 2.2.9+
- djangorestframework 3.12.2
- requests 2.25.1+
- python-decouple 3.3+


## Setup

Add the following in the `urls.py`
```python
urlpatterns = [
    ...
    path('payments/', include('shopyangu_payments.urls', 'shopyangu_payments')),
    ...
]
```


Add the following to installed apps

```python
INSTALLED_APPS = [
    ...
    'shopyangu-payments',
    ...
```