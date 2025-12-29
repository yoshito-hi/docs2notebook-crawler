import logging
import sys

def setup_logger(name: str = "docs2notebook", level: int = logging.INFO) -> logging.Logger:
    """
    アプリケーション全体のロガーを設定します。
    
    Args:
        name: ロガー名
        level: ログレベル
        
    Returns:
        設定済みのロガーインスタンス
    """
    # ルートロガーの設定（または指定された名前のロガー）
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # ハンドラが既にある場合は追加しない
    if logger.hasHandlers():
        return logger

    # 標準エラー出力へのハンドラ（進捗ログ用）
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    
    # フォーマット設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger
