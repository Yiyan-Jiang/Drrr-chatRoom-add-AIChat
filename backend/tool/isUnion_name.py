from sqlalchemy.exc import IntegrityError

def is_duplicate_entry_error(exc: IntegrityError, field_name: str) -> bool:

    # 判断 IntegrityError 是否由指定字段的唯一约束冲突引起
    orig = exc.orig
    if orig is None:
        return False

    # PyMySQL 的 IntegrityError 错误码为 1062
    if hasattr(orig, 'args') and len(orig.args) >= 2:
        error_code = orig.args[0]
        error_msg = orig.args[1].lower()
        # 1062 是 MySQL 的 Duplicate entry 错误码
        if error_code == 1062 and field_name.lower() in error_msg:
            return True


    error_str = str(orig).lower()
    return "duplicate entry" in error_str and field_name.lower() in error_str