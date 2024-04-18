## Basic Plugins ⚾
### Transaction Validation Plugin (`txid_validation.py/TxidValidation` class)
Being executed on `POST /v2/tx_sign_request`.
The plugin gets the transaction ID (txId) from the payload sent from the Co-Signer and check against a given DB if the same transaction ID exists. \
Purpose - validate that the arrived transaction was not initiated by some external actor and is known to the operator. 

#### Flow:
1. API client initiates transaction via Fireblocks API
2. Fireblocks API returns 200OK with a unique transaction identifier and status 'SUBMITTED'
3. The transaction ID is being saved in user's DB 
4. The transaction hits the Co-Signer machine that forwards the request to the configured callback handler
5. The callback handler runs the Transaction Validation Plugin 
6. The plugin extracts the transaction ID (txId) from the received data
7. The plugin accesses the provided DB instance and checks if the same txId exists
8. If true -> returns `APPROVE` else returns `REJECT`

#### Requirements:
1. Supported DB connection (`DB_TYPE` in .env file)
2. DB access credentials:
   - Username (`DB_USER` in .env file)
   - Password (`DB_PASSWORD` in .env file)
   - Host (`DB_HOST` in .env file)
   - Port (`DB_PORT` in .env file if applicable)
   - DB Name (`DB_NAME` in .env file)
   - DB Table/Collection name (`DB_TABLE` in .env file)
   - Transaction ID DB Column/Field name (`DB_COLUMN` in .env file)

### Extra Signature Validation (`extra_signature.py/ExtraSignature` class)
Being executed on `POST /v2/tx_sign_request`.
The plugin expects to receive an extra message and a signature of this message, checks that the message is signed by a known signer (by holding a pre-defined public key). \
Purpose - validate that the arrived transaction was initiated only by a pre-defined signer that holds a corresponding private key.

#### Flow:
1. API client initiates transaction via Fireblocks API
2. The transaction contains `extraSignature` and `message` strings within the `extraParameters` object, transaction payload for example:
   ```javascript
    {
      assetId: 'BTC',
      amount: 1,
      source: { ... },
      destination: { ... },
      extraParameters: {
        extraSignature: signed(`MyExampleMessage`),
        message: 'MyExampleMessage'
      }
    }
   ```
3. Fireblocks API returns 200OK with a unique transaction identifier and status 'SUBMITTED'
4. The transaction hits the Co-Signer machine that forwards the request to the configured callback handler
5. The callback handler runs the Extra Signature Validation plugin
6. The plugin retrieves the message from the `message` and the signature from the `extraSignature` fields
7. The plugin loads a pre-defined public key and verifies the given signature
8. If true -> returns `APPROVE` else returns `REJECT`

#### Requirements:
1. Public key file path for extra signature verification (`EXTRA_SIGNATURE_PUBLIC_KEY_PATH` var in .env file) 
2. Currently the supported signature algorithm is - `RSA-SHA256`

### Transaction Policy Validation Plugin (`tx_policy_validation.py/TxPolicyValidation` class)
Being executed on `POST /v2/tx_sign_request`.
The plugin validates that the transaction is allowed by the defined policy. \
Purpose - Customize policy programmatically, supporting your specific usecase. 

#### Flow:
1. API client initiates transaction via Fireblocks API 
2. The transaction hits the Co-Signer machine that forwards the request to the configured callback handler
3. The callback handler runs the Transaction Policy Validation Plugin
4. The plugin fetches the active transaction policy, or the user can define a custom policy
5. The plugin checks the transaction against the policy, determines if it is allowed or not
6. If true -> returns `APPROVE` else returns `REJECT`

#### Requirements:
Fireblocks API Credentials
   - API Key (`FIREBLOCKS_API_KEY` in .env file)
   - API Private Key Path (`FIREBLOCKS_API_PRIVATE_KEY_PATH=` in .env file)

---