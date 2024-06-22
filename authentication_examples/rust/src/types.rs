use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct VaultAccountPaginatedResponse {
    accounts: Vec<VaultAccountResponse>,
    paging: Paging,
    previous_url: Option<String>,
    next_url: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct VaultAccountResponse {
    id: String,
    name: String,
    #[serde(rename = "hiddenOnUI")]
    hidden_on_ui: bool,
    assets: Vec<AssetResponse>,
    customer_ref_id: Option<String>,
    auto_fuel: bool,
}

#[derive(Debug, serde::Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PagedVaultAccountsResponse {
    accounts: Vec<VaultAccountResponse>,
    paging: Option<Paging>,
    previous_url: Option<String>,
    next_url: Option<String>,
}
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Paging {
    before: Option<String>,
    after: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreateVaultRequest {
    pub name: String,
    #[serde(rename = "hiddenOnUI")]
    pub hidden_on_ui: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub customer_ref_id: Option<String>,
    #[serde(rename = "autoFuel")]
    pub auto_fuel: bool,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreateVaultResponse {
    pub id: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AssetTypeResponse {
    id: String,
    name: String,
    #[serde(rename = "type")]
    kind: String,
    #[serde(rename = "contractAddress")]
    contract_address: String,
    #[serde(rename = "nativeAsset")]
    native_asset: String,
    decimals: Option<i64>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AssetResponse {
    id: String,
    total: String,
    /// DEPRECATED
    balance: Option<String>,
    #[serde(rename = "lockedAmount")]
    locked_amount: Option<String>,
    available: Option<String>,
    pending: Option<String>,
    self_staked_cpu: Option<String>,
    self_staked_network: Option<String>,
    pending_refund_cpu: Option<String>,
    pending_refund_network: Option<String>,
    total_staked_cpu: Option<String>,
    total_staked_network: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AssetWalletsResponse {
    #[serde(rename = "vaultId")]
    pub vault_id: String,
    #[serde(rename = "assetId")]
    pub asset_id: String,
    pub total: String,
    pub available: String,
    pub pending: String,
    pub staked: String,
    pub frozen: String,
    #[serde(rename = "lockedAmount")]
    pub locked_amount: String,
    #[serde(rename = "blockHeight")]
    pub block_height: String,
    #[serde(rename = "blockHash")]
    pub block_hash: String,
    #[serde(rename = "creationTime")]
    pub creation_time: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnspentInputsResponse {
    pub address: String,
    pub input: Input,
    pub amount: String,
    pub confirmations: String,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Input {
    #[serde(rename = "txHash")]
    pub tx_hash: String,
    pub number: i64,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GetAssetWalletsResponse {
    #[serde(rename = "assetWallets")]
    pub asset_wallets: Vec<AssetWalletsResponse>,
    pub paging: Paging,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DepositAddressResponse {
    #[serde(rename = "assetId")]
    pub asset_id: String,
    pub address: String,
    pub tag: Option<String>,
    pub description: Option<String>,
    #[serde(rename = "type")]
    pub kind: String,
    #[serde(rename = "legacyAddress")]
    pub legacy_address: Option<String>,
    #[serde(rename = "customerRefId")]
    pub customer_ref_id: Option<String>,
    #[serde(rename = "addressFormat")]
    pub address_format: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TransactionArguments {
    #[serde(rename = "assetId")]
    pub asset_id: String,
    pub operation: TransactionOperation,
    pub source: TransferPeerPath,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub destination: Option<DestinationTransferPeerPath>,
    pub amount: String,
    //pub extra_parameters: Option<ExtraParameters>,
    //#[serde(skip_serializing_if = "Option::is_none")]
    //pub gas_price: Option<String>,
    //#[serde(skip_serializing_if = "Option::is_none")]
    //pub gas_limit: Option<String>,
    pub note: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub enum ExtraParameters {
    ContractCallData(String),
    RawMessageData(RawMessageData),
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TransferPeerPath {
    #[serde(rename = "type")]
    pub peer_type: PeerType,
    pub id: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DestinationTransferPeerPath {
    #[serde(rename = "type")]
    pub peer_type: PeerType,
    //  #[serde(skip_serializing_if = "Option::is_none")]
    pub id: String,
    //  #[serde(skip_serializing_if = "Option::is_none")]
    //  pub one_time_address: Option<OneTimeAddress>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OneTimeAddress {
    pub address: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tag: Option<String>,
}

#[allow(non_camel_case_types)]
#[derive(Debug, Serialize, Deserialize)]
#[allow(clippy::upper_case_acronyms)]
pub enum TransactionOperation {
    TRANSFER,
    RAW,
    CONTRACT_CALL,

    MINT,
    BURN,
    SUPPLY_TO_COMPOUND,
    REDEEM_FROM_COMPOUND,
}

#[allow(non_camel_case_types)]
#[derive(Debug, Serialize, Deserialize)]
#[allow(clippy::upper_case_acronyms)]
pub enum PeerType {
    VAULT_ACCOUNT,
    EXCHANGE_ACCOUNT,
    INTERNAL_WALLET,
    EXTERNAL_WALLET,
    ONE_TIME_ADDRESS,
    NETWORK_CONNECTION,
    FIAT_ACCOUNT,
    COMPOUND,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreateTransactionResponse {
    pub id: String,
    pub status: TransactionStatus,
}

#[allow(non_camel_case_types)]
#[allow(clippy::upper_case_acronyms)]
#[derive(Debug, Serialize, Deserialize)]
pub enum TransactionStatus {
    SUBMITTED,
    QUEUED,
    PENDING_SIGNATURE,
    PENDING_AUTHORIZATION,
    PENDING_3RD_PARTY_MANUAL_APPROVAL,
    PENDING_3RD_PARTY,
    PENDING,
    BROADCASTING,
    CONFIRMING,
    CONFIRMED,
    COMPLETED,
    PENDING_AML_SCREENING,
    PARTIALLY_COMPLETED,
    CANCELLING,
    CANCELLED,
    REJECTED,
    FAILED,
    TIMEOUT,
    BLOCKED,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TransactionDetails {
    pub id: String,
    pub asset_id: String,

    pub tx_hash: String,
    pub status: TransactionStatus,
    pub sub_status: String,

    pub signed_messages: Vec<SignedMessageResponse>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SignedMessageResponse {
    content: String,
    algorithm: String,
    derivation_path: Vec<usize>,
    pub signature: SignatureResponse,
    public_key: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SignatureResponse {
    pub full_sig: String,
    pub r: String,
    pub s: String,
    pub v: u64,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RawMessageData {
    pub messages: Vec<UnsignedMessage>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsignedMessage {
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RequestOptions {
    #[serde(rename = "idempotencyKey")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub idempotency_key: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ncw: Option<NCW>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NCW {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub wallet_id: Option<String>,
}
