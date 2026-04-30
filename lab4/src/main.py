import subprocess


def main():
    print("CI/CD pipeline test")
    # Уязвимость для демонстрации работы Bandit (CWE-78)
    subprocess.run("echo 'Security test'", shell=True)


if __name__ == "__main__":
    main()
