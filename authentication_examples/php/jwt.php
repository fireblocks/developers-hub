<?php

// Dependencies (require Composer)
require 'vendor/autoload.php';

use Firebase\JWT\JWT;
use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;

// Define your private key, API key, and API endpoint
$privateKey = file_get_contents('SECRET_KEY_PATH'); // Replace with your private key file path
$apiKey = 'API_KEY'; // Replace with your API key
$baseUrl = 'https://api.fireblocks.io'; // For sandbox use: https://sandbox-api.fireblocks.io

// Function to generate a JWT token
function generateToken($privateKey, $apiKey, $path, $body = null) {
    $currentTime = time();
    $nonce = uniqid();
    $iat = $currentTime;
    $exp = $currentTime + 55;
    $sub = $apiKey;
    $bodyHash = hash('sha256', json_encode($body));

    $payload = [
        "uri" => $path,
        "nonce" => $nonce,
        "iat" => $iat,
        "exp" => $exp,
        "sub" => $sub,
        "bodyHash" => $bodyHash
    ];

    $token = JWT::encode($payload, $privateKey, 'RS256');
    return $token;
}

// Create a JWT token
$pathGet = '/v1/vault/accounts_paged';
$tokenGet = generateToken($privateKey, $apiKey, $pathGet);

// Make a GET request
$client = new Client();
$headersGet = [
    'Authorization' => 'Bearer ' . $tokenGet,
    'X-API-Key' => $apiKey,
    'Content-Type' => 'application/json'
];

try {
    $responseGet = $client->get($baseUrl . $pathGet, ['headers' => $headersGet]);
    echo "GET Request Status Code: " . $responseGet->getStatusCode() . "\n";
    echo "GET Response Body:\n" . $responseGet->getBody() . "\n";
} catch (RequestException $e) {
    echo "GET Request Failed: " . $e->getResponse()->getStatusCode() . "\n";
    echo "GET Response Body:\n" . $e->getResponse()->getBody() . "\n";
}

// Create a JWT token for POST
$pathPost = '/v1/vault/accounts';
$bodyPost = [
    "name" => "MyPHPVault",
    "hiddenOnUI" => true
];
$tokenPost = generateToken($privateKey, $apiKey, $pathPost, $bodyPost);

// Make a POST request
$headersPost = [
    'Authorization' => 'Bearer ' . $tokenPost,
    'X-API-Key' => $apiKey,
    'Content-Type' => 'application/json'
];

try {
    $responsePost = $client->post($baseUrl . $pathPost, ['headers' => $headersPost, 'json' => $bodyPost]);
    echo "POST Request Status Code: " . $responsePost->getStatusCode() . "\n";
    echo "POST Response Body:\n" . $responsePost->getBody() . "\n";
} catch (RequestException $e) {
    echo "POST Request Failed: " . $e->getResponse()->getStatusCode() . "\n";
    echo "POST Response Body:\n" . $e->getResponse()->getBody() . "\n";
}
