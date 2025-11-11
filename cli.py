import argparse
from secret_hunter.auth_check import confirm_authorization
from secret_hunter.fetcher import fetch_source
from secret_hunter.scanner import scan_directory
from secret_hunter.remediation import generate_report

def main():
    parser = argparse.ArgumentParser(description="secret-hunter: A tool for finding exposed secrets in software packages.")
    parser.add_argument("--target", help="Path to the target file or directory.")
    parser.add_argument("--type", choices=["auto", "jar", "apk", "bin", "dir", "file"], default="auto", help="Type of the target.")
    parser.add_argument("--output", default="report.json", help="Path to the output report file.")
    parser.add_argument("--rules", default="rules.yml", help="Path to the rules file.")
    parser.add_argument("--whitelist", help="Path to the whitelist file.")
    parser.add_argument("--no-decompile", action="store_true", help="Only perform string extraction.")
    parser.add_argument("--confirm-authorization", action="store_true", help="Require explicit authorization before running.")
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum depth for directory scanning.")
    
    # Fetcher arguments
    fetch_group = parser.add_argument_group('Fetcher Options', 'Control how remote sources are fetched')
    fetch_group.add_argument("--fetch", action="store_true", help="Enable fetching from a remote source.")
    fetch_group.add_argument("--source-url", help="URL of the remote source to fetch.")
    fetch_group.add_argument("--source-type", choices=["auto", "git", "archive"], default="auto", help="Type of the remote source.")
    fetch_group.add_argument("--branch", help="Branch to checkout for git repositories.")
    fetch_group.add_argument("--tag", help="Tag to checkout for git repositories.")
    fetch_group.add_argument("--cache-dir", default=".cache", help="Directory to cache downloaded artifacts.")
    fetch_group.add_argument("--max-download-size", type=int, default=100, help="Maximum download size in MB.")
    fetch_group.add_argument("--timeout", type=int, default=60, help="Timeout for network operations in seconds.")
    fetch_group.add_argument("--verify-license", action="store_true", default=True, help="Verify the license of the remote source.")
    fetch_group.add_argument("--dry-run", action="store_true", help="Perform a dry run without downloading files.")
    fetch_group.add_argument("--verify-checksum", help="Expected SHA256 checksum of the downloaded archive.")


    args = parser.parse_args()

    confirm_authorization(args.confirm_authorization)

    target_path = None
    if args.fetch:
        if not args.source_url:
            parser.error("--source-url is required when --fetch is enabled.")
        
        target_path = fetch_source(args)
        
        if args.dry_run:
            print("Dry run complete.")
            return # Exit after dry run
            
    elif args.target:
        target_path = args.target
    else:
        parser.error("--target is required unless --fetch is enabled.")
    
    if target_path:
        findings = scan_directory(target_path, args.rules, args.whitelist, args.no_decompile, args.max_depth)
        generate_report(findings, args.output)
    else:
        print("No target to scan. Exiting.")


if __name__ == "__main__":
    main()
  
