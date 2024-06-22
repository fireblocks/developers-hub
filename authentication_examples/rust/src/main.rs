mod types;

use crate::types::*;
use chrono::Utc;
use jsonwebtoken::{encode, Algorithm, EncodingKey, Header};
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, CONTENT_TYPE};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fmt::format;
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct Claims {
    uri: String,
    nonce: String,
    iat: i64,
    exp: i64,
    sub: String,
    #[serde(rename = "bodyHash")]
    body_hash: String,
}

pub struct ApiTokenProvider {
    private_key: String,
    api_key: String,
    api_url: String, // Added api_url field
}

impl ApiTokenProvider {
    pub fn new(private_key: String, api_key: String, api_url: String) -> Self {
        ApiTokenProvider {
            private_key,
            api_key,
            api_url,
        }
    }

    pub fn sign_jwt(
        &self,
        path: &str,
        body: Option<&str>,
    ) -> Result<String, jsonwebtoken::errors::Error> {
        let now = Utc::now().timestamp();
        let nonce = Uuid::new_v4().to_string();
        let body_hash = match body {
            Some(b) => hex::encode(Sha256::digest(b.as_bytes())),
            None => hex::encode(Sha256::digest("".as_bytes())),
        };

        let claims = Claims {
            uri: path.to_owned(),
            nonce,
            iat: now,
            exp: now + 30, // Adjusted to ensure it's within the required timeframe
            sub: self.api_key.clone(),
            body_hash,
        };

        let token = encode(
            &Header::new(Algorithm::RS256),
            &claims,
            &EncodingKey::from_rsa_pem(self.private_key.as_bytes())?,
        )?;
        Ok(token)
    }

    pub async fn get_request(&self, path: &str) -> Result<String, Box<dyn std::error::Error>> {
        let token = self.sign_jwt(path, None)?;

        let client = reqwest::Client::new();
        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", token))?,
        );
        headers.insert("X-API-Key", HeaderValue::from_str(&self.api_key)?);

        // Make the GET request
        let response = client
            .get(self.api_url.to_owned() + path) // Use api_url here
            .headers(headers)
            .send()
            .await?;

        // Check response status and return result
        if response.status().is_success() {
            let response_text = response.text().await?;
            Ok(response_text)
        } else {
            Err(format!(
                "GET Request failed with status: {}",
                response.status()
            ))?
        }
    }

    // TODO: add PagedVaultAccountsRequestFilters param
    pub async fn get_vaults(
        &self,
    ) -> Result<PagedVaultAccountsResponse, Box<dyn std::error::Error>> {
        let res = self.get_request("/v1/vault/accounts_paged").await?;
        let vaults: PagedVaultAccountsResponse = serde_json::from_str(&res).unwrap();
        print!("{:?}", vaults);
        Ok(vaults)
    }

    // TODO: Handle no vault found with that vaultid
    pub async fn get_vault_by_id(
        &self,
        vault_id: &str,
    ) -> Result<VaultAccountResponse, Box<dyn std::error::Error>> {
        let path = format!("/v1/vault/accounts/{}", vault_id);
        let res = self.get_request(&path).await?;
        let vault: VaultAccountResponse = serde_json::from_str(&res).unwrap();
        Ok(vault)
    }

    pub async fn get_vault_asset_by_id(
        &self,
        vault_id: &str,
        asset_id: &str,
    ) -> Result<AssetResponse, Box<dyn std::error::Error>> {
        let path = format!("/v1/vault/accounts/{}/{}", vault_id, asset_id);
        let res = self.get_request(&path).await?;
        let vault: AssetResponse = serde_json::from_str(&res).unwrap();
        Ok(vault)
    }

    pub async fn get_deposit_address(
        &self,
        vault_id: &str,
        asset_id: &str,
    ) -> Result<Vec<DepositAddressResponse>, Box<dyn std::error::Error>> {
        let path = format!("/v1/vault/accounts/{}/{}/addresses", vault_id, asset_id);
        let res = self.get_request(&path).await?;
        let vault: Vec<DepositAddressResponse> = serde_json::from_str(&res).unwrap();
        Ok(vault)
    }

    pub async fn get_utxo(
        &self,
        vault_id: &str,
        asset_id: &str,
    ) -> Result<Vec<UnspentInputsResponse>, Box<dyn std::error::Error>> {
        let path = format!(
            "/v1/vault/accounts/{}/{}/unspent_inputs",
            vault_id, asset_id
        );
        let res = self.get_request(&path).await?;
        let utxo: Vec<UnspentInputsResponse> = serde_json::from_str(&res).unwrap();
        Ok(utxo)
    }

    pub async fn get_supported_assets(
        &self,
    ) -> Result<Vec<AssetTypeResponse>, Box<dyn std::error::Error>> {
        let res = self.get_request("/v1/supported_assets").await?;
        let trimmed_res = res.trim();
        let result = serde_json::from_str::<Vec<AssetTypeResponse>>(trimmed_res);

        match result {
            Ok(supported) => {
                println!("Response:\n{:#?}", supported);
                Ok(supported)
            }
            Err(e) => {
                eprintln!("Failed to deserialize response: {:?}", trimmed_res);
                eprintln!("Deserialization error: {}", e);
                Err(Box::new(e))
            }
        }
    }

    // TODO: add Filter GetAssetWalletsFilters
    pub async fn get_asset_wallets(&self) -> Result<String, Box<dyn std::error::Error>> {
        let res = self.get_request("/v1/vault/asset_wallets").await?;
        println!("RAW JSON from Fireblocks API:\n {:#?}", res);
        // TODO: Serialize into Get AssetWalletResponse instead of just JSON
        // let assets: GetAssetWalletsResponse = serde_json::from_str(&res).unwrap();
        // print!("{:?}", assets);
        Ok(res)
    }

    pub async fn post_request(
        &self,
        path: &str,
        body: &str,
    ) -> Result<String, Box<dyn std::error::Error>> {
        let token = self.sign_jwt(path, Some(body))?;

        let client = reqwest::Client::new();
        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", token))?,
        );
        headers.insert("X-API-Key", HeaderValue::from_str(&self.api_key)?);

        // Make the POST request
        let response = client
            .post(self.api_url.to_owned() + path) // Use api_url here
            .headers(headers)
            .header(CONTENT_TYPE, "application/json") // Set Content-Type header
            .body(body.to_string())
            .send()
            .await?;

        // Check response status and return result
        if response.status().is_success() {
            let response_text = response.text().await?;
            Ok(response_text)
        } else {
            Err(format!(
                "POST Request failed with status: {}",
                response.status()
            ))?
        }
    }

    pub async fn refresh_vault(
        &self,
        vault_id: &str,
        asset_id: &str,
        request_opts: &RequestOptions,
    ) -> Result<AssetResponse, Box<dyn std::error::Error>> {
        let path = format!("/v1/vault/accounts/{vault_id}/{asset_id}/balance");
        let json_args = serde_json::to_string(request_opts)?;
        let res = self.post_request(&path, &json_args).await?;

        let refresh_res: AssetResponse = serde_json::from_str(&res)?;
        Ok(refresh_res)
    }

    pub async fn create_vault(
        &self,
        name: &str,
        hidden_on_ui: bool,
        customer_ref_id: &str,
        auto_fuel: bool,
    ) -> Result<VaultAccountResponse, Box<dyn std::error::Error>> {
        println!("Creating Vault account");
        let body = CreateVaultRequest {
            name: name.to_string(),
            hidden_on_ui,
            customer_ref_id: Option::from(customer_ref_id.to_string()),
            auto_fuel,
        };

        let json_args = serde_json::to_string(&body)?;
        let res = self.post_request("/v1/vault/accounts", &json_args).await?;

        let create_vault_res: VaultAccountResponse = serde_json::from_str(&res)?;
        Ok(create_vault_res)
    }
    pub async fn create_tx(
        &self,
        tx_args: &TransactionArguments,
    ) -> Result<CreateTransactionResponse, Box<dyn std::error::Error>> {
        println!("Creating transaction with arguments: {:#?}", tx_args);
        let json_args = serde_json::to_string(tx_args)?;
        let res = self.post_request("/v1/transactions", &json_args).await?;

        let create_tx_response: CreateTransactionResponse = serde_json::from_str(&res)?;
        println!("Create transaction response:\n{:#?}", create_tx_response);
        Ok(create_tx_response)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let api_key = "API_KEY".to_string();
    let private_key = "API_SECRET_KEY_PATH";
    let api_url = "https://api.fireblocks.io".to_string(); // For sandbox use: https://sandbox-api.fireblocks.io

    let fireblocks =
        ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
    let tx = TransactionArguments {
        asset_id: "ETH_TEST5".to_string(),
        operation: TransactionOperation::TRANSFER,
        source: TransferPeerPath {
            peer_type: PeerType::VAULT_ACCOUNT,
            id: "0".to_string(),
        },
        destination: Some(DestinationTransferPeerPath {
            peer_type: PeerType::VAULT_ACCOUNT,
            id: "0".to_string(),
        }),
        amount: "1.0".to_string(),
        note: "Sample transaction".to_string(),
    };
    println!("Creating TX");
    let c = fireblocks.create_tx(&tx).await?;
    println!("Sumitted TX: {:#?}", c);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tokio::test;

    #[tokio::test]
    async fn test_get_supported() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string(); // For sandbox use: https://sandbox-api.fireblocks.io

        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());

        match fireblocks.get_supported_assets().await {
            Ok(s) => {
                println!("Supported Assets: {:#?}", s);
            }
            Err(e) => {
                eprintln!("Error fetching supported assets: {}", e);
                assert!(false);
            }
        }
    }

    #[tokio::test]
    async fn test_get_wallets() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());

        match fireblocks.get_asset_wallets().await {
            Ok(s) => {
                println!("Test: {:#?}", s);
            }
            Err(e) => {
                eprintln!("Error fetching wallet assets: {}", e);
                assert!(false);
            }
        }
    }

    #[test]
    async fn test_create_vault() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
        let c = fireblocks.create_vault("Test", false, "2", true).await;
        println!("{:#?}", c)
    }

    #[test]
    async fn test_get_vault_by_id() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
        let c = fireblocks.get_vault_by_id("1").await.unwrap();
        println!("{:#?}", c)
    }

    #[test]
    async fn test_get_vault_asset_by_id() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
        let c = fireblocks.get_vault_asset_by_id("0", "ETH").await.unwrap();
        println!("{:#?}", c)
    }

    #[test]
    async fn test_get_deposit_addr() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
        let c = fireblocks.get_deposit_address("0", "ETH").await.unwrap();
        println!("{:#?}", c)
    }

    #[test]
    async fn test_get_utxo() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
        let c = fireblocks.get_utxo("0", "BTC").await.unwrap();
        println!("{:#?}", c)
    }
    #[test]
    async fn test_refresh() {
        let api_key = "API_KEY".to_string();
        let private_key = "API_SECRET_KEY_PATH";
        let api_url = "https://api.fireblocks.io".to_string();
        let fireblocks =
            ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());
        let c = fireblocks
            .refresh_vault(
                "0",
                "ETH",
                &RequestOptions {
                    idempotency_key: None,
                    ncw: None,
                },
            )
            .await
            .unwrap();
        println!("{:#?}", c)
    }
}
