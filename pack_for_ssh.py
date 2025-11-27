import zipfile
import os

def zip_project():
    zip_name = "WOS_Bot_Deploy.zip"
    files_to_include = [
        "main.py",
        "requirements.txt",
        "permission_manager.py",
        "i18n_manager.py",
        "check_managers.py",
        "add_interaction_logging.py",
        "bot_config.env.example",
        "README.md",
        "PERMISSION_SYSTEM.md",
        "setup_systemd.sh",
        "deploy_check.sh"
    ]
    dirs_to_include = [
        "cogs",
        "i18n",
        "fonts",
        "models",
        "docker",
        "migrations"
    ]

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Write individual files
        for file in files_to_include:
            if os.path.exists(file):
                print(f"Adding {file}")
                zf.write(file)
            else:
                print(f"Warning: {file} not found")
        
        # Write directories
        for directory in dirs_to_include:
            if not os.path.exists(directory):
                print(f"Warning: Directory {directory} not found")
                continue
                
            for root, dirs, files in os.walk(directory):
                # Exclude __pycache__
                if "__pycache__" in root.split(os.sep):
                    continue
                
                for file in files:
                    if file.endswith(".pyc") or file.endswith(".pyo") or file == ".DS_Store":
                        continue
                    
                    file_path = os.path.join(root, file)
                    print(f"Adding {file_path}")
                    zf.write(file_path)
    
    print(f"\n✅ Successfully created {zip_name}")

if __name__ == "__main__":
    zip_project()




