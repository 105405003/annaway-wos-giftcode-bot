import subprocess
import sys
import os
import shutil
import stat

def is_container() -> bool:
    return os.path.exists("/.dockerenv") or os.path.exists("/var/run/secrets/kubernetes.io")

def is_ci_environment() -> bool:
    """Check if running in a CI environment"""
    ci_indicators = [
        'CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS', 
        'JENKINS_URL', 'TRAVIS', 'CIRCLECI', 'GITLAB_CI'
    ]
    return any(os.getenv(indicator) for indicator in ci_indicators)

def should_skip_venv() -> bool:
    """Check if venv should be skipped"""
    return '--no-venv' in sys.argv or is_container() or is_ci_environment()

# Handle venv setup
if sys.prefix == sys.base_prefix and not should_skip_venv():
    print("Running the bot in a venv (virtual environment) to avoid dependency conflicts.")
    print("Note: You can skip venv creation with the --no-venv argument if needed.")
    venv_path = "bot_venv"

    # Determine the python executable path in the venv
    if sys.platform == "win32":
        venv_python_name = os.path.join(venv_path, "Scripts", "python.exe")
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
    else:
        venv_python_name = os.path.join(venv_path, "bin", "python")
        activate_script = os.path.join(venv_path, "bin", "activate")

    if not os.path.exists(venv_path):
        try:
            print("Attempting to create virtual environment automatically...")
            subprocess.check_call([sys.executable, "-m", "venv", venv_path], timeout=300)
            print(f"Virtual environment created at {venv_path}")

            if sys.platform == "win32":
                print("\nVirtual environment created.")
                print("To continue, please run the script again with the venv Python:")
                print(f"  1. Ensure CMD or PowerShell is open in this directory: {os.getcwd()}")
                print(f"  2. Run this exact command: {venv_python_name} {os.path.basename(sys.argv[0])}")
                sys.exit(0)
            else: # For non-Windows, try to relaunch automatically
                print("Restarting script in virtual environment...")
                venv_python_executable = os.path.join(venv_path, "bin", "python")
                os.execv(venv_python_executable, [venv_python_executable] + sys.argv)

        except Exception as e:
            print("Failed to create virtual environment automatically.")
            print(f"Error: {e}")
            print("Please create one manually with: python -m venv bot_venv")
            print("Then activate it and run this script again.")
            print("See also: https://docs.python.org/3/library/venv.html#how-venvs-work")
            sys.exit(1)
    else: # Venv exists
        if sys.platform == "win32":
            print(f"Virtual environment at {venv_path} exists.")
            print("To ensure you are using it, please run the script with the venv Python:")
            print(f"  1. Ensure CMD or PowerShell is open in this directory: {os.getcwd()}")
            print(f"  2. Run this exact command: {venv_python_name} {os.path.basename(sys.argv[0])}")
            sys.exit(0)
        elif '--no-venv' in sys.argv:
            print("Virtual environment setup skipped due to --no-venv flag.")
            print("Warning: Dependencies will be installed system-wide which may cause conflicts.")
        else: # For non-Windows, if venv exists but we're not in it, try to relaunch
            venv_python_executable = os.path.join(venv_path, "bin", "python")
            if os.path.exists(venv_python_executable):
                print(f"Using existing virtual environment at {venv_path}. Restarting...")
                os.execv(venv_python_executable, [venv_python_executable] + sys.argv)
            else:
                print(f"Virtual environment at {venv_path} appears corrupted.")
                print("Please remove it and run the script again, or create a new one manually.")
                sys.exit(1)

try: # Import or install requests so we can get the requirements
    import requests
except ImportError:
    print("Installing requests (required for dependency management)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], 
                            timeout=300, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import requests
    except Exception as e:
        print(f"Failed to install requests: {e}")
        print("Please install requests manually: pip install requests")
        sys.exit(1)

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_remove(path, is_dir=None):
    """
    Safely remove a file or directory.
    Clear the read-only bit on Windows.
    
    Args:
        path: Path to file or directory to remove
        is_dir: True for directory, False for file, None to auto-detect
        
    Returns:
        bool: True if successfully removed, False otherwise
    """
    if not os.path.exists(path):
        return True  # Already gone, consider it success
    
    if is_dir is None: # Auto-detect type if not specified
        is_dir = os.path.isdir(path)
    
    try:
        if is_dir:
            if sys.platform == "win32":
                shutil.rmtree(path, onexc=remove_readonly)
            else:
                shutil.rmtree(path)
        else:
            try:
                os.remove(path)
            except PermissionError:
                if sys.platform == "win32":
                    os.chmod(path, stat.S_IWRITE)
                    os.remove(path)
                else:
                    raise  # Re-raise on non-Windows platforms
        
        return True
        
    except PermissionError:
        print(f"Warning: Access Denied. Could not remove '{path}'.\nCheck permissions or if {'directory' if is_dir else 'file'} is in use.")
    except OSError as e:
        print(f"Warning: Could not remove '{path}': {e}")
    
    return False

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    import hashlib
    if not os.path.exists(filepath):
        return None
    
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def uninstall_packages(packages, reason=""):
    """Generic function to uninstall a list of packages"""
    if not packages:
        return
    
    print(F.YELLOW + f"Found {len(packages)} packages to remove{reason}: {', '.join(packages)}" + R)
    debug_mode = "--verbose" in sys.argv or "--debug" in sys.argv
    
    for package in packages:
        try:
            cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package]
            
            if debug_mode:
                subprocess.check_call(cmd, timeout=300)
            else:
                subprocess.check_call(cmd, timeout=300, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(F.GREEN + f"[V] Removed {package}" + R)
        except subprocess.CalledProcessError:
            print(F.YELLOW + f"[X] Could not remove {package} (might be needed by other packages)" + R)
        except Exception as e:
            print(F.YELLOW + f"[X] Error removing {package}: {e}" + R)

def get_packages_to_remove():
    """Get all packages that should be removed (from requirements comparison + legacy)"""
    packages_to_remove = set()
    
    # Check requirements.old vs requirements.txt (if they exist)
    if os.path.exists("requirements.old") and os.path.exists("requirements.txt"):
        try:
            old_packages = set()
            new_packages = set()
            
            # Parse old requirements
            with open("requirements.old", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
                        old_packages.add(pkg_name.strip().lower())
            
            # Parse new requirements
            with open("requirements.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
                        new_packages.add(pkg_name.strip().lower())
            
            packages_to_remove.update(old_packages - new_packages)
        except Exception as e:
            print(F.YELLOW + f"Error comparing requirements: {e}" + R)
    
    # Always check for legacy packages that are still installed
    for package in LEGACY_PACKAGES_TO_REMOVE:
        if is_package_installed(package):
            packages_to_remove.add(package.lower())
    
    return list(packages_to_remove)

def cleanup_removed_packages():
    """Main cleanup function - removes obsolete packages"""
    packages = get_packages_to_remove()
    
    if packages:
        reason = " from requirements" if os.path.exists("requirements.old") else " (legacy packages)"
        uninstall_packages(packages, reason)
    
    # Clean up requirements.old
    if os.path.exists("requirements.old"):
        safe_remove("requirements.old", is_dir=False)

# Potential leftovers from older bot versions
LEGACY_PACKAGES_TO_REMOVE = [
    "ddddocr",
    "easyocr", 
    "torch",
    "torchvision",
    "torchaudio",
    "opencv-python",
    "opencv-python-headless",
]

def has_obsolete_requirements():
    """
    Check if requirements.txt contains obsolete packages from older versions.
    Required to fix bug with v1.2.0 upgrade logic that deleted new requirements.txt.
    """
    if not os.path.exists("requirements.txt"):
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read().lower()
            
        for package in LEGACY_PACKAGES_TO_REMOVE:
            if package.lower() in content:
                return True
        
        return False
    except Exception as e:
        print(f"Error checking requirements.txt: {e}")
        return False

def is_package_installed(package_name):
    """Check if a package is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False


# 自動更新配置已移除

def check_and_install_requirements():
    """Check each requirement and install missing ones."""
    if not os.path.exists("requirements.txt"):
        print("No requirements.txt found")
        return False
        
    # Read requirements
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    print(f"Checking {len(requirements)} requirements...")
    
    missing_packages = []
    
    # Test each requirement
    for requirement in requirements:
        package_name = requirement.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
        
        try:
            if package_name == "discord.py":
                import discord
            elif package_name == "aiohttp-socks":
                import aiohttp_socks
            elif package_name == "python-dotenv":
                import dotenv
            elif package_name == "python-bidi":
                import bidi
            elif package_name == "arabic-reshaper":
                import arabic_reshaper
            elif package_name.lower() == "pillow":
                import PIL
            elif package_name.lower() == "numpy":
                import numpy
            elif package_name.lower() == "onnxruntime":
                import onnxruntime
            else:
                __import__(package_name)
                        
        except ImportError:
            print(f"[X] {package_name} - MISSING")
            missing_packages.append(requirement)
    
    if missing_packages: # Install missing packages
        print(f"Installing {len(missing_packages)} missing packages...")
        
        for package in missing_packages:
            try:
                cmd = [sys.executable, "-m", "pip", "install", package, "--no-cache-dir"]
                
                subprocess.check_call(cmd, timeout=1200, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[V] {package} installed successfully")
                
            except Exception as e:
                print(f"[X] Failed to install {package}: {e}")
                return False
    
    print("All requirements satisfied")
    return True

def setup_dependencies():
    """Main function to set up all dependencies."""
    print("\nChecking dependencies...")
    
    # 檢查是否存在過時的套件
    removed_obsolete = False
    if has_obsolete_requirements():
        print("! Warning: requirements.txt contains obsolete packages from older version")
        print("! Please update requirements.txt manually")
        removed_obsolete = True

    # 檢查 requirements.txt 是否存在
    if not os.path.exists("requirements.txt"):
        print("! Warning: requirements.txt not found")
        print("! Please ensure requirements.txt exists in the project directory")
        return False
    
    # 安裝缺少的套件
    if not check_and_install_requirements():
        print("[X] Failed to install requirements")
        return False
    
    return True

# 設定依賴
if not setup_dependencies():
    print("Warning: Dependency setup incomplete.")
    print("Please install manually with: pip install -r requirements.txt")

try:
    from colorama import Fore, Style, init
    import discord
    # 載入中文化管理器
    from i18n_manager import i18n, _
    # 載入權限管理器
    from permission_manager import permission_manager
    print("所有核心模組載入成功")
except ImportError as e:
    print(f"Import failed even after dependency setup: {e}")
    print("Please restart the script or install dependencies manually")
    sys.exit(1)

# Colorama shortcuts
F = Fore
R = Style.RESET_ALL

import warnings

def startup_cleanup():
    """Perform all cleanup tasks on startup - directories, files, and legacy packages."""
    v1_path = "V1oldbot"
    if os.path.exists(v1_path) and safe_remove(v1_path):
        print(f"Removed directory: {v1_path}")
    
    v2_path = "V2Old"
    if os.path.exists(v2_path) and safe_remove(v2_path):
        print(f"Removed directory: {v2_path}")
    
    pictures_path = "pictures"
    if os.path.exists(pictures_path) and safe_remove(pictures_path):
        print(f"Removed directory: {pictures_path}")
    
    txt_path = "autoupdateinfo.txt"
    if os.path.exists(txt_path) and safe_remove(txt_path):
        print(f"Removed file: {txt_path}")
    
    # Check for legacy packages to remove on startup
    legacy_packages = []
    for package in LEGACY_PACKAGES_TO_REMOVE:
        if is_package_installed(package):
            legacy_packages.append(package.lower())
    
    if legacy_packages:
        uninstall_packages(legacy_packages, " (legacy packages)")

startup_cleanup()

warnings.filterwarnings("ignore", category=DeprecationWarning)

init(autoreset=True)

try:
    import ssl
    import certifi

    def _create_ssl_context_with_certifi():
        return ssl.create_default_context(cafile=certifi.where())
    
    original_create_default_https_context = getattr(ssl, "_create_default_https_context", None)

    if original_create_default_https_context is None or \
       original_create_default_https_context is ssl.create_default_context:
        ssl._create_default_https_context = _create_ssl_context_with_certifi
        
        print(F.GREEN + "Applied SSL context patch using certifi for default HTTPS connections." + R)
    else: # Assume if it's already patched, it's for a good reason, just log it.
        print(F.YELLOW + "SSL default HTTPS context seems to be already modified. Skipping certifi patch." + R)
except ImportError:
    print(F.RED + "Certifi library not found. SSL certificate verification might fail until it's installed." + R)
except Exception as e:
    print(F.RED + f"Error applying SSL context patch: {e}" + R)

if __name__ == "__main__":
    import requests
    
    # 顯示啟動 Banner
    from utils.banner import print_startup_banner, __version__
    print_startup_banner(__version__)

    # 已移除自動更新功能，避免專案被意外覆蓋

    # 自動更新功能已移除
    import asyncio
    from datetime import datetime
            
    print(F.GREEN + "✅ 自動更新功能已停用，專案不會被意外覆蓋" + R)
            
    import discord
    from discord.ext import commands
    import sqlite3

    class CustomBot(commands.Bot):
        async def on_error(self, event_name, *args, **kwargs):
            if event_name == "on_interaction":
                error = sys.exc_info()[1]
                if isinstance(error, discord.NotFound) and error.code == 10062:
                    return
            
            await super().on_error(event_name, *args, **kwargs)

        async def on_command_error(self, ctx, error):
            if isinstance(error, discord.NotFound) and error.code == 10062:
                return
            await super().on_command_error(ctx, error)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True  # ✨ 必須啟用才能讀取成員角色（Manager 權限需要）

    bot = CustomBot(command_prefix="/", intents=intents, help_command=None)

    init(autoreset=True)

    # 優先從環境變量讀取 Token
    bot_token = os.getenv("BOT_TOKEN")
    
    # 強制設定期望語言為中文，確保不出現土耳其語錯誤
    language = os.getenv("LANGUAGE", "zh_TW")
    i18n.set_language(language)
    
    # 強制設定系統語言環境
    import locale
    import os
    
    # 設定環境變量強制中文
    os.environ["LC_ALL"] = "zh_TW.UTF-8"
    os.environ["LANG"] = "zh_TW.UTF-8"
    os.environ["LANGUAGE"] = "zh_TW.UTF-8"
    
    try:
        locale.setlocale(locale.LC_ALL, "zh_TW.utf8")
    except Exception:
        try:
            locale.setlocale(locale.LC_ALL, "chinese.utf8")
        except Exception:
            try:
                locale.setlocale(locale.LC_ALL, "C.UTF-8")
            except Exception:
                print("無法設定中文語言環境，但將繼續運行")
    
    # 如果環境變量中沒有，則嘗試從 bot_config.env 文件讀取
    if not bot_token:
        env_file = "bot_config.env"
        if os.path.exists(env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                bot_token = os.getenv("BOT_TOKEN")
            except ImportError:
                print("python-dotenv 未安裝，無法讀取 bot_config.env 文件")
                print("請運行: pip install python-dotenv")
    
    # 如果需要創建新的 token 文件
    if not bot_token:
        token_file = "bot_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                bot_token = f.read().strip()
        else:
            print("未找到 Discord Token！")
            print("請在 bot_config.env 文件中設置 BOT_TOKEN")
            sys.exit(1)

    if not os.path.exists("db"):
        os.makedirs("db")
        
        print(F.GREEN + "db folder created" + R)

    databases = {
        "conn_alliance": "db/alliance.sqlite",
        "conn_giftcode": "db/giftcode.sqlite",
        "conn_changes": "db/changes.sqlite",
        "conn_users": "db/users.sqlite",
        "conn_settings": "db/settings.sqlite",
    }

    connections = {name: sqlite3.connect(path) for name, path in databases.items()}

    print(F.GREEN + "Database connections have been successfully established." + R)

    def create_tables():
        with connections["conn_changes"] as conn_changes:
            conn_changes.execute("""CREATE TABLE IF NOT EXISTS nickname_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                fid INTEGER, 
                old_nickname TEXT, 
                new_nickname TEXT, 
                change_date TEXT
            )""")
            
            conn_changes.execute("""CREATE TABLE IF NOT EXISTS furnace_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                fid INTEGER, 
                old_furnace_lv INTEGER, 
                new_furnace_lv INTEGER, 
                change_date TEXT
            )""")

        with connections["conn_settings"] as conn_settings:
            conn_settings.execute("""CREATE TABLE IF NOT EXISTS botsettings (
                id INTEGER PRIMARY KEY, 
                channelid INTEGER, 
                giftcodestatus TEXT,
                global_gift_code_channel INTEGER
            )""")
            
            # 添加 global_gift_code_channel 欄位到現有表
            try:
                conn_settings.execute("ALTER TABLE botsettings ADD COLUMN global_gift_code_channel INTEGER")
            except sqlite3.OperationalError:
                # 欄位已存在
                pass
            
            conn_settings.execute("""CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY, 
                is_initial INTEGER
            )""")
            
            # 確保 botsettings 有預設記錄
            cursor_settings = conn_settings.cursor()
            cursor_settings.execute("SELECT COUNT(*) FROM botsettings WHERE id = 1")
            if cursor_settings.fetchone()[0] == 0:
                cursor_settings.execute("INSERT INTO botsettings (id) VALUES (1)")
                conn_settings.commit()
            cursor_settings.close()

        with connections["conn_users"] as conn_users:
            conn_users.execute("""CREATE TABLE IF NOT EXISTS users (
                fid INTEGER PRIMARY KEY, 
                nickname TEXT, 
                furnace_lv INTEGER DEFAULT 0, 
                kid INTEGER, 
                stove_lv_content TEXT, 
                alliance TEXT
            )""")

        with connections["conn_giftcode"] as conn_giftcode:
            conn_giftcode.execute("""CREATE TABLE IF NOT EXISTS gift_codes (
                giftcode TEXT PRIMARY KEY, 
                date TEXT
            )""")
            
            conn_giftcode.execute("""CREATE TABLE IF NOT EXISTS user_giftcodes (
                fid INTEGER, 
                giftcode TEXT, 
                status TEXT, 
                PRIMARY KEY (fid, giftcode),
                FOREIGN KEY (giftcode) REFERENCES gift_codes (giftcode)
            )""")

        with connections["conn_alliance"] as conn_alliance:
            conn_alliance.execute("""CREATE TABLE IF NOT EXISTS alliancesettings (
                alliance_id INTEGER PRIMARY KEY, 
                channel_id INTEGER, 
                interval INTEGER
            )""")
            
            conn_alliance.execute("""CREATE TABLE IF NOT EXISTS alliance_list (
                alliance_id INTEGER PRIMARY KEY, 
                name TEXT
            )""")

        print(F.GREEN + "All tables checked." + R)

    create_tables()

    async def load_cogs():
        cogs = ["olddb", "control", "alliance", "alliance_member_operations", "logsystem", "support_operations", "gift_operations", "changes", "w", "wel", "other_features", "backup_operations", "statistics", "permission_management"]
        
        failed_cogs = []
        
        for cog in cogs:
            try:
                await bot.load_extension(f"cogs.{cog}")
                print(f"[OK] Successfully loaded cog: {cog}")
            except Exception as e:
                print(f"[X] Failed to load cog {cog}: {e}")
                failed_cogs.append(cog)
        
        if failed_cogs:
            print(F.RED + f"\n[W] {len(failed_cogs)} cog(s) failed to load:" + R)
            for cog in failed_cogs:
                print(F.YELLOW + f"   - {cog}" + R)
            print(F.YELLOW + "\nThe bot will continue with reduced functionality." + R)
            print(F.YELLOW + "To fix missing or corrupted files, run: " + F.GREEN + "python main.py --repair" + R)
            print(F.YELLOW + "This will download and restore all files from the latest release.\n" + R)

    @bot.event
    async def on_ready():
        try:
            print(f"{F.GREEN}Logged in as {F.CYAN}{bot.user}{R}")
            
            # 同步命令
            synced = await bot.tree.sync()
            
            # 顯示同步的命令
            print(f"Commands synced: {len(synced)}")
            print("Synced commands:")
            for cmd in synced:
                print(f"  - /{cmd.name}: \"{cmd.description}\"")
            
            # 確保 botsettings 有記錄
            conn_settings = connections["conn_settings"]
            c_settings = conn_settings.cursor()
            c_settings.execute("SELECT COUNT(*) FROM botsettings WHERE id = 1")
            if c_settings.fetchone()[0] == 0:
                c_settings.execute("INSERT INTO botsettings (id) VALUES (1)")
                conn_settings.commit()
            c_settings.close()
                
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def main():
        await load_cogs()
        
        await bot.start(bot_token)

    if __name__ == "__main__":
        asyncio.run(main())