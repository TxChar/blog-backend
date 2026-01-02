"""
Script to generate RSA key pair for JWE token encryption
Run this script once to generate keys and save them to keys/ folder
"""

from jwcrypto import jwk
from pathlib import Path


def generate_rsa_keys():
    """Generate RSA 2048-bit key pair and save to files"""
    # Generate RSA key
    key = jwk.JWK.generate(kty='RSA', size=2048)

    # Export public key (PEM format)
    public_pem = key.export_to_pem()

    # Export private key (PEM format)
    private_pem = key.export_to_pem(private_key=True, password=None)

    # Create keys directory
    base_dir = Path(__file__).parent.parent
    keys_dir = base_dir / "keys"
    keys_dir.mkdir(exist_ok=True)

    # Save keys to files
    private_key_path = keys_dir / "private_key.pem"
    public_key_path = keys_dir / "public_key.pem"

    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)

    # Print success message
    print("=" * 80)
    print("✅ RSA Keys Generated Successfully!")
    print("=" * 80)
    print(f"\n📁 Keys saved to:")
    print(f"   - {private_key_path}")
    print(f"   - {public_key_path}")
    print("\n" + "=" * 80)
    print("⚠️  IMPORTANT: Keep private_key.pem secure and never commit to git!")
    print("   Add 'keys/' to .gitignore")


if __name__ == "__main__":
    generate_rsa_keys()
