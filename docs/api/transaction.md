# Deposits
Supports depositing funds from bank

## Make a deposit from your bank account

**Request**:

`POST` `/users/:user_id/deposits`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
bank       | id     | Yes      | users bank account
amount     | float  | Yes      | amount to be deposited


*Note:*

- Authorization Protected

**Response**:

```json
Content-Type application/json
201 Created

{
    "success": true,
    "message": "successful",
    "data": {
        "id": "bb53cccb-7d53-4ee8-9a41-2b5f7c798105",
        "owner": "e9d28e78-a5cd-4af9-a2a4-e6e05b22d9c3",
        "reference": "a7edb0e62c92f553e68f1c2b",
        "status": "success",
        "amount": 1000.0,
        "bank": 4,
        "new_balance": 10000.0,
        "banking_details": {
            "id": 4,
            "owner": "e9d28e78-a5cd-4af9-a2a4-e6e05b22d9c3",
            "bank": "ff6daa06-c4a7-4e28-8fa6-9e82a9def29e",
            "account_name": "ALADE Oladele Tumise",
            "account_number": "0229564465",
            "account_type": "savings"
        },
        "created": "2021-06-07T21:25:37+0100"
    }
}
```