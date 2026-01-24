"""
apply_patch 工具
支持解析和应用 unified diff 格式的补丁
"""
import os
import re
from typing import Dict, List, Tuple, Optional, Any
from toy_agent import tool

# https://github.com/openai/openai-agents-python/blob/main/examples/tools/apply_patch.py

def _parse_unified_diff(patch_content: str) -> List[Dict[str, Any]]:
    """
    解析 unified diff 格式的补丁内容
    
    Args:
        patch_content: unified diff 格式的补丁字符串
        
    Returns:
        补丁操作列表，每个操作包含:
        - file_path: 文件路径
        - hunks: 补丁块列表，每个块包含:
            - old_start: 原始起始行号
            - old_count: 原始行数
            - new_start: 新起始行号
            - new_count: 新行数
            - lines: 行操作列表（' '=保持, '-'=删除, '+'=添加）
    """
    patches = []
    lines = patch_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 查找文件头：--- a/path 或 --- path
        if line.startswith('--- '):
            old_file = line[4:].strip()
            # 移除 'a/' 前缀（如果存在）
            if old_file.startswith('a/'):
                old_file = old_file[2:]
            # 移除时间戳（如果存在）
            old_file = old_file.split('\t')[0]
            
            # 查找对应的 +++ 行
            i += 1
            if i >= len(lines) or not lines[i].startswith('+++ '):
                i += 1
                continue
            
            new_file = lines[i][4:].strip()
            if new_file.startswith('b/'):
                new_file = new_file[2:]
            new_file = new_file.split('\t')[0]
            
            # 使用 new_file 作为目标文件路径，如果为空则使用 old_file
            file_path = new_file if new_file != '/dev/null' else old_file
            if file_path == '/dev/null':
                i += 1
                continue
            
            i += 1
            hunks = []
            
            # 解析补丁块（hunks）
            while i < len(lines):
                line = lines[i]
                
                # 查找 hunk 头：@@ -old_start,old_count +new_start,new_count @@
                if line.startswith('@@ '):
                    hunk_match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                    if not hunk_match:
                        i += 1
                        continue
                    
                    old_start = int(hunk_match.group(1))
                    old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                    new_start = int(hunk_match.group(3))
                    new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1
                    
                    i += 1
                    hunk_lines = []
                    
                    # 解析 hunk 内容
                    while i < len(lines):
                        hunk_line = lines[i]
                        
                        # 如果遇到新的文件头或 hunk 头，停止当前 hunk
                        if hunk_line.startswith('--- ') or hunk_line.startswith('@@ '):
                            break
                        
                        if hunk_line.startswith('\\'):
                            # 忽略 "\ No newline at end of file"
                            i += 1
                            continue
                        
                        if hunk_line.startswith(' '):
                            # 上下文行（保持不变）
                            hunk_lines.append((' ', hunk_line[1:]))
                        elif hunk_line.startswith('-'):
                            # 删除行
                            hunk_lines.append(('-', hunk_line[1:]))
                        elif hunk_line.startswith('+'):
                            # 添加行
                            hunk_lines.append(('+', hunk_line[1:]))
                        else:
                            # 空行或其他，作为上下文处理
                            if hunk_line == '':
                                hunk_lines.append((' ', ''))
                            else:
                                break
                        
                        i += 1
                    
                    hunks.append({
                        'old_start': old_start,
                        'old_count': old_count,
                        'new_start': new_start,
                        'new_count': new_count,
                        'lines': hunk_lines
                    })
                elif line.startswith('--- '):
                    # 遇到新文件，停止当前文件解析
                    break
                else:
                    i += 1
                    if i >= len(lines) or lines[i].startswith('--- '):
                        break
            
            if hunks:
                patches.append({
                    'file_path': file_path,
                    'hunks': hunks
                })
        else:
            i += 1
    
    return patches


def _apply_hunk_to_content(content: str, hunk: Dict) -> Tuple[str, bool]:
    """
    将单个 hunk 应用到文件内容
    
    Args:
        content: 原始文件内容
        hunk: hunk 字典，包含 old_start, old_count, new_start, new_count, lines
        
    Returns:
        (new_content, success) 元组
    """
    lines = content.split('\n')
    # 处理文件末尾没有换行符的情况
    if content and not content.endswith('\n'):
        # 如果原文件末尾没有换行，split('\n') 会保留最后一个空字符串
        # 但我们需要移除它
        if lines and lines[-1] == '':
            lines = lines[:-1]
    
    old_start = hunk['old_start'] - 1  # 转换为 0-based 索引
    hunk_lines = hunk['lines']
    
    # 验证上下文匹配
    # 计算需要匹配的行数（上下文行和删除行）
    match_count = sum(1 for op, _ in hunk_lines if op in (' ', '-'))
    
    # 检查是否有足够的行来匹配
    if old_start + match_count > len(lines):
        return content, False
    
    # 验证每一行是否匹配
    line_idx = old_start
    for op, expected_line in hunk_lines:
        if op == ' ' or op == '-':
            actual_line = lines[line_idx] if line_idx < len(lines) else ''
            if actual_line != expected_line:
                # 上下文不匹配
                return content, False
            line_idx += 1
    
    # 应用补丁：构建新内容
    new_lines = []
    
    # 添加 hunk 之前的内容
    new_lines.extend(lines[:old_start])
    
    # 应用 hunk
    line_idx = old_start
    for op, line in hunk_lines:
        if op == ' ':
            # 保持原行（上下文）
            if line_idx < len(lines):
                new_lines.append(lines[line_idx])
            line_idx += 1
        elif op == '-':
            # 删除行
            line_idx += 1
        elif op == '+':
            # 添加行
            new_lines.append(line)
    
    # 添加 hunk 之后的内容
    new_lines.extend(lines[line_idx:])
    
    return '\n'.join(new_lines), True


def _apply_patch_to_file(file_path: str, hunks: List[Dict]) -> Dict[str, Any]:
    """
    将补丁应用到单个文件
    
    Args:
        file_path: 目标文件路径
        hunks: hunk 列表
        
    Returns:
        操作结果字典
    """
    # 解析绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    # 检查文件是否存在
    file_exists = os.path.exists(file_path)
    
    if not file_exists:
        # 创建新文件
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'无法创建父目录: {str(e)}'
                }
        
        # 对于新文件，构建内容
        content = ''
        for hunk in hunks:
            for op, line in hunk['lines']:
                if op == '+':
                    content += line + '\n'
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.rstrip('\n'))
            return {
                'success': True,
                'message': f'成功创建文件 {file_path}',
                'file_path': file_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'写入文件时出错: {str(e)}'
            }
    
    # 读取现有文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return {
            'success': False,
            'error': '无法读取文件 - 可能是二进制文件或编码问题'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'读取文件时出错: {str(e)}'
        }
    
    # 按顺序应用所有 hunks
    modified_content = content
    applied_hunks = []
    failed_hunks = []
    
    for i, hunk in enumerate(hunks):
        new_content, success = _apply_hunk_to_content(modified_content, hunk)
        if success:
            modified_content = new_content
            applied_hunks.append(i + 1)
        else:
            failed_hunks.append(i + 1)
    
    if failed_hunks:
        return {
            'success': False,
            'error': f'部分 hunk 应用失败: {failed_hunks}',
            'applied_hunks': applied_hunks,
            'failed_hunks': failed_hunks
        }
    
    # 写入修改后的内容
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return {
            'success': True,
            'message': f'成功应用补丁到 {file_path}',
            'file_path': file_path,
            'applied_hunks': len(applied_hunks)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'写入文件时出错: {str(e)}'
        }


@tool(name="apply_patch", description="应用 unified diff 格式的补丁到文件")
def apply_patch(patch: str, base_path: Optional[str] = None) -> str:
    """
    应用 unified diff 格式的补丁到文件
    
    支持标准的 unified diff 格式（类似 git diff 的输出）：
    --- a/file.py
    +++ b/file.py
    @@ -1,3 +1,3 @@
     line1
    -line2
    +new_line2
     line3
    
    Args:
        patch: unified diff 格式的补丁字符串
        base_path: 基础路径（可选），用于解析相对路径
        
    Returns:
        操作结果摘要
    """
    try:
        if not patch or not patch.strip():
            return "错误: 补丁内容不能为空"
        
        # 解析补丁
        patches = _parse_unified_diff(patch)
        
        if not patches:
            return "错误: 无法解析补丁内容，请确保是有效的 unified diff 格式"
        
        # 应用每个文件的补丁
        results = []
        for patch_info in patches:
            file_path = patch_info['file_path']
            hunks = patch_info['hunks']
            
            # 如果提供了 base_path，则解析相对路径
            if base_path and not os.path.isabs(file_path):
                if os.path.isabs(base_path):
                    file_path = os.path.join(base_path, file_path.lstrip('/'))
                else:
                    file_path = os.path.join(os.path.abspath(base_path), file_path.lstrip('/'))
            
            result = _apply_patch_to_file(file_path, hunks)
            results.append({
                'file_path': file_path,
                **result
            })
        
        # 生成结果摘要
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        summary_lines = [f"补丁应用完成: {success_count}/{total_count} 个文件成功"]
        
        for result in results:
            if result.get('success', False):
                summary_lines.append(f"✓ {result['file_path']}: {result.get('message', '成功')}")
            else:
                summary_lines.append(f"✗ {result['file_path']}: {result.get('error', '失败')}")
        
        return '\n'.join(summary_lines)
        
    except Exception as e:
        return f"应用补丁时出错: {str(e)}"

