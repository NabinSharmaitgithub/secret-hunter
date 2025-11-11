import sys

def confirm_authorization(force_confirmation=False):
    """
    Presents an authorization checklist and requires user confirmation.
    The tool will exit if authorization is not confirmed.
    """
    if not force_confirmation:
        print("Skipping authorization check. Use --confirm-authorization to enable.")
        return

    print("-" * 80)
    print("IMPORTANT: AUTHORIZATION REQUIRED")
    print("-" * 80)
    print("You are about to run a security analysis tool. Please confirm the following:")
    print("\n")
    print("[ ] I have WRITTEN PERMISSION from the owner of the target system to perform this analysis.")
    print("[ ] I will ONLY use this tool for lawful, authorized security assessments.")
    print("[ ] I understand that unauthorized scanning is illegal and unethical.")
    print("[ ] I will NOT use this tool to bypass DRM, authentication, or other protections.")
    print("\n")

    try:
        response = input('Type "I AUTHORIZE" to continue: ')
        if response.strip() == "I AUTHORIZE":
            print("Authorization confirmed. Proceeding with analysis.")
        else:
            print("Authorization not confirmed. Exiting.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nAuthorization cancelled by user. Exiting.")
        sys.exit(1)

def confirm_license(license_text, force_confirmation=False):
    """
    Presents the license (if found) and requires user confirmation.
    Handles cases where a license file is not found.
    """
    if not force_confirmation:
        return

    print("-" * 80)
    if license_text:
        print("LICENSE AGREEMENT")
        print("-" * 80)
        print("The target software is licensed under the following terms:")
        print("\n")
        print(license_text)
        print("\n")
    else:
        print("WARNING: NO LICENSE FILE FOUND")
        print("-" * 80)
        print("The tool could not automatically find a LICENSE file for the remote source.")
        print("It is your responsibility to ensure you are authorized to analyze this code.")
        print("\n")

    prompt_text = 'Type "I AUTHORIZE AND LICENSE OK" to continue: '
    expected_response = "I AUTHORIZE AND LICENSE OK"

    try:
        response = input(prompt_text)
        if response.strip() == expected_response:
            print("License confirmation received. Proceeding with analysis.")
        else:
            print("License confirmation not provided. Exiting.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nAuthorization cancelled by user. Exiting.")
        sys.exit(1)
