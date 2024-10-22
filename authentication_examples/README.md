<p align="center">
  <img src="../logo.svg" width="350" alt="accessibility text">
</p>
<div align="center">

  [Fireblocks Developer Portal](https://developers.fireblocks.com) </br>
</div>


# Fireblocks API Authentication examples
In this repo you will find Fireblocks API authentication mechanism implementation examples in multiple programming languages.

- [Rust](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/rust)
- [Java](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/java/my-java-project)
- [PHP](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/php)
- [Go](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/go)
- [C#](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/cs)
- [Ruby](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/ruby)
- [Elixir](https://github.com/fireblocks/developers-hub/tree/main/authentication_examples/elixir)
The examples include the access token generation method (JWT) in addition to a GET and POST call examples.

⚠️ **Note**

- All examples have a hard encoded `base URL` for the Fireblocks production API. Make sure to find and update the base URL if you want to try these on the sandbox environment.

- Each request requires an API key and a signed JWT access token (signed with an API Secret key) as described below - please make sure to update the relevant variables with your API Key and API Secret key path.

---

## Fireblocks API Authentication scheme
Fireblocks uses API keys to authenticate all API calls. 

Depending on the type of workspace environment, the base API URL will be one of the following:

- Sandbox: https://sandbox-api.fireblocks.io/v1
- Production: https://api.fireblocks.io/v1

Every API request must contain the following headers:

- `X-API-Key` - The API Key created from your Fireblocks workspace.
- `Authorization` - This value should be set to `Bearer <Access Token>`. \
  The access token is a Base64-encoded JSON Web Token (`JWT`).

### JWT Structure
The payload field should contain the following fields:

- `uri` - The URI part of the request (e.g., /v1/transactions).
- `nonce` - Unique number or string. Each API request needs to have a different nonce.
- `iat` - The time at which the JWT was issued, in seconds since Epoch.
- `exp` - The expiration time on and after which the JWT must not be accepted for processing, in seconds since Epoch. (Must be less than iat+30sec.)
- `sub` - The API Key.
- `bodyHash` - Hex-encoded SHA-256 hash of the raw HTTP request body.

⚠️ **Note**

The JWT must be signed with the Fireblocks API secret key and the `RS256 (RSASSA-PKCS1-v1_5 using SHA-256 hash)` algorithm.

---


### Fireblocks API SDKs
Fireblocks released official API SDKs in the following programming languages:
- [JavaScript](https://github.com/fireblocks/fireblocks-sdk-js)
- [Python](https://github.com/fireblocks/fireblocks-sdk-py)

These SDK handle the entire authentication process for the user. The user just need to instatiate the relevant classes with the API Key and the API Secret values.

---

## Generate your client code from the Open API 3.0 (Swagger) specification
Fireblocks API specification is also available in [OpenAPI](https://github.com/fireblocks/fireblocks-openapi-spec) 3.0 format.

The users can generate client libraries by importing the OpenAPI spec into [Swagger Editor](https://editor.swagger.io/).

Once the file is imported click on *Generate Client* in top menu and choose the relevant programming language.

⚠️ **Note**

The Swagger Editor client library generation process will NOT generate the authentication mechanism as it's not specified in the OpenAPI Specification.

---

