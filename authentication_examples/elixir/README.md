## Fireblocks SDK Example Application

This is a simple Elixir application demonstrating how to interact with the Fireblocks API. It shows how to authenticate using a private key and make HTTP requests to the Fireblocks API to retrieve vault accounts.

### Prerequisites

Before running this example, ensure you have the following prerequisites:

- **Elixir installed:** If you don't have Elixir installed, follow the official installation guide.
- **Fireblocks API credentials:**
    - **API Key:** You'll need an API key from Fireblocks.
    - **Private Key:** You need a `.pem` file containing your private key that is associated with your Fireblocks API key.

### Required dependencies:

The application uses the following dependencies:

- `httpoison` for making HTTP requests.
- `jason` for parsing JSON.
- `jose` for handling JWT token creation.

### Setup

1. **Clone the repository:**

    ```bash
    cd developers-hub/authentication_examples/elixir
    ```

2. Then run the following command to install the dependencies:

    ```bash
    mix deps.get
    ```

3. **Save your private key:**

   Place your Fireblocks private key (in PEM format) in the location specified in the `@api_secret_path` in the code. The file should be similar to:

    ```vbnet
    -----BEGIN PRIVATE KEY-----
    YOUR_PRIVATE_KEY_HERE
    -----END PRIVATE KEY-----
    ```

4. **Edit the API Key and Secret Path:**

   In the `fireblocks_sdk_example.ex` file, ensure that your API key and the path to your private key are correctly set:

    ```elixir
    @api_key "YOUR_API_KEY"
    @api_secret_path "/path/to/your/private_key.pem"
    ```

### Running the Application

Once everything is set up, you can run the application using the Elixir interactive shell:

1. Start the interactive shell:

    ```bash
    iex -S mix
    ```

2. **Run the example:**

   In the interactive shell, run the following command to make the request to Fireblocks:

    ```elixir
    Elixir.FireblocksSDKExample.run()
    ```

3. **Output:** If successful, the response from the Fireblocks API (vaults information) will be printed. If there is an error (e.g., an issue with authentication or network), an error message will be shown.

### Example Output

**Successful request:**

```elixir
%{"accounts" => [%{"assets" => [...]}] }
