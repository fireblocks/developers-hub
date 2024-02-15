package com.fireblocks.developers.example;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import java.util.Base64;
import okhttp3.*;
import org.json.JSONObject;
import java.util.concurrent.TimeUnit;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.*;
import java.security.interfaces.RSAKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Calendar;
import java.util.Date;
import java.util.Objects;
import java.util.UUID;
import java.util.stream.Stream;

public class FireblocksSDKExample {

    public FireblocksSDKExample() {
        StringBuilder secretBuilder = new StringBuilder();
        String API_SECRET_PATH = "SECRET_KEY_PATH";
        try (Stream<String> stream = Files.lines(Paths.get(API_SECRET_PATH), StandardCharsets.UTF_8)) {
            stream.forEach(s -> secretBuilder.append(s).append("\n"));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        String API_KEY = "API_KEY";
        String BASE_URL = "https://api.fireblocks.io"; // 

        FireblocksHttpClient httpClient = new FireblocksHttpClient(API_KEY, secretBuilder.toString(), BASE_URL);

        JSONObject getVaultsResponse = httpClient.get("/v1/vault/accounts_paged");
        System.out.println(getVaultsResponse.toString(4));

        JSONObject newVaultRequest = new JSONObject().put("name", "MyJavaVault").put("hiddenOnUI", true);
        JSONObject newVaultResponse = httpClient.post("/v1/vault/accounts", newVaultRequest);
        System.out.println(newVaultResponse.toString(4));

    }

    private static class FireblocksHttpClient {

        private String baseUrl = "https://api.fireblocks.io";
        private final String apiKey;

        private final PrivateKey privateKey;
        private final OkHttpClient client;

        public FireblocksHttpClient(String apiKey, String apiSecret) {
            this(apiKey, apiSecret, "https://api.fireblocks.io");
        }

        public FireblocksHttpClient(String apiKey, String apiSecret, String baseUrl) {
            Objects.requireNonNull(apiKey);
            Objects.requireNonNull(apiSecret);
            if (baseUrl != null && !this.baseUrl.equals(baseUrl)) {
                this.baseUrl = baseUrl;
            }
            this.apiKey = apiKey;
            this.client = new OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS) // Set connection timeout here
                    .build();
            try {
                // Use java.util.Base64 to decode the secret
                byte[] keyBytes = Base64.getDecoder().decode(apiSecret
                        .replace("-----BEGIN PRIVATE KEY-----", "")
                        .replace("-----END PRIVATE KEY-----", "")
                        .replace("\n", ""));
                PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
                KeyFactory factory = KeyFactory.getInstance("RSA");
                this.privateKey = factory.generatePrivate(keySpec);
            } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
                throw new RuntimeException(e);
            }
        }

        public JSONObject get(String path) {
            Request req = new Request.Builder()
                    .url(this.baseUrl + path)
                    .addHeader("X-API-Key", this.apiKey)
                    .addHeader("Authorization", "Bearer " + this.signJwt(path))
                    .build();
            try (Response resp = this.client.newCall(req).execute()) {
                ResponseBody body = resp.body();
                if (body == null) {
                    return new JSONObject();
                }
                return new JSONObject(body.string());
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

        public JSONObject post(String path, JSONObject data) {
            Request req = new Request.Builder()
                    .url(this.baseUrl + path)
                    .addHeader("X-API-Key", this.apiKey)
                    .addHeader("Authorization", "Bearer " + this.signJwt(path, data.toString()))
                    .post(RequestBody.create(data.toString().getBytes(), MediaType.parse("application/json; charset=utf-8")))
                    .build();
            try (Response resp = this.client.newCall(req).execute()) {
                ResponseBody body = resp.body();
                if (body == null) {
                    return new JSONObject();
                }
                return new JSONObject(body.string());
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

        private String signJwt(String path) {
            return this.signJwt(path, "");
        }

        private String signJwt(String path, String dataJSONString) {
            String bodyHash;
            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                digest.update(dataJSONString.getBytes());
                BigInteger number = new BigInteger(1, digest.digest());
                StringBuilder hexString = new StringBuilder(number.toString(16));
                while (hexString.length() < 64) {
                    hexString.insert(0, '0');
                }
                bodyHash = hexString.toString();
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException(e);
            }
            Algorithm algo = Algorithm.RSA256((RSAKey) this.privateKey);
            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.SECOND, 55);
            return JWT.create()
                    .withSubject(this.apiKey)
                    .withIssuedAt(new Date())
                    .withExpiresAt(cal.getTime())
                    .withClaim("nonce", UUID.randomUUID().toString())
                    .withClaim("uri", path)
                    .withClaim("bodyHash", bodyHash)
                    .sign(algo);
        }
    }

    public static void main(String[] args) {
        new FireblocksSDKExample();
    }
}
