use jsonwebtoken::{encode, Algorithm, EncodingKey, Header};
use serde::{Serialize, Deserialize};
use sha2::{Sha256, Digest};
use uuid::Uuid;
use chrono::Utc;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, CONTENT_TYPE};

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    uri: String,
    nonce: String,
    iat: i64,
    exp: i64,
    sub: String,
    bodyHash: String,
}

pub struct ApiTokenProvider {
    private_key: String,
    api_key: String,
    api_url: String, // Added api_url field
}

impl ApiTokenProvider {
    pub fn new(private_key: String, api_key: String, api_url: String) -> Self {
        ApiTokenProvider { private_key, api_key, api_url }
    }

    pub fn sign_jwt(&self, path: &str, body: Option<&str>) -> Result<String, jsonwebtoken::errors::Error> {
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
            bodyHash: body_hash,
        };

        let token = encode(&Header::new(Algorithm::RS256), &claims, &EncodingKey::from_rsa_pem(self.private_key.as_bytes())?)?;
        Ok(token)
    }

    pub async fn get_request(&self, path: &str) -> Result<String, Box<dyn std::error::Error>> {
        let token = self.sign_jwt(path, None)?;

        let client = reqwest::Client::new();
        let mut headers = HeaderMap::new();
        headers.insert(AUTHORIZATION, HeaderValue::from_str(&format!("Bearer {}", token))?);
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
            Err(format!("GET Request failed with status: {}", response.status()))?
        }
    }

    pub async fn post_request(&self, path: &str, body: &str) -> Result<String, Box<dyn std::error::Error>> {
        let token = self.sign_jwt(path, Some(body))?;

        let client = reqwest::Client::new();
        let mut headers = HeaderMap::new();
        headers.insert(AUTHORIZATION, HeaderValue::from_str(&format!("Bearer {}", token))?);
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
            Err(format!("POST Request failed with status: {}", response.status()))?
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let api_key = "b4ccc098-897f-4696-94b4-34e8e312667b".to_string();
    let private_key = include_str!("/Users/slavaserebriannyi/api_keys/fireblocks_secret.key");
    let api_url = "https://api.fireblocks.io".to_string(); // For sandbox use: https://sandbox-api.fireblocks.io
    
    let provider = ApiTokenProvider::new(private_key.to_string(), api_key.clone(), api_url.clone());

    // Call GET request
    let get_response = provider.get_request("/v1/vault/accounts_paged").await?;
    println!("GET Response: {}", get_response);

    // Call POST request
    let body = serde_json::json!({
        "name": "MyRustVault",
        "hiddenOnUI": true,
    });
    let post_response = provider.post_request("/v1/vault/accounts", &body.to_string()).await?;
    println!("POST Response: {}", post_response);

    Ok(())
}
