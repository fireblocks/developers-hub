defmodule FireblocksHttpClient do
  @moduledoc """
  Fireblocks HTTP Client for interacting with the Fireblocks API.
  """

  defstruct [:api_key, :private_key, :base_url]

  require Logger
  alias Joken
  alias HTTPoison

  @headers [
    {"Content-Type", "application/json; charset=utf-8"}
  ]

  def request(client, method, path, data \\ nil) do
    url = build_url(client.base_url, path)
    jwt = sign_jwt(client, path, if(data, do: Jason.encode!(data), else: ""))

    headers = build_headers(client.api_key, jwt)

    case method do
      :get -> HTTPoison.get(url, headers)
      :post -> HTTPoison.post(url, Jason.encode!(data), headers)
    end
    |> handle_response()
  end

  def get(client, path), do: request(client, :get, path)

  def post(client, path, data), do: request(client, :post, path, data)

  defp build_url(base_url, path), do: "#{base_url}#{path}"

  defp build_headers(api_key, jwt) do
    [
      {"X-API-Key", api_key},
      {"Authorization", "Bearer " <> jwt} | @headers
    ]
  end

  defp sign_jwt(client, path, body) do
    body_hash = hash_body(body)

    claims = %{
      "sub" => client.api_key,
      "iat" => DateTime.utc_now() |> DateTime.to_unix(),
      "exp" => DateTime.utc_now() |> DateTime.add(55) |> DateTime.to_unix(),
      "nonce" => UUID.uuid4(),
      "uri" => path,
      "bodyHash" => body_hash
    }

    jwk = JOSE.JWK.from_pem(client.private_key)

    {_, signed_token} =
      jwk
      |> JOSE.JWT.sign(%{"alg" => "RS256"}, claims)
      |> JOSE.JWS.compact()

    signed_token
  end

  defp hash_body(body) do
    :crypto.hash(:sha256, body)
    |> Base.encode16(case: :lower)
  end

  defp handle_response({:ok, %HTTPoison.Response{body: body}}), do: {:ok, Jason.decode!(body)}

  defp handle_response({:error, %HTTPoison.Error{reason: reason}}) do
    Logger.error("HTTP request failed: #{inspect(reason)}")
    {:error, reason}
  end
end
