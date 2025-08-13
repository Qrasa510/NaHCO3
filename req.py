import os
import ast
import pkgutil
import sys

# 要排除的目录
EXCLUDE_DIRS = {'.venv', 'venv', 'env', '__pycache__'}

# 内置模块列表
builtin_modules = set(sys.builtin_module_names)

# 所有已安装模块（防止把本地虚拟环境里的都算上）
installed_modules = {pkg.name for pkg in pkgutil.iter_modules()}

third_party = set()

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    third_party.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    third_party.add(node.module.split('.')[0])
    except Exception:
        pass

def scan_dir(directory):
    for root, dirs, files in os.walk(directory):
        # 排除虚拟环境目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith('.py'):
                scan_file(os.path.join(root, file))

if __name__ == '__main__':
    scan_dir('.')
    # 去掉内置模块
    third_party_cleaned = [m for m in third_party if m not in builtin_modules]
    print("找到的第三方库：", ", ".join(sorted(third_party_cleaned)))
    print("安装命令： pip install", " ".join(sorted(third_party_cleaned)))
