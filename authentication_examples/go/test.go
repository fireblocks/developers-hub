package main

import (
	"bytes"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/golang-jwt/jwt"
	"github.com/google/uuid"
)

type ApiTokenProvider struct {
	privateKey *rsa.PrivateKey
	apiKey     string
}

func NewApiTokenProvider(privateKeyPath, apiKey string) (*ApiTokenProvider, error) {
	privateKeyBytes, err := os.ReadFile(privateKeyPath)
	if err != nil {
		return nil, fmt.Errorf("error reading private key from %s: %w", privateKeyPath, err)
	}

	privateKey, err := jwt.ParseRSAPrivateKeyFromPEM(privateKeyBytes)
	if err != nil {
		return nil, fmt.Errorf("error parsing RSA private key: %w", err)
	}

	return &ApiTokenProvider{
		privateKey: privateKey,
		apiKey:     apiKey,
	}, nil
}

func (a *ApiTokenProvider) SignJwt(path string, bodyJson interface{}) (string, error) {
	nonce := uuid.New().String()
	now := time.Now().Unix()
	expiration := now + 55 // Consider making this configurable

	bodyBytes, err := json.Marshal(bodyJson)
	if err != nil {
		return "", fmt.Errorf("error marshaling JSON: %w", err)
	}

	h := sha256.New()
	h.Write(bodyBytes)
	hashed := h.Sum(nil)

	claims := jwt.MapClaims{
		"uri":      path,
		"nonce":    nonce,
		"iat":      now,
		"exp":      expiration,
		"sub":      a.apiKey,
		"bodyHash": hex.EncodeToString(hashed),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
	tokenString, err := token.SignedString(a.privateKey)
	if err != nil {
		return "", fmt.Errorf("error signing token: %w", err)
	}

	return tokenString, nil
}

var httpClient = &http.Client{} // Reuse HTTP client

func makeAPIRequest(method, path string, body interface{}, tokenProvider *ApiTokenProvider) ([]byte, error) {
	var url = "https://api.fireblocks.io" + path

	var reqBodyBytes []byte
	if body != nil {
		var err error
		reqBodyBytes, err = json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("error marshaling request body: %w", err)
		}
	}

	token, err := tokenProvider.SignJwt(path, body)
	if err != nil {
		return nil, fmt.Errorf("error signing JWT: %w", err)
	}

	req, err := http.NewRequest(method, url, bytes.NewBuffer(reqBodyBytes))
	if err != nil {
		return nil, fmt.Errorf("error creating HTTP request: %w", err)
	}

	if method == "POST" {
		req.Header.Set("Content-Type", "application/json")
	}

	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("X-API-KEY", tokenProvider.apiKey)

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending HTTP request: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	return respBody, nil
}

// getAccountsPaged makes a GET request to retrieve paged accounts
func getAccountsPaged(tokenProvider *ApiTokenProvider) error {
	path := "/v1/vault/accounts_paged"
	respBody, err := makeAPIRequest("GET", path, nil, tokenProvider)
	if err != nil {
		return fmt.Errorf("error making GET request to accounts_paged: %w", err)
	}

	fmt.Printf("Response body for accounts_paged: %s\n", string(respBody))
	return nil
}

// createAccount makes a POST request to create a new account
func createAccount(tokenProvider *ApiTokenProvider) error {
	path := "/v1/vault/accounts"
	body := map[string]interface{}{
		"name":       "MyGoVault",
		"hiddenOnUI": true,
	}

	respBody, err := makeAPIRequest("POST", path, body, tokenProvider)
	if err != nil {
		return fmt.Errorf("error making POST request to create account: %w", err)
	}

	fmt.Printf("Response body for createAccount: %s\n", string(respBody))
	return nil
}

// Main function
func main() {
	privateKeyPath := "SECRET_KEY_PATH"
	apiKey := "API_KEY"
	tokenProvider, err := NewApiTokenProvider(privateKeyPath, apiKey)
	if err != nil {
		fmt.Printf("Error initializing token provider: %v\n", err)
		return
	}

	// Example API calls
	// Ensure functions getAccountsPaged and createAccount are correctly defined to use this main function.
	err = getAccountsPaged(tokenProvider)
	if err != nil {
		fmt.Printf("Error calling getAccountsPaged: %v\n", err)
	}

	err = createAccount(tokenProvider)
	if err != nil {
		fmt.Printf("Error calling createAccount: %v\n", err)
	}
}
