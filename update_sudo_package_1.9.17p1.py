import paramiko
from scp import SCPClient
import csv
from concurrent.futures import ThreadPoolExecutor
import os
import urllib.request
import logging

# Настройка логирования
logging.basicConfig(filename='sudo_update.log', level=logging.DEBUG)

CSV_FILE = "hosts.csv"
LOCAL_DEB_FOR_DEB10 = './sudo_1.9.17p1-1_amd64.deb'
SSH_USER = 'your-ssh-user'

download_links = {
    'debian11': 'https://github.com/sudo-project/sudo/releases/download/v1.9.17p1/sudo_1.9.17-2_deb11_amd64.deb',
    'debian12': 'https://github.com/sudo-project/sudo/releases/download/v1.9.17p1/sudo_1.9.17-2_deb12_amd64.deb',
    'rocky9': 'https://github.com/sudo-project/sudo/releases/download/v1.9.17p1/sudo-1.9.17-2.el9.x86_64.rpm',
    'ubuntu2004': 'https://github.com/sudo-project/sudo/releases/download/v1.9.17p1/sudo_1.9.17-2_ubu2004_amd64.deb',
    'ubuntu2204': 'https://github.com/sudo-project/sudo/releases/download/v1.9.17p1/sudo_1.9.17-2_ubu2204_amd64.deb',
    'ubuntu2404': 'https://github.com/sudo-project/sudo/releases/download/v1.9.17p1/sudo_1.9.17-2_ubu2404_amd64.deb',
}

def get_os_version(ssh):
    stdin, stdout, stderr = ssh.exec_command('cat /etc/os-release')
    data = stdout.read().decode()
    if "Debian GNU/Linux 10" in data:
        return 'debian10'
    elif "Debian GNU/Linux 11" in data:
        return 'debian11'
    elif "Debian GNU/Linux 12" in data:
        return 'debian12'
    elif "Ubuntu 20.04" in data:
        return 'ubuntu2004'
    elif "Ubuntu 22.04" in data:
        return 'ubuntu2204'
    elif "Ubuntu 24.04" in data:
        return 'ubuntu2404'
    elif "Rocky Linux 9" in data:
        return 'rocky9'
    return None

def install_sudo(ssh, os_version):
    # Создаём резервную папку для /etc/sudoers.d
    cmd = 'sudo mkdir -p /tmp/sudoers.d.backup'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if err:
        print(f"[ERROR] {cmd}:\n{err}")
        logging.error(f"[ERROR] {cmd}:\n{err}")
        return False
    print(f"[OK] {cmd}:\n{out}")
    logging.debug(f"[OK] {cmd}:\n{out}")

    # Перемещаем файлы из /etc/sudoers.d
    cmd = 'sudo find /etc/sudoers.d -type f -exec mv {} /tmp/sudoers.d.backup/ \\;'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if err and 'warning' not in err.lower():
        print(f"[ERROR] {cmd}:\n{err}")
        logging.error(f"[ERROR] {cmd}:\n{err}")
        return False
    print(f"[OK] {cmd}:\n{out}")
    logging.debug(f"[OK] {cmd}:\n{out}")

    if os_version == 'debian10':
        if not os.path.exists(LOCAL_DEB_FOR_DEB10):
            print(f"[ERROR] Local .deb file {LOCAL_DEB_FOR_DEB10} not found")
            logging.error(f"[ERROR] Local .deb file {LOCAL_DEB_FOR_DEB10} not found")
            return False
        try:
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(LOCAL_DEB_FOR_DEB10, '/tmp/sudo_1.9.17p1-1_amd64.deb')
            print(f"[OK] Copied {LOCAL_DEB_FOR_DEB10} to /tmp/sudo_1.9.17p1-1_amd64.deb")
            logging.debug(f"[OK] Copied {LOCAL_DEB_FOR_DEB10} to /tmp/sudo_1.9.17p1-1_amd64.deb")
        except Exception as e:
            print(f"[ERROR] SCP failed: {e}")
            logging.error(f"[ERROR] SCP failed: {e}")
            return False

        commands = [
            'sudo DEBIAN_FRONTEND=noninteractive dpkg --force-confold -i /tmp/sudo_1.9.17p1-1_amd64.deb',
            'sudo apt-get install -f -y',
            'sudo rm /tmp/sudo_1.9.17p1-1_amd64.deb',
            'sudo dpkg -l sudo',
            'sudo mv /tmp/sudoers.d.backup/* /etc/sudoers.d/ || true'
        ]
    elif os_version in download_links:
        url = download_links[os_version]
        if os_version.startswith('rocky'):
            commands = [
                f'sudo yum --setopt=tsflags=noscripts --replacepkgs install -y {url}',
                'sudo rpm -q sudo',
                'sudo restorecon -v /usr/bin/sudo || true'
            ]
        else:
            try:
                urllib.request.urlopen(url, timeout=10)
                print(f"[OK] URL {url} is accessible")
                logging.debug(f"[OK] URL {url} is accessible")
            except Exception as e:
                print(f"[ERROR] URL {url} is not accessible: {e}")
                logging.error(f"[ERROR] URL {url} is not accessible: {e}")
                return False

            commands = [
                f'sudo wget --timeout=30 -O /tmp/sudo_package.deb {url}',
                'sudo DEBIAN_FRONTEND=noninteractive dpkg --force-confold -i /tmp/sudo_package.deb',
                'sudo apt-get install -f -y',
                'sudo rm /tmp/sudo_package.deb',
                'sudo dpkg -l sudo',
                'sudo mv /tmp/sudoers.d.backup/* /etc/sudoers.d/ || true'
            ]
    else:
        print(f"[ERROR] OS {os_version} not supported")
        logging.error(f"[ERROR] OS {os_version} not supported")
        return False

    for cmd in commands:
        print(f"[DEBUG] Executing: {cmd}")
        try:
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode()
            err = stderr.read().decode()
            if exit_status != 0 and '|| true' not in cmd:
                print(f"[ERROR] {cmd} (exit status {exit_status}):\n{err}\n{out}")
                logging.error(f"[ERROR] {cmd} (exit status {exit_status}):\n{err}\n{out}")
                return False
            print(f"[OK] {cmd}:\n{out}")
            logging.debug(f"[DEBUG] Executing: {cmd}\nExit status: {exit_status}\nOut: {out}\nErr: {err}")
        except Exception as e:
            print(f"[ERROR] Exception during {cmd}: {e}")
            logging.error(f"[ERROR] Exception during {cmd}: {e}")
            return False

    # Установка успешна, если все команды выполнены
    return True

def get_sudo_version(ssh):
    stdin, stdout, stderr = ssh.exec_command('sudo -V')
    output = stdout.read().decode()
    for line in output.splitlines():
        if line.lower().startswith("sudo version"):
            return line.strip().split()[-1]
    return None

def process_host(ip, hostname, username=SSH_USER, port=22, password=None, keyfile=None):
    print(f"Connecting to {ip} ({hostname}) as {username}")
    logging.info(f"Connecting to {ip} ({hostname}) as {username}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if keyfile:
            ssh.connect(ip, port=port, username=username, key_filename=keyfile, timeout=10)
        else:
            ssh.connect(ip, port=port, username=username, password=password, timeout=10)
    except Exception as e:
        print(f"[ERROR] Could not connect to {ip}: {e}")
        logging.error(f"[ERROR] Could not connect to {ip}: {e}")
        return

    try:
        current_version = get_sudo_version(ssh)
        print(f"{ip} current sudo version: {current_version or 'unknown'}")
        logging.info(f"{ip} current sudo version: {current_version or 'unknown'}")
        if current_version == "1.9.17p1":
            print(f"{ip} sudo is already up-to-date. Skipping update.")
            logging.info(f"{ip} sudo is already up-to-date. Skipping update.")
            return

        os_version = get_os_version(ssh)
        print(f"{ip} OS version detected as: {os_version}")
        logging.info(f"{ip} OS version detected as: {os_version}")

        if os_version:
            if install_sudo(ssh, os_version):
                print(f"{ip} sudo updated successfully")
                logging.info(f"{ip} sudo updated successfully")
            else:
                print(f"[ERROR] Installation failed on {ip}")
                logging.error(f"[ERROR] Installation failed on {ip}")
    finally:
        ssh.close()

def main():
    hosts = []
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hosts.append((row['IP address'], row['Hostname']))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for ip, hostname in hosts:
            futures.append(executor.submit(process_host, ip, hostname))

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] Exception in thread: {e}")
                logging.error(f"[ERROR] Exception in thread: {e}")

if __name__ == "__main__":
    main()
