defmodule FireblocksSDKExample do
  @moduledoc """
  Fireblocks SDK Example in Elixir.
  """

  @api_key "API_KEY"
  @base_url "https://api.fireblocks.io"
  @api_secret_path "SECRET_KEY_PATH"

  def run do
    api_secret = read_private_key_file(@api_secret_path)

    client = %FireblocksHttpClient{
      api_key: @api_key,
      private_key: api_secret,
      base_url: @base_url
    }

    case FireblocksHttpClient.get(client, "/v1/vault/accounts_paged") do
      {:ok, get_vaults_response} -> IO.inspect(get_vaults_response)
      {:error, reason} -> IO.puts("Failed to fetch vaults: #{inspect(reason)}")
    end
  end

  defp read_private_key_file(path) do
    File.read!(path)
  end
end
