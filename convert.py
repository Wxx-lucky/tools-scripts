"""
文件格式转换工具
基于 MinerU CLI，支持 PDF→MD、图片→MD、XLSX→JSON、XLS→JSON、DOCX→MD、PPTX→MD
"""

import sys
import os
import subprocess
import shutil
import tempfile
from pathlib import Path

MINERU_EXE = r"D:\mineru-env\Scripts\mineru.exe"
PYTHON_EXE = r"D:\mineru-env\Scripts\python.exe"
MINERU_CONFIG = r"D:\mineru-env\mineru.json"

# 设置 MinerU 配置文件路径（避免在 C 盘 ~/mineru.json 下查找）
os.environ["MINERU_TOOLS_CONFIG_JSON"] = MINERU_CONFIG
# 强制使用本地模型，禁止从 HuggingFace/ModelScope 远程下载
os.environ["MINERU_MODEL_SOURCE"] = "local"

# MinerU 原生支持的格式
MINERU_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp", ".xlsx", ".docx", ".pptx"}

# 需要用 pandas 处理的格式
PANDAS_EXTENSIONS = {".xls"}

# 所有支持的格式
ALL_EXTENSIONS = MINERU_EXTENSIONS | PANDAS_EXTENSIONS

# 图片扩展名
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}


def get_file_path():
    """获取要转换的文件路径：命令行参数 > 手动输入"""
    if len(sys.argv) > 1:
        path = sys.argv[1].strip().strip('"')
        print(f"传入文件: {path}")
        return Path(path)
    path = input("请输入文件路径（可直接拖拽文件到此处）: ").strip().strip('"')
    return Path(path) if path else None


def validate_file(file_path: Path):
    """校验文件是否存在、格式是否支持"""
    if not file_path.exists():
        print(f"[错误] 文件不存在: {file_path}")
        return False
    ext = file_path.suffix.lower()
    if ext not in ALL_EXTENSIONS:
        print(f"[错误] 不支持的格式: {ext}")
        print(f"  支持的格式: {', '.join(sorted(ALL_EXTENSIONS))}")
        return False
    return True


def convert_with_mineru(file_path: Path):
    """使用 MinerU CLI 转换文件，只保留目标格式文件，清理附件"""
    ext = file_path.suffix.lower()

    # 确定目标格式
    if ext in (".xlsx",):
        target_ext = ".json"
    else:
        target_ext = ".md"

    # 输出到临时目录，方便提取单一文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 构建命令
        cmd = [MINERU_EXE, "-p", str(file_path), "-o", temp_dir, "-b", "pipeline"]

        if ext == ".pdf":
            cmd.extend(["-m", "auto"])
            cmd.extend(["-l", "ch"])

        print(f"\n正在转换: {file_path.name}")
        print(f"目标格式: {target_ext}")

        try:
            result = subprocess.run(cmd)
            if result.returncode != 0:
                print(f"\n[失败] MinerU 返回错误码: {result.returncode}")
                return

            # 在临时目录中查找生成的目标文件
            temp_path = Path(temp_dir)
            found = list(temp_path.rglob(f"*.{target_ext.lstrip('.')}"))
            if not found:
                print(f"\n[失败] 未在输出中找到 {target_ext} 文件")
                return

            target_file = found[0]
            output_path = file_path.parent / f"{file_path.stem}{target_ext}"

            # 如果已存在同名文件则覆盖
            shutil.copy2(target_file, output_path)

            size_kb = output_path.stat().st_size / 1024
            print(f"\n[完成] {output_path}")
            print(f"文件大小: {size_kb:.1f} KB")

        except FileNotFoundError:
            print(f"[错误] 找不到 MinerU CLI: {MINERU_EXE}")
        except Exception as e:
            print(f"[错误] 转换失败: {e}")


def convert_xls_with_pandas(file_path: Path):
    """使用 pandas 将 .xls 转为 JSON"""
    output_dir = file_path.parent
    output_name = file_path.stem + ".json"
    output_path = output_dir / output_name

    print(f"\n正在转换: {file_path.name}")
    print(f"转换引擎: pandas")
    print(f"输出文件: {output_path}\n")

    try:
        cmd = [
            PYTHON_EXE, "-c",
            f"""
import pandas as pd
import json
from pathlib import Path

df = pd.read_excel(r'{file_path}', engine='xlrd')
output_path = Path(r'{output_path}')
output_path.parent.mkdir(parents=True, exist_ok=True)

# 转换 DataFrame 为 JSON（records 格式，每行一个对象）
records = df.to_dict(orient='records')

# 处理 NaN 等特殊值
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        import math
        try:
            if isinstance(obj, float) and math.isnan(obj):
                return None
        except:
            pass
        try:
            return super().default(obj)
        except:
            return str(obj)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({{
        'sheet_name': 'Sheet1',
        'rows': len(records),
        'columns': list(df.columns),
        'data': records
    }}, f, ensure_ascii=False, indent=2, cls=NpEncoder)
print('OK')
"""
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})

        if result.returncode == 0 and "OK" in result.stdout:
            print(f"\n[完成] 转换成功: {output_path}")
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"\n[失败] 转换 .xls 文件失败")
            if error_msg:
                print(f"错误详情: {error_msg}")
            if "xlrd" in error_msg.lower():
                print("\n提示: 旧版 .xls 文件需要 xlrd 库支持，请运行:")
                print(f"  {PYTHON_EXE} -m pip install xlrd")
    except Exception as e:
        print(f"[错误] 转换失败: {e}")


def main():
    print("=" * 50)
    print("  文件格式转换工具")
    print("  基于 MinerU v3.2.3")
    print("=" * 50)

    file_path = get_file_path()
    if not file_path:
        print("[取消] 未提供文件路径")
        input("\n按回车键退出...")
        return

    if not validate_file(file_path):
        input("\n按回车键退出...")
        return

    ext = file_path.suffix.lower()

    if ext in MINERU_EXTENSIONS:
        convert_with_mineru(file_path)
    elif ext in PANDAS_EXTENSIONS:
        convert_xls_with_pandas(file_path)

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
