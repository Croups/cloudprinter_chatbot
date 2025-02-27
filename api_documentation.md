Cloudprinter Core API
This documentation describes the Cloudprinter Core API v1.0


Getting started
To get started with Cloudprinter please register online here: Client registration


Basics

RESTful API
The Cloudprinter API is RESTful API. All API calls are implemented as HTTP post. The HTTP response codes 200 and 201 are positive responses, all other response codes must be considered as error. Data will only be returned for HTTP response code 200. Error descriptions can be returned on 4xx response codes.


Request Data
All request data posted to the API must be in JSON objects. The documentation for each API call describes the request data parameters in detail.


Return Data
Return data from the API is in JSON objects. The documentation for each API call describes the return values in detail.


Content-type
Set content-type to application/json on all requests.


Authentication
Each request to the API contains an API key for authentication. API keys are created in the Cloudprinter admin system under CloudCore API Interface.


Order calls

List all orders

https://api.cloudprinter.com/cloudcore/1.0/orders/
Request a list of all orders

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/orders/,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


[
    {
        "reference": "12346",
        "order_date": "2015-08-05 10:00:00",
        "state": "1",
        "state_code": "order_state_new"
    },
    {
        "reference": "12348",
        "order_date": "2015-08-05 10:00:00",
        "state": "1",
        "state_code": "order_state_new"
    }
]
1
2
3
4
5
6
7
8
9
10
11
12
13
14
Parameters

Name	Type	Description
apikey
string	Api access key
Return values

Name	Type	Description
reference
string	The clients own order reference identifier
state
string	The order state. See state definitions
state_code
string	The text version of the order state
order_date
string	The time the order was added
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
204
No content	The requested order was not found
400
Bad request	The request was invalid or parameters are missing
403
Forbidden	The request was denied due to missing credentils

Get order info:

https://api.cloudprinter.com/cloudcore/1.0/orders/info
Request details on a specific order

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/orders/info,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "reference": "12346"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response



{
  "reference": "123456",
  "state": "45",
  "state_code": "order_state_uploaded",
  "order_date": "2017-02-01 11:22:33",
  "email": "customer1@example.com",
  "addresses": [
    {
      "type": "delivery",
      "firstname": "John",
      "lastname": "Doe",
      "street1": "Example street",
      "zip": "1234",
      "city": "Example city",
      "state": "Example state",
      "country": "NL"
    }
  ],
  "items": [
    {
      "reference": "123561",
      "name": "book_hardcover_21x21",
      "count": "1",
      "shipping_option": "DHL - National Standard (DE)",
      "tracking": "FEDEX",
      "options": [
        {
          "type": "total_pages",
          "count": "24"
        },
        {
          "type": "gloss_pages_170g",
          "count": "24"
        },
        {
          "type": "gloss_laminate_cover",
          "count": "1"
        }
      ],
      "files": [
      	{
      	  "type": "cover",
      	  "url": "https://download.example.com/files/9aade201b3a85ceec318b2240d5eb373",
      	  "md5sum": "4578c3ecf64e47581b175d542f8b0160"
      	},
      	{
      	  "type": "book",
      	  "url": "https://download.example.com/files/c4b5a0b95114f40fc8c9d4e7cd504290",
      	  "md5sum": "1ef89e74e628e223ae94aa4586330833"
      	}
      ]
    }
  ]
}
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
Parameters

Name	Type	Description
apikey
string	Api access key
reference
string	The clients own order reference identifier
Return values

Name	Type	Description
reference
string	The clients own order reference identifier
state
string	The order state. See state definitions
state_code
string	The text version of the order state
order_date
string	The time the order was added
email
string	The email address of the end consumer
Addresses	Type	Description
addresses
array	Array of one or more address objects
addresses : type
string	The addres type (delivery)
addresses : firstname
string	Firstname of the recipient
addresses : lastname
string	Lastname of the recipient
addresses : street1
string	Street
addresses : zip
string	Zip
addresses : city
string	City
addresses : state
string	State ANSI INCITS 38:2009 alpha-2
addresses : country
string	Country - ISO 3166-1 alpha-2
Items	Type	Description
items
array	Array of one or more item objects
items : reference
string	The clients item reference id
items : name
string	The name of the item
items : count
string	The quantity of the item
items:shipping_option
string	the shipping option of the item
items : tracking
string	Tracking code of the item
Item options	Type	Description
options
array	Array of zero or more option objects
options : type
string	The option type
options : count
string	The quantity of the option
Files	Type	Description
files
array	Array of one or more file objects
files : type
string	The type of file
files : md5
string	Md5 sum of the file - used for validation
files : url
string	Url to the order file
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
400
Bad request	The request was invalid or parameters are missing
410
Gone	The requested order was not found

Add order:

https://api.cloudprinter.com/cloudcore/1.0/orders/add
Add a new order including one or more items, adresses, options and files.

Note: Files are added with a URL from where Cloudprinter can fetch the files when the order has been accepted. A TLS encrypted HTTPS connection, use of an access key in the query string and use of a network access control list is recomented.

Example: "https://download.example.com/files/28fa76ff5a9e0566eaa1e11f1ce51f09"

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/orders/add,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "reference": "12346",
  "email": "support@client-company.com",
  "addresses": [
    {
      "type": "delivery",
      "company": "Example company",
      "firstname": "Example firstname",
      "lastname": "Example lastname",
      "street1": "Example street 1234",
      "zip": "99999",
      "city": "Example city",
      "country": "DE",
      "email": "email@example.com",
      "phone": "12345678"
    }
  ],
  "items": [
    {
      "reference": "12346-1",
      "product": "book_hardcover_21x30",
      "shipping_level": "cp_saver",
      "title": "Book Hardcover 21x30",
      "count": "5",
      "files": [
        {
          "type": "cover",
          "url": "https://download.example.com/files/9aade201b3a85ceec318b2240d5eb373",
          "md5sum": "4578c3ecf64e47581b175d542f8b0160"
        },
        {
          "type": "book",
          "url": "https://download.example.com/files/c4b5a0b95114f40fc8c9d4e7cd504290",
          "md5sum": "1ef89e74e628e223ae94aa4586330833"
        }
      ],
      "options": [
        {
          "type": "total_pages",
          "count": "36"
        },
        {
          "type": "paper_130mcg",
          "count": "36"
        }
      ]
    }
  ]
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


{
    "order": "12346"
}
1
2
3
Parameters

Name	Type	Description
apikey
string	Api access key
reference
string	The clients own order reference identifier - this must be unique among all orders
email
string	Email address of the clints support team for contact regarding processing and production issues
price
string	End customer sales price ex. vat/tax pr item in selected currency - comma as decimal separator, used for customs
currency
string	The currency of the end customer sales price - ISO 4217
hc
string	Harmonized code - classify product according to Harmonized System
meta
array	Meta data array for custom production parameters - only available for Enterprise clients
addresses		
addresses
array	Array of one or more address objects
addresses : type
string	The type of address - valid values are: "delivery"
addresses : company
string	End customers company name
addresses : firstname
string	End customers firstname
addresses : lastname
string	End customers lastname
addresses : street1
string	End customers street name
addresses : street2
string	End customers street name
addresses : zip
string	End customers zip/postal code
addresses : city
string	End customers city name
addresses : state
string	End customers state name - ANSI INCITS 38:2009 alpha-2 - required for US and CA
addresses : country
string	End customers country - ISO 3166-1 alpha-2
addresses : email
string	End customers email address - used in case of problems during delivery
addresses : phone
string	End customers phone number - used in case of problems during delivery
addresses : customer_identification
string	End customers identification information - Read more
files		
files
array	Array of zero or more file objects
files : type
string	The type of file - valid values are: "delivery_note", "promotion"
files : url
string	Url to the order file
files : md5sum
string	Md5 sum of the file - used for validation
items		
items
array	Array of one or more item objects
items : reference
string	The clients own item reference identifier - this must be unique with in the order
items : product
string	The name of the product - valid values can be requested via Products Calls
items : count
string	The number of copies to produce of this specific item
items : shipping_level
string	The preferred shipping level - standard options are: "cp_postal", "cp_ground", "cp_saver", "cp_fast" (required if no "quote" hash is set)
items : quote
string	A quote hash reference from a quote call.
items : title
string	The title of the product
items : price
string	End customer sales price ex. vat/tax in selected currency - comma as decimal separator, used for customs
items : currency
string	The currency of the end customer sales price - ISO 4217
items : hc
string	Harmonized code - classify product according to Harmonized System
items : reorder_cause
string	Reorder cause for reorders - Read more
items : reorder_desc
string	Additional description of the problem - Read more
items : reorder_order_reference
string	Reference to the original order - Read more
items : reorder_item_reference
string	Reference to the item in the original order - Read more
items files		
items : files
array	Array of one or more file objects
items : files : type
string	The type of file - valid values are: "product", "cover", "book"
items : files : url
string	Url to the product file for the specific item
items : files : md5sum
string	Md5 sum of the file - used for validation
items options		
items : options
array	Array of zero or more option objects
items : options : type
string	The type of option - "total_pages" required for books, adding papertype eg. 130mcg is recomended
items : options : count
string	The number of times the specific option is used pr item
Return values

Name	Type	Description
order
string	The clients own order reference identifier
HTTP status codes

Code	Status	Description
201
Created	The order registration was created with success
400
Bad request	The request was invalid or parameters are missing

Cancel order:

https://api.cloudprinter.com/cloudcore/1.0/orders/cancel
Request cancellation of a specific order.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/orders/cancel,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "reference": "12346"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Parameters

Name	Type	Description
apikey
string	Api access key
reference
string	The clients own order reference identifier
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
400
Bad request	The request was invalid or parameters are missing
403
Forbidden	The request was denied due to missing credentils
409
Conflict	The request failed due to wrong order state
410
Gone	The requested order was not found

Order log:

https://api.cloudprinter.com/cloudcore/1.0/orders/log
Request log data for a specific order.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/orders/log,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "reference": "12346"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response



[
    {
        "reference": "12346",
        "create_date": "2016-04-12 12:37:01",
        "state": "5"
    },
    {
        "reference": "12346",
        "create_date": "2016-04-12 12:37:02",
        "state": "6"
    }
]
1
2
3
4
5
6
7
8
9
10
11
12
13
Parameters

Name	Type	Description
apikey
string	Api access key
reference
string	The clients own order reference identifier
Return values

Name	Type	Description
reference
string	The clients own order reference identifier
create_date
string	The date and time of the state change
state
string	The order state. See state definitions
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
204
No content	The requested order was not found
400
Bad request	The request was invalid or parameters are missing

Order quote:

https://api.cloudprinter.com/cloudcore/1.0/orders/quote
Request quote data for a list of items

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/orders/quote,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "country": "NL",
  "items": [
    {
      "reference": "ref_id_1234567",
      "product": "textbook_pb_a4_p_bw",
      "count": "1",
      "options": [
        {
            "type": "pageblock_80off",
            "count": "120"
        },
        {
            "type": "total_pages",
            "count": "120"
        }
      ]
    }
  ]
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response



{
  "price": "4.5412",
  "vat": "0.00",
  "currency": "EUR",
  "expire_date": "2021-04-18T15:32:58+00:00",
  "subtotals": {
    "items": "1.7912",
    "fee": "2.7500",
    "app_fee": "0.0000"
  },
  "shipments": [
    {
      "total_weight": "712",
      "items": [
        {
          "reference": "ref_id_1234567"
        }
      ],
      "quotes": [
        {
          "quote": "a1e771f2e375bc33b5385fcc8091a328481bc45f3bff13de96ba0e7585ff936f",
          "service": "Postal - Untracked",
          "shipping_level": "cp_postal",
          "shipping_option": "National Post - Int. Postal Untracked",
          "price": "4.2000",
          "vat": "0.0000",
          "currency": "EUR"
        },
        {
          "quote": "90aa928c65b6115e2fd76f5c3238381e42630fbe6cd137422db469fb070b5f7f",
          "service": "Express ground - Tracked",
          "shipping_level": "cp_ground",
          "shipping_option": "National Post - Int. Postal Tracked",
          "price": "6.2300",
          "vat": "0.0000",
          "currency": "EUR"
        },
        {
          "quote": "c6159e6c0a1b3e2d4ad7be940a327fb139351149e9f7ad7a1295a534cc37a4c3",
          "service": "Express fast - Tracked",
          "shipping_level": "cp_fast",
          "shipping_option": "DHL - International Express",
          "price": "14.5000",
          "vat": "0.0000",
          "currency": "EUR"
        }
      ]
    }
  ],
  "invoice_currency": "EUR",
  "invoice_exchange_rate": "1.0000"
}
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
Parameters

Name	Type	Description
apikey
string	Api access key
currency
string	The currency of the price quote - ISO 4217 - default value is EUR
country
string	The country the order will ship to
state
string	End customers state name - ANSI INCITS 38:2009 alpha-2 - required for US
items
array	Array of item objects in the order
items : reference
string	Client item reference
items : product
string	The product id
items : count
string	The product quantity
items : options
array	Array of option objects on a item
items : options : type
string	The option type
items : options : count
string	The option count
Return values

Name	Type	Description
price
string	The total product sum for the order, ex shipping and incl VAT
vat
string	The vat part of the total product sum
currency
string	The currency of the price quote
invoice_currency
string	The currency of the invoice for the order
invoice_exchange_rate
string	The currency exchange rate between the quote currency and invoice currency
expire_date
string	The quote expiration date, 48 hours after the request was made
subtotals
array	Array of objects - subtotals
subtotals : items
string	The sum of the item cost for the order
subtotals : fee
string	The sum of the fees for the order
subtotals : app_fee
string	The sum of the app fees for the order
shipments
array	Array of objects - shipments (item bundles)
shipments : total_weight
string	The calculated total weight of the shipment
shipments : items
array	Array of objects - the items contained in this shipment
shipments : items : reference
string	The item reference
shipments : quotes
array	Array of objects - available shipping options
shipments : quotes : quote
string	The unique quote id
shipments : quotes : service
string	The shipping service level name
shipments : quotes : shipping_level
string	The shipping service level reference
shipments : quotes : shipping_option
string	Text description of the specific shipping option
shipments : quotes : price
string	The price of the shipment incl VAT
shipments : quotes : vat
string	The vat part of the shipment
shipments : quotes : currency
string	The currency of the price quote
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
400
Bad request	The request was invalid or parameters are missing

Product calls:

List all products:

https://api.cloudprinter.com/cloudcore/1.0/products
Request a list of all products already enabled for the account.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/products,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


[
  {
    "name": "Textbook CW A6 P BW",
    "note": "Textbook Casewrap (PUR, 3 mm board) A6 Portrait DIG BW 80OFF",
    "reference": "textbook_cw_a6_p_bw",
    "category": "Textbook BW",
    "from_price": "3.33",
    "currency": "EUR"
  },
  {
    "name": "Textbook CW A5 P BW",
    "note": "Textbook Casewrap (PUR, 3 mm board) A5 Portrait DIG BW 80OFF",
    "reference": "textbook_cw_a5_p_bw",
    "category": "Textbook BW",
    "from_price": "4.44",
    "currency": "EUR"
  }
]
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
Parameters

Name	Type	Description
apikey
string	API access key
Return values

Name	Type	Description
name
string	Product short name
note
string	Product long description
reference
string	Product API reference
category
string	Product category
from_price
string	Product from price
currency
string	The currency in ISO 4217
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
204
No content	The requested order was not found
400
Bad request	The request was invalid or parameters are missing
403
Forbidden	The request was denied due to missing credentils

Product info:

https://api.cloudprinter.com/cloudcore/1.0/products/info
Get detailed information on a single product. This includes price on the base product and available options, as well as specs on the product.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/products/info,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "reference": "textbook_cw_a6_p_bw"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


{
  "name": "Textbook CW A6 P BW",
  "note": "Textbook Casewrap A6 Portrait Digital Toner BW",
  "reference": "textbook_cw_a6_p_bw",
    "prices": [ // Deprecated
    {
      "price": "-",
      "min": "100",
      "max": "9000",
      "note": "-",
      "reference": "-",
      "currency": "-",
      "price_unit": "-",
      "price_unit_type": "-",
      "type": "-"
    },
    {
      "price": "-",
      "min": "100",
      "max": "9000",
      "note": "-",
      "reference": "-",
      "currency": "-",
      "price_unit": "-",
      "price_unit_type": "-",
      "type": "-"
    },  	
    {
      "price": "-",
      "min": "100",
      "max": "9000",
      "note": "-",
      "reference": "-",
      "currency": "-",
      "price_unit": "-",
      "price_unit_type": "-",
      "type": "-"
    }
  ],
  "options": [
    {
      "reference": "cover_finish_matte",
      "note": "Cover lamination Matte finish",
      "type": "type_book_cover_finish",
      "default": 0
    },
    {
      "reference": "cover_finish_gloss",
      "note": "Cover lamination Gloss finish",
      "type": "type_book_cover_finish",
      "default": 1
    },
    {
      "reference": "pageblock_80off",
      "note": "Pageblock paper 80gsm Offset",
      "type": "type_book_paper",
      "default": 1
    },
    {
      "reference": "pageblock_130mcs",
      "note": "Pageblock paper 130gsm Machine Coated Silk",
      "type": "type_book_paper",
      "default": 0
    },
    {
      "reference": "cover_130mcg",
      "note": "Cover paper 130gsm Machine Coated Gloss",
      "type": "type_canvas_paper",
      "default": 1
    }
  ],
  "specs": [
    {
      "note": "Binding method / technology",
      "value": "CW - Casewrap"
    },
    {
      "note": "Bleed in mm",
      "value": "3"
    },
    {
      "note": "Cover overlap in mm",
      "value": "3"
    },
    {
      "note": "Cover squeeze in mm",
      "value": "5"
    },
    {
      "note": "Cover wrap in mm",
      "value": "18"
    },
    {
      "note": "Is the product orientation dependent",
      "value": "Yes"
    },
    {
      "note": "Minimum order quantity",
      "value": "1"
    },
    {
      "note": "Number of printable sides",
      "value": "2"
    },
    {
      "note": "Orientation of the product",
      "value": "Portrait"
    },
    {
      "note": "Per set order quantity",
      "value": "1"
    },
    {
      "note": "Size category",
      "value": "A6P"
    },
    {
      "note": "The exact height of the book in mm. after trimming",
      "value": "148"
    },
    {
      "note": "The exact width of the book in mm. after trimming",
      "value": "105"
    },
    {
      "note": "The page safety margin in mm",
      "value": "10"
    },
    {
      "note": "Colors on the back of the page",
      "value": "Black/White"
    },
    {
      "note": "Colors on the front of the page",
      "value": "Black/White"
    },
    {
      "note": "Print technology",
      "value": "Digital Toner"
    }
  ]
}
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
Parameters

Name	Type	Description
apikey
string	Api access key
reference
string	The reference of the product
Return values

Name	Type	Description
name
string	Product short name
note
string	Product long description
reference
string	Product API reference
Prices section is deprecated and will be removed after March 1, 2025. Use price/lookup for price calculation.

Name	Type	Description
prices
array	Array of price objects
prices : price
string	Product or option price
prices : min
string	Minimum item quantity range
prices : max
string	Maximum item quantity range
prices : note
string	Product long description
prices : reference
string	For options, the API reference
prices : currency
string	The currency in ISO 4217
prices : price_unit
string	The price unit type (Pr. Order, Pr. Item, Pr. Quantity, Pr. Page)
prices : type
string	Type of price (product, option)
Name	Type	Description
options
array	Array of option objects
options : reference
string	For options API reference
options : note
string	Option long description
options : type
string	Option category type
options : default
number	Default option flag (0, 1) - 1 for default - Default options work within options of the same option category type and only if not specified in the order
Name	Type	Description
specs
array	Array of spec objects
specs : note
string	Spec long description
specs : value
string	Spec value
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
204
No content	The requested order was not found
400
Bad request	The request was invalid or parameters are missing

List shipping levels:

https://api.cloudprinter.com/cloudcore/1.0/shipping/levels
Request a list of available shipping levels for the account.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/shipping/levels,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


[
  {
    "shipping_level_reference": "cp_saver",
    "shipping_level": "cp_saver",
    "name": "Express saver - Tracked",
    "note": "Saver express  - Fast saver tracked delivery - Cloudprinter shared"
  },
  {
    "shipping_level_reference": "cp_ground",
    "shipping_level": "cp_ground",
    "name": "Express ground - Tracked",
    "note": "Ground express - Fast ground delivery - Cloudprinter shared"
  }
]
1
2
3
4
5
6
7
8
9
10
11
12
13
14
Parameters

Name	Type	Description
apikey
string	API access key
Return values

Name	Type	Description
shipping_level_reference
string	Shipping level API reference
shipping_level
string	Shipping level API reference (to be deprecated)
name
string	Shipping level short name
note
string	Shipping level long description
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
400
Bad request	The request was invalid or parameters are missing
403
Forbidden	The request was denied due to missing credentils

Shipping countries:

https://api.cloudprinter.com/cloudcore/1.0/shipping/countries
Request a list of available shipping countries for the account.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/shipping/countries,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


[
  {
    "country_reference": "AE",
    "note": "United Arab Emirates",
    "require_state": 1
  },
  {
    "country_reference": "AF",
    "note": "Afghanistan",
    "require_state": 0
  }
]
1
2
3
4
5
6
7
8
9
10
11
12
Parameters

Name	Type	Description
apikey
string	Api access key
Return values

Name	Type	Description
country_reference
string	Shipping country short name
note
string	Shipping country long description
require_state
string	1 = Country requires state, 0 = Country does not require state
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
400
Bad request	The request was invalid or parameters are missing

Shipping states/regions:

https://api.cloudprinter.com/cloudcore/1.0/shipping/states
Request a list of available shipping countries for the account.

Example request


""

import requests
import json

url = "https://api.cloudprinter.com/cloudcore/1.0/shipping/states,"

payload = json.dumps({
  "apikey": "__YOUR_API_KEY__",
  "country_reference":"AE"
}
)
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
Example JSON Response


[
  {
      "state_reference": "AJ",
      "name": "Ajman",
      "note": "Ajman"
  },
  {
      "state_reference": "AZ",
      "name": "Abu Dhabi",
      "note": "Abu Dhabi"
  }
]
Parameters

Name	Type	Description
apikey
string	Api access key
country_reference
string	Country - ISO 3166-1 alpha-2
Return values

Name	Type	Description
state_reference
string	Shipping state reference
name
string	Shipping state short name
note
string	Shipping state long name
HTTP status codes

Code	Status	Description
200
OK	The request has succeeded
400
Bad request	The request was invalid or parameters are missing