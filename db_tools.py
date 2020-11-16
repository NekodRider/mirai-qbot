from json.decoder import JSONDecodeError
import sys
import json
from bot import Storage

if __name__ == "__main__":
    db = Storage.load()
    print(f"当前群组有: {list(db.groups.keys())}, 请输入要修改的群号或 N 跳过:")
    input = sys.stdin.readline().strip()
    while input != "N":
        try:
            group_index = int(input)
            if group_index not in db.groups.keys():
                print("请输入正确的群号或 N 跳过:")
                input = sys.stdin.readline().strip()
                continue
            print(f"当前群组已有数据为: {db.groups[group_index]}, 请输入修改后的数据或 N 跳过:")
            group_value = sys.stdin.readline().strip().replace("'", '"')
            while group_value != "N":
                try:
                    db.groups = json.loads(group_value)
                    break
                except JSONDecodeError as e:
                    print(f"格式不正确{e}，请重新输入修改后数据:")
                    group_value = sys.stdin.readline().strip().replace("'", '"')
            break
        except ValueError as e:
            print("请输入数字群号或 N 跳过:")
            input = sys.stdin.readline().strip()
    print(f"当前好友有: {list(db.friends.keys())}, 请输入要修改的QQ号或 N 跳过:")
    input = sys.stdin.readline().strip()
    while input != "N":
        try:
            friend_index = int(input)
            if friend_index not in db.friends.keys():
                print("请输入正确的QQ号或 N 跳过:")
                input = sys.stdin.readline().strip()
                continue
            print(f"当前好友已有数据为: {db.friends[friend_index]}, 请输入修改后的数据或 N 跳过:")
            friend_value = sys.stdin.readline().strip().replace("'", '"')
            while friend_value != "N":
                try:
                    db.friends = json.loads(friend_value)
                    break
                except JSONDecodeError as e:
                    print(f"格式不正确{e}，请重新输入修改后数据:")
                    friend_value = sys.stdin.readline().strip().replace(
                        "'", '"')
            break
        except ValueError as e:
            print("请输入数字QQ号或 N 跳过:")
            input = sys.stdin.readline().strip()