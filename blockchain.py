"""
Mock Blockchain Implementation for HealthCredX
Simulates an immutable ledger for storing medical credentials
"""
import hashlib
import json
from datetime import datetime


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Credential data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Generate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self):
        """Convert block to dictionary for JSON serialization"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:
    """Mock blockchain for storing and verifying credentials"""
    
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, datetime.now().isoformat(), {
            "type": "genesis",
            "message": "HealthCredX Blockchain Initialized"
        }, "0")
        self.chain.append(genesis_block)
    
    def get_latest_block(self):
        """Return the most recent block"""
        return self.chain[-1]
    
    def add_credential(self, user_id, name, skill):
        """Add a new credential to the blockchain"""
        latest_block = self.get_latest_block()
        new_index = latest_block.index + 1
        timestamp = datetime.now().isoformat()
        
        credential_data = {
            "user_id": user_id,
            "name": name,
            "skill": skill,
            "verified": True,
            "issuer": "HealthCredX Platform"
        }
        
        new_block = Block(new_index, timestamp, credential_data, latest_block.hash)
        self.chain.append(new_block)
        
        return new_block.hash
    
    def add_medical_record(self, record_data):
        """Add a medical record hash to the blockchain"""
        latest_block = self.get_latest_block()
        new_index = latest_block.index + 1
        timestamp = datetime.now().isoformat()
        
        # Ensure required fields are present
        record_data["type"] = "medical_record"
        record_data["verified"] = True
        record_data["issuer"] = "HealthCredX Platform"
        
        new_block = Block(new_index, timestamp, record_data, latest_block.hash)
        self.chain.append(new_block)
        
        return new_block.hash
    
    def verify_credential(self, credential_hash):
        """Check if a credential exists on the blockchain"""
        for block in self.chain:
            if block.hash == credential_hash:
                return True, block.data
        return False, None
    
    def get_chain(self):
        """Return the entire blockchain as a list of dictionaries"""
        return [block.to_dict() for block in self.chain]
    
    def is_chain_valid(self):
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True


# Global blockchain instance
blockchain = Blockchain()
