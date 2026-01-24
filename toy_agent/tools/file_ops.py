"""
文件操作工具
包含: read_file, multi_edit
"""
import os
import re
from typing import Dict, Any
from toy_agent import tool


@tool(name="read_file", description="读取文件内容")
async def read_file(file_path: str) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"错误: 文件 {file_path} 不存在"
    except Exception as e:
        return f"错误: 读取文件时发生异常 - {str(e)}"


def _is_binary_file(path: str) -> bool:
    """检查文件是否为二进制文件"""
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return False


def _validate_input(path: str, edit_list: list) -> Dict[str, Any]:
    """验证输入参数"""
    # 检查是否有编辑操作
    if not edit_list or len(edit_list) == 0:
        return {"valid": False, "message": "至少需要一个编辑操作"}
    
    # 解析绝对路径
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    # 检查是否为 Jupyter notebook
    if path.endswith('.ipynb'):
        return {"valid": False, "message": "不支持编辑 Jupyter Notebook 文件"}
    
    # 处理新文件创建
    if not os.path.exists(path):
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except Exception as e:
                return {"valid": False, "message": f"无法创建父目录: {str(e)}"}
        
        # 对于新文件，第一个编辑必须创建文件（空的 old_string）
        if len(edit_list) == 0 or edit_list[0].get("old_string", "") != "":
            return {"valid": False, "message": "对于新文件，第一个编辑的 old_string 必须为空"}
    else:
        # 检查是否为二进制文件
        if _is_binary_file(path):
            return {"valid": False, "message": "无法编辑二进制文件"}
        
        # 预验证所有 old_string 是否存在于文件中
        try:
            with open(path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            for i, edit in enumerate(edit_list):
                old_string = edit.get("old_string", "")
                if old_string != "" and old_string not in current_content:
                    truncated = old_string[:100] + ('...' if len(old_string) > 100 else '')
                    return {"valid": False, "message": f"编辑 {i + 1}: 要替换的字符串在文件中未找到: \"{truncated}\""}
                    
        except UnicodeDecodeError:
            return {"valid": False, "message": "无法读取文件 - 可能是二进制文件或编码问题"}
    
    # 验证每个编辑操作
    for i, edit in enumerate(edit_list):
        old_string = edit.get("old_string", "")
        new_string = edit.get("new_string", "")
        
        if old_string == new_string:
            return {"valid": False, "message": f"编辑 {i + 1}: old_string 和 new_string 不能相同"}
    
    return {"valid": True}


def _apply_content_edit(content: str, old_string: str, new_string: str, 
                        replace_all: bool = False) -> Dict[str, Any]:
    """应用单个内容编辑"""
    if replace_all:
        # 替换所有匹配项
        escaped_old = re.escape(old_string)
        pattern = re.compile(escaped_old)
        matches = pattern.findall(content)
        occurrences = len(matches)
        new_content = pattern.sub(new_string, content)
        return {"new_content": new_content, "occurrences": occurrences}
    else:
        # 替换单个匹配项
        if old_string in content:
            new_content = content.replace(old_string, new_string, 1)
            return {"new_content": new_content, "occurrences": 1}
        else:
            raise Exception(f"未找到字符串: {old_string[:50]}...")


@tool(name="multi_edit", description="对单个文件进行多次原子性编辑操作")
def multi_edit(file_path: str, edits: list) -> str:
    """
    多次编辑工具 - 对单个文件进行多次原子性编辑操作
    
    Args:
        file_path: 要修改的文件的绝对路径
        edits: 编辑操作数组，每个操作包含:
            - old_string: 要替换的文本
            - new_string: 替换后的新文本
            - replace_all: 是否替换所有匹配项（可选，默认 False）
            
    Returns:
        操作结果摘要
    """
    try:
        # 验证输入
        print(f"[multi_edit] file_path: {file_path}, edits: {edits}")
        validation_result = _validate_input(file_path, edits)
        if not validation_result["valid"]:
            return f"错误: {validation_result['message']}"
        
        # 解析绝对路径
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # 读取当前文件内容（新文件为空）
        file_exists = os.path.exists(file_path)
        
        if file_exists:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            except UnicodeDecodeError:
                return "错误: 无法读取文件 - 可能是二进制文件或编码问题"
        else:
            current_content = ""
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 按顺序应用所有编辑
        modified_content = current_content
        applied_edits = []
        
        for i, edit in enumerate(edits):
            old_string = edit.get("old_string", "")
            new_string = edit.get("new_string", "")
            replace_all_flag = edit.get("replace_all", False)
            
            try:
                result = _apply_content_edit(
                    modified_content, old_string, new_string, replace_all_flag
                )
                modified_content = result["new_content"]
                applied_edits.append({
                    "edit_index": i + 1,
                    "success": True,
                    "old_string": old_string[:100] + ("..." if len(old_string) > 100 else ""),
                    "new_string": new_string[:100] + ("..." if len(new_string) > 100 else ""),
                    "occurrences": result["occurrences"]
                })
            except Exception as e:
                return f"编辑 {i + 1} 出错: {str(e)}"
        
        # 写入修改后的内容
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        except Exception as e:
            return f"写入文件时出错: {str(e)}"
        
        # 生成结果摘要
        operation = "创建" if not file_exists else "更新"
        summary = f"成功对 {file_path} 应用了 {len(edits)} 个编辑操作"
        
        details = []
        for edit_info in applied_edits:
            details.append(f"编辑 {edit_info['edit_index']}: 替换了 {edit_info['occurrences']} 处匹配")
        
        if details:
            summary += "\n" + "\n".join(details)
        
        return summary
        
    except Exception as e:
        return f"多次编辑过程中出错: {str(e)}"

