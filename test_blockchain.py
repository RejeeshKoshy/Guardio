#!/usr/bin/env python3
"""
Test script to demonstrate the blockchain-inspired audit trail functionality.
This script shows how the tamper-evident audit system works.
"""

import hashlib
import json
from datetime import datetime

class TestAuditBlock:
    """Simplified version of the AuditBlock for testing"""
    
    def __init__(self, user_id, action, details, previous_block=None):
        self.user_id = user_id
        self.action = action
        self.details = json.dumps(details) if isinstance(details, dict) else str(details)
        self.previous_hash = previous_block.block_hash if previous_block else None
        self.timestamp = datetime.utcnow()
        self.nonce = 0
        self.block_hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = f"{self.user_id}{self.previous_hash}{self.timestamp.isoformat()}{self.action}{self.details}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty=2):
        """Simple proof-of-work mining"""
        target = "0" * difficulty
        while self.block_hash[:difficulty] != target:
            self.nonce += 1
            self.block_hash = self.calculate_hash()
    
    def is_valid(self, previous_block=None):
        """Validate the block's integrity"""
        if self.block_hash != self.calculate_hash():
            return False, "Invalid block hash"
        
        if previous_block and self.previous_hash != previous_block.block_hash:
            return False, "Previous hash mismatch"
        
        if not previous_block and self.previous_hash is not None:
            return False, "Genesis block should have null previous hash"
        
        return True, "Valid block"

def test_blockchain_audit_trail():
    """Test the blockchain audit trail functionality"""
    print("🔗 Testing Blockchain-Inspired Audit Trail")
    print("=" * 50)
    
    # Create a chain of audit blocks for a user
    user_id = 1
    blocks = []
    
    # Genesis block (user registration)
    print("1. Creating genesis block (user registration)...")
    genesis_block = TestAuditBlock(user_id, 'user_registration', {
        'username': 'testuser',
        'email': 'test@example.com',
        'role': 'user'
    })
    genesis_block.mine_block(difficulty=2)
    blocks.append(genesis_block)
    print(f"   ✅ Genesis block created: {genesis_block.block_hash[:16]}...")
    
    # File upload block
    print("2. Creating file upload block...")
    file_block = TestAuditBlock(user_id, 'file_upload', {
        'filename': 'document.pdf',
        'file_size': 1024000,
        'ai_analyzed': True
    }, blocks[-1])
    file_block.mine_block(difficulty=2)
    blocks.append(file_block)
    print(f"   ✅ File upload block created: {file_block.block_hash[:16]}...")
    
    # Password addition block
    print("3. Creating password addition block...")
    password_block = TestAuditBlock(user_id, 'password_add', {
        'website': 'example.com',
        'username': 'testuser',
        'password_length': 12
    }, blocks[-1])
    password_block.mine_block(difficulty=2)
    blocks.append(password_block)
    print(f"   ✅ Password block created: {password_block.block_hash[:16]}...")
    
    # Validate the chain
    print("\n4. Validating the audit chain...")
    previous_block = None
    chain_valid = True
    
    for i, block in enumerate(blocks):
        # For genesis block, previous_block should be None
        if block.action == "genesis_block":
            is_valid, message = block.is_valid(None)
        else:
            is_valid, message = block.is_valid(previous_block)
        print(f"   Block {i+1}: {'✅ Valid' if is_valid else '❌ Invalid'} - {message}")
        if not is_valid:
            chain_valid = False
        previous_block = block
    
    print(f"\n🔍 Chain validation result: {'✅ VALID' if chain_valid else '❌ TAMPERED'}")
    
    # Demonstrate tampering detection
    print("\n5. Demonstrating tamper detection...")
    print("   Modifying a block's data...")
    
    # Tamper with the file block
    original_hash = file_block.block_hash
    file_block.details = json.dumps({'filename': 'malicious.exe', 'file_size': 1024000, 'ai_analyzed': True})
    file_block.block_hash = file_block.calculate_hash()
    
    print(f"   Original hash: {original_hash[:16]}...")
    print(f"   New hash: {file_block.block_hash[:16]}...")
    
    # Validate the tampered chain
    print("\n6. Validating tampered chain...")
    previous_block = None
    tampered_chain_valid = True
    
    for i, block in enumerate(blocks):
        is_valid, message = block.is_valid(previous_block)
        print(f"   Block {i+1}: {'✅ Valid' if is_valid else '❌ Invalid'} - {message}")
        if not is_valid:
            tampered_chain_valid = False
        previous_block = block
    
    print(f"\n🚨 Tampered chain validation: {'✅ VALID' if tampered_chain_valid else '❌ TAMPERED'}")
    
    # Show the chain structure
    print("\n7. Audit Chain Structure:")
    print("   " + "=" * 40)
    for i, block in enumerate(blocks):
        print(f"   Block {i+1}: {block.action}")
        print(f"   ├─ Hash: {block.block_hash[:16]}...")
        print(f"   ├─ Previous: {block.previous_hash[:16] + '...' if block.previous_hash else 'Genesis'}")
        print(f"   ├─ Nonce: {block.nonce}")
        print(f"   └─ Details: {block.details[:50]}...")
        if i < len(blocks) - 1:
            print("   ⛓️")
    
    print("\n🎉 Blockchain audit trail test completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Cryptographic hashing (SHA-256)")
    print("✅ Immutable chain linking")
    print("✅ Proof-of-work mining")
    print("✅ Tamper detection")
    print("✅ Complete audit trail")

if __name__ == "__main__":
    test_blockchain_audit_trail()
