import os
from concurrent.futures import ThreadPoolExecutor
from actions.recall import recall
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCABULARY_DIR = os.path.join(BASE_DIR, "Vocabulary")


def check_file_for_substring(filepath, content_lower):
    """
    检查单个词库文件是否包含屏蔽词
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word and word in content_lower:
                    print(f"匹配到文件：{os.path.basename(filepath)}，词条：'{word}'")
                    return True
    except Exception as e:
        print(f"读取文件失败 {filepath}: {e}")
    return False


def check_and_recall(chat_id, msg_id, content):
    """
    检查消息是否包含屏蔽词，匹配则撤回
    """
    txt_files = [
        os.path.join(VOCABULARY_DIR, f)
        for f in os.listdir(VOCABULARY_DIR) if f.endswith(".txt")
    ]
    content_lower = content.lower()

    with ThreadPoolExecutor(max_workers=8) as executor:
        for matched in executor.map(
            lambda f: check_file_for_substring(f, content_lower),
            txt_files
        ):
            if matched:
                recall(chat_id, msg_id)
                return True  # 有匹配，直接返回 True
    return False  # 没匹配到