// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title HealthCredX Credential Contract
 * @dev Smart contract for issuing and verifying healthcare professional credentials
 * @notice This contract is designed for demonstration purposes in the HealthCredX platform
 */
contract HealthCredential {
    
    // Struct to store credential information
    struct Credential {
        address holder;           // Wallet address of the credential holder
        string name;             // Full name of the healthcare professional
        string skill;            // Type of certification (e.g., "Certified Phlebotomist")
        uint256 timestamp;       // Time when credential was issued
        bool verified;           // Verification status
        address issuer;          // Address of the issuing authority
    }
    
    // Mapping from credential ID to Credential struct
    mapping(bytes32 => Credential) public credentials;
    
    // Mapping from holder address to their credential IDs
    mapping(address => bytes32[]) public holderCredentials;
    
    // List of authorized issuers
    mapping(address => bool) public authorizedIssuers;
    
    // Contract owner
    address public owner;
    
    // Events
    event CredentialIssued(
        bytes32 indexed credentialId,
        address indexed holder,
        string skill,
        uint256 timestamp
    );
    
    event CredentialVerified(
        bytes32 indexed credentialId,
        address indexed verifier
    );
    
    event IssuerAuthorized(address indexed issuer);
    event IssuerRevoked(address indexed issuer);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender], "Only authorized issuers can call this function");
        _;
    }
    
    /**
     * @dev Constructor - sets the contract deployer as owner and authorized issuer
     */
    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
    }
    
    /**
     * @dev Issue a new credential to a healthcare professional
     * @param _holder Address of the credential holder
     * @param _name Full name of the holder
     * @param _skill Type of certification
     * @return credentialId Unique identifier for the credential
     */
    function issueCredential(
        address _holder,
        string memory _name,
        string memory _skill
    ) public onlyAuthorizedIssuer returns (bytes32) {
        require(_holder != address(0), "Invalid holder address");
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_skill).length > 0, "Skill cannot be empty");
        
        // Generate unique credential ID
        bytes32 credentialId = keccak256(
            abi.encodePacked(
                _holder,
                _name,
                _skill,
                block.timestamp,
                msg.sender
            )
        );
        
        // Create credential
        credentials[credentialId] = Credential({
            holder: _holder,
            name: _name,
            skill: _skill,
            timestamp: block.timestamp,
            verified: true,
            issuer: msg.sender
        });
        
        // Add to holder's credential list
        holderCredentials[_holder].push(credentialId);
        
        // Emit event
        emit CredentialIssued(credentialId, _holder, _skill, block.timestamp);
        
        return credentialId;
    }
    
    /**
     * @dev Verify that a credential exists and is valid
     * @param _credentialId The unique identifier of the credential
     * @return bool True if credential exists and is verified
     */
    function verifyCredential(bytes32 _credentialId) public returns (bool) {
        Credential memory cred = credentials[_credentialId];
        
        require(cred.holder != address(0), "Credential does not exist");
        require(cred.verified, "Credential is not verified");
        
        emit CredentialVerified(_credentialId, msg.sender);
        
        return true;
    }
    
    /**
     * @dev Get credential details
     * @param _credentialId The unique identifier of the credential
     * @return Credential struct with all details
     */
    function getCredential(bytes32 _credentialId) public view returns (
        address holder,
        string memory name,
        string memory skill,
        uint256 timestamp,
        bool verified,
        address issuer
    ) {
        Credential memory cred = credentials[_credentialId];
        require(cred.holder != address(0), "Credential does not exist");
        
        return (
            cred.holder,
            cred.name,
            cred.skill,
            cred.timestamp,
            cred.verified,
            cred.issuer
        );
    }
    
    /**
     * @dev Get all credentials for a specific holder
     * @param _holder Address of the credential holder
     * @return Array of credential IDs
     */
    function getHolderCredentials(address _holder) public view returns (bytes32[] memory) {
        return holderCredentials[_holder];
    }
    
    /**
     * @dev Authorize a new issuer
     * @param _issuer Address of the new issuer
     */
    function authorizeIssuer(address _issuer) public onlyOwner {
        require(_issuer != address(0), "Invalid issuer address");
        authorizedIssuers[_issuer] = true;
        emit IssuerAuthorized(_issuer);
    }
    
    /**
     * @dev Revoke an issuer's authorization
     * @param _issuer Address of the issuer to revoke
     */
    function revokeIssuer(address _issuer) public onlyOwner {
        authorizedIssuers[_issuer] = false;
        emit IssuerRevoked(_issuer);
    }
    
    /**
     * @dev Check if an address is an authorized issuer
     * @param _issuer Address to check
     * @return bool True if authorized
     */
    function isAuthorizedIssuer(address _issuer) public view returns (bool) {
        return authorizedIssuers[_issuer];
    }
}
