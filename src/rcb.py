# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7
import os
import sys
import shutil
import time

#TODO: /// USER CONFIGURATION ///////////////////////////////////////////////////////////////////
RECYCLE_BIN_ROOT_DIR = "/root/test/.recycle_bin" # Thư mục chứa thùng rác
MAX_CYCLE_BIN_SIZE_GB = 20                       # Dung lượng tối đa của thùng rác
MAX_STORE_DAY = 30                               # Số ngày tồn tại tối đa của file trong thùng rác

CHECK_FILE_SIZE_AND_TYPE = True                  # Kiểm tra kích thước và kiểu dữ liệu của file
MAX_FILE_SIZE_MB = 1000                          # Kích thước tối đa của file
IGNORE_FILE_TYPE = [".vpd", ".fsdb"]             # Loại file không được lưu trữ trong thùng rác
#TODO://////////////////////////////////////////////////////////////////////////////////////////

#\/// DAILY TASK ///////////////////////////////////////////////////////////////////////////////
def handle_daily_maintenance():
    # 1. Kiểm tra và xóa các file có thời gian tồn tại lớn hơn MAX_STORE_DAY
    # 2. Kiểm tra và xóa các file có kích thước lớn hơn MAX_FILE_SIZE_MB
    # 3. Kiểm tra và xóa các file có kiểu dữ liệu không nằm trong IGNORE_FILE_TYPE
    # 4. Kiểm tra dung lượng của thư mục RECYCLE_BIN_ROOT_DIR, nếu lớn hơn MAX_CYCLE_BIN_SIZE_GB thì xóa các file có thời gian tồn tại lớn nhất.
    ### TASK 1 ###
    cleanup_old_files()
    ### TASK 2 & 3 ###
    if CHECK_FILE_SIZE_AND_TYPE:
      check_file_size_and_type()
    ### TASK 4 ###
    keep_recycle_bin_in_max()

def check_file_size_and_type():
    """
    Kiểm tra và xóa các file trong thùng rác dựa trên:
    - Kích thước file > MAX_FILE_SIZE_MB
    - File có đuôi nằm trong IGNORE_FILE_TYPE
    """
    for dir_path, dir_names, file_names in os.walk(RECYCLE_BIN_ROOT_DIR):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)

            # Kiểm tra kích thước file
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE_MB * (1024 ** 2):
                os.remove(file_path)
                print(f"Đã xóa file vượt quá kích thước cho phép: {file_path}")
                continue

            # Kiểm tra loại file
            if any(file_name.endswith(ext) for ext in IGNORE_FILE_TYPE):
                os.remove(file_path)
                print(f"Đã xóa file thuộc loại bị cấm: {file_path}")

    # Dọn dẹp thư mục rỗng sau khi xóa file
    removeEmptyDirs(RECYCLE_BIN_ROOT_DIR)

def keep_recycle_bin_in_max():
    max_size_bytes = MAX_CYCLE_BIN_SIZE_GB * (1024 ** 3)

    files = []
    total_size = 0
    for dp, dn, filenames in os.walk(RECYCLE_BIN_ROOT_DIR):
        for f in filenames:
            file_path = os.path.join(dp, f)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            files.append((file_path, os.path.getmtime(file_path), file_size))

    if total_size > max_size_bytes:
        files.sort(key=lambda x: x[1])
        while files and total_size > max_size_bytes:
            oldest_file, _, file_size = files.pop(0)
            total_size -= file_size
            os.remove(oldest_file)
            print("Deleted file: {}".format(oldest_file))
        print("Total size after deletion: {} bytes".format(total_size))
    removeEmptyDirs(RECYCLE_BIN_ROOT_DIR)

def cleanup_old_files():
    cutoff_time = time.time() - (MAX_STORE_DAY * 86400)
    for dp, dn, filenames in os.walk(RECYCLE_BIN_ROOT_DIR):
        for f in filenames:
            file_path = os.path.join(dp, f)
            if os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)

#\/// FUNCTIONS ///////////////////////////////////////////////////////////////////////////////

def check_space_and_cleanup(file_size):
    max_size_bytes = MAX_CYCLE_BIN_SIZE_GB * (1024 ** 3)

    total_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, filenames in os.walk(RECYCLE_BIN_ROOT_DIR) for f in filenames)

    if total_size + file_size > max_size_bytes:
        files = [(os.path.join(dp, f), os.path.getmtime(os.path.join(dp, f))) for dp, dn, filenames in os.walk(RECYCLE_BIN_ROOT_DIR) for f in filenames]
        files.sort(key=lambda x: x[1])

        while files and total_size + file_size > max_size_bytes:
            oldest_file, _ = files.pop(0)
            total_size -= os.path.getsize(oldest_file)
            os.remove(oldest_file)

def get_recycle_path(filepath):
    filepath = os.path.abspath(filepath)
    rel_path = filepath[1:] if filepath.startswith('/') else filepath
    return os.path.join(RECYCLE_BIN_ROOT_DIR, rel_path)

def check_and_remove_large_and_ignore_files(dir_path, file_names):
    for file_name in file_names:
        file_size = os.path.getsize(dir_path+'/'+file_name)
        if file_size > MAX_FILE_SIZE_MB * (1024 ** 2):
            os.remove(dir_path+'/'+file_name)
            print(f"Deleted file: {file_name}")
            return "deleted"
        else:
            if any(file_name.endswith(ext) for ext in IGNORE_FILE_TYPE):
                os.remove(dir_path+'/'+file_name)
                print(f"Deleted file: {file_name}")
                return "deleted"

def move_to_recycle_bin(arg_list: list):
    for filepath in arg_list:
        if filepath.startswith('-'):
            continue # skip the option
        else:
            if RECYCLE_BIN_ROOT_DIR in filepath or "@RCB/" in filepath:
                filepath = filepath.replace("@RCB",RECYCLE_BIN_ROOT_DIR)
                os.system("rm -rdf '{}'".format(filepath)) #User xóa file từ thùng rác.
                print("\033[91mDeleted file from Recycle Bin: {}\033[0m".format(filepath))
            else:
                current_dir = os.path.abspath(os.getcwd())
                try:
                    original_path = os.path.join(current_dir, filepath)
                    recycle_path = get_recycle_path(filepath)
                    recycle_dir = os.path.dirname(recycle_path)
                    if not os.path.exists(recycle_dir):
                        os.makedirs(recycle_dir)

                    shutil.move(filepath, recycle_path)
                    removeEmptyDirs(recycle_dir)

                except:
                    print(f"\033[91mFile/Directory '{filepath}' not found in '{current_dir}'\033[0m")
                finally:
                    os.system("rm -rdf '{}'".format(filepath)) #Đảm bảo file/folder được xóa

def removeEmptyDirs(dir_path):
    for dir_path, dir_names, file_names in os.walk(dir_path, topdown=False):
        for dir_name in dir_names:
            dir_path_to_remove = os.path.join(dir_path, dir_name)
            if not os.listdir(dir_path_to_remove):
                os.rmdir(dir_path_to_remove)

def handle_restore(arg_list: list):
    #Có 3 dạng targer:
    #1. Relative path: là target không có ký tự '/' ở đầu.
    #2. Absolute path: là target có ký tự '/' ở đầu và không chứa RECYCLE_BIN_ROOT_DIR trong đường dẫn.
    #3. Recycle path : là target có ký tự '/' ở đầu và chứa RECYCLE_BIN_ROOT_DIR trong đường dẫn.
    for target in arg_list:
        if target.startswith('-'):
            continue # skip the option
        else:
            if target.startswith('/'):
                if RECYCLE_BIN_ROOT_DIR in target or "@RCB/" in target:
                    targetType = "recycle_path"
                    des_path = target.replace(RECYCLE_BIN_ROOT_DIR, "")
                    des_path = des_path.replace("@RCB", "")
                    source_path = get_recycle_path(des_path)
                else:
                    targetType = "absolute_path"
                    des_path = target
                    source_path = get_recycle_path(des_path)
            else:
                targetType = "relative_path"
                des_path = os.path.join(os.getcwd(), target)
                source_path = get_recycle_path(des_path)

            if target == "all":
                targetType = "all"
                des_path = os.getcwd()
                source_path = RECYCLE_BIN_ROOT_DIR+des_path

            print(f"TARGET TYPE: {targetType}")
            print(f"ORIGINAL FILE PATH: {des_path}")
            print(f"RECYCLE FILE PATH: {source_path}")

            # original_target_dir = os.path.abspath(os.getcwd())  # Đường dẫn gốc
            # recycle_target_dir = get_recycle_path(original_target_dir)
            if target == "all":
                os.system("mv "+source_path+"/* "+des_path)
                print(f"\033[92mRestored all files and directories from recycle bin to '{des_path}'\033[0m")
            else:
                if os.path.exists(source_path):
                    #Tạo thư mục cha nếu không tồn tại
                    if not os.path.exists(os.path.dirname(des_path)):
                        os.makedirs(os.path.dirname(des_path))
                    shutil.move(source_path, des_path)
                    print(f"\033[92mRestored: {target}\033[0m")
                else:
                    print(f"\033[91mFile/Directory '{target}' not found in recycle bin at '{source_path}'\033[0m")
            removeEmptyDirs(RECYCLE_BIN_ROOT_DIR)

def handle_ls(path="./"):
    try:
      current_dir = os.path.abspath(path)
      check_path = get_recycle_path(current_dir)
      result = os.popen("ls -lha '{}'".format(check_path)).read()
      if result == "":
          print("\033[93mNOT FOUND\033[0m")
      else:
          print("\033[93m{}\033[0m".format(result))
    except:
      print("\033[93mNOT FOUND\033[0m")

def handle_path_dir(path="./"):
    try:
      current_dir = os.path.abspath(path)
      check_path = get_recycle_path(current_dir)
      result = os.popen("tree -ifFhDa {} | grep -v '/$'".format(check_path)).read()
      result = result.replace(RECYCLE_BIN_ROOT_DIR, "@RCB")
      if result == "":
          print("\033[93mNOT FOUND\033[0m")
      else:
          print("\033[93m{}\033[0m".format(result))
    except:
      print("\033[93mNOT FOUND\033[0m")

def handle_tree(path="./"):
    try:
        current_dir = os.path.abspath(path)
        tree_path = get_recycle_path(current_dir)
        result = os.popen("tree '{}'".format(tree_path)).read()
        if result == "":
            print("\033[93mNOT FOUND\033[0m")
        else:
            print("\033[93m{}\033[0m".format(result))
    except:
        print("\033[93mNOT FOUND\033[0m")

def handle_clean(path="./"):
    RED       = "\033[91m"
    RED_BG    = "\033[41m"
    RESET     = "\033[0m"
    current_dir = os.path.abspath(path)
    clean_path = get_recycle_path(current_dir)

    confirm = input(f"{RED_BG}[WARNING]{RESET}{RED} Bạn có chắc chắn muốn xóa '{clean_path}' không? (y/n): {RESET}")
    if confirm.lower() == 'y':
        os.system("rm -rdf {}/*".format(clean_path))
        print("Dữ liệu đã được xóa.")
    else:
        print("Hủy bỏ hành động xóa.")

def handle_empty():
    RED       = "\033[91m"
    RED_BG    = "\033[41m"
    RESET     = "\033[0m"

    confirm = input(f"{RED_BG}[WARNING]{RESET}{RED} Bạn có chắc chắn muốn xóa toàn bộ dữ liệu tự Recycle Bin không? (y/n): {RESET}")
    if confirm.lower() == 'y':
        os.system("rm -rdf {}/*".format(RECYCLE_BIN_ROOT_DIR))
        print("Dữ liệu đã được xóa.")
    else:
        print("Hủy bỏ hành động xóa.")


def handle_info():
    total_size_bytes = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, filenames in os.walk(RECYCLE_BIN_ROOT_DIR) for f in filenames)
    total_size_gb = total_size_bytes / (1024 ** 3)
    max_size_gb = MAX_CYCLE_BIN_SIZE_GB
    usage_percentage = (total_size_gb / max_size_gb) * 100 if max_size_gb > 0 else 0

    print("\033[92mUsage/Total  : {:.2f}/{}GB ({:.1f}%)\033[0m".format(total_size_gb,max_size_gb, usage_percentage))
    print("\033[92mMax store day: {} days\033[0m".format(MAX_STORE_DAY))
    if CHECK_FILE_SIZE_AND_TYPE:
        print("\033[92mMax file size: {} MB\033[0m".format(MAX_FILE_SIZE_MB))
        print("\033[92mIgnore files : {}\033[0m".format(IGNORE_FILE_TYPE))
    else:
        print("\033[92mCheck file size and type: False\033[0m")
    print("\033[92mRecycle Bin Alive: {}/{} days {}\033[0m".format("30","365",""))

    # Tìm 10 file lớn nhất
    all_files = [(os.path.join(dp, f), os.path.getsize(os.path.join(dp, f))) for dp, dn, filenames in os.walk(RECYCLE_BIN_ROOT_DIR) for f in filenames]
    top_files = sorted(all_files, key=lambda x: x[1], reverse=True)[:10]
    print("\033[93m========================================\033[0m")
    print("\033[93mTop 10 biggest files:\033[0m")
    for file_path, size in top_files:
        file_path_new = file_path.replace(RECYCLE_BIN_ROOT_DIR, "@RCB")
        print("\033[93m{}: {:.2f} MB\033[0m".format(file_path_new, size / (1024 ** 2)))
    print("")
    # # In tree với dung lượng cho 1 cấp độ
    # print("\n\033[94m========================================\033[0m")
    # #Dùng lệnh du -h --max-depth=1 để in ra dung lượng của các thư mục con và thêm ANSI
    # os.system("du -h --max-depth=1 '{}' | sed 's|{}|\\[BIN\\]|g' | awk '{{print \"\033[94m\"$1, $2\"\033[0m\"}}' | column -t".format(RECYCLE_BIN_ROOT_DIR, RECYCLE_BIN_ROOT_DIR))


def print_help():
    # Mã ANSI cho màu sắc
    RED       = "\033[91m"
    GREEN     = "\033[92m"
    YELLOW    = "\033[93m"
    BLUE      = "\033[94m"
    GRAY      = "\033[90m"
    RED_BG    = "\033[41m"
    GREEN_BG  = "\033[42m"
    YELLOW_BG = "\033[43m"
    BLUE_BG   = "\033[44m"
    GRAY_BG   = "\033[40m"
    RESET     = "\033[0m"

    print("{}Usage: rcb <command> [<path>]{}".format(GREEN, RESET))
    print("{}Commands:{}".format(YELLOW, RESET))
    print("{} === [1] List Group  === {}   ".format(GREEN_BG, RESET))
    print("{} + ls      {}[path|./]   {}   Execute 'ls' command for [path] in recycle bin.   {}{}{}{}{}{}EX: {}rcb ls   {}./data/{}".format(GREEN,GRAY,RESET,"","","","","","",GREEN,GRAY,RESET))
    print("{} + path    {}[path|./]   {}   Show path for [path] in recycle bin.              {}{}{}{}{}{}EX: {}rcb path {}./data/{}".format(GREEN,GRAY,RESET,"","","","","","",GREEN,GRAY,RESET))
    print("{} + tree    {}[path|./]   {}   Execute 'tree' command for [path] in recycle bin. {}{}{}{}{}{}EX: {}rcb tree {}./data/{}".format(GREEN,GRAY,RESET,"","","","","","",GREEN,GRAY,RESET))
    print("{} === [2] Del/Restore === {}   ".format(BLUE_BG, RESET))
    print("{} + delete  {}<path>      {}   Move {}<path>{} to recycle bin {}(Alias to rm).{}         {}{}EX: {}rcb delete  {}./data/abc{}".format(BLUE,RED,RESET,RED,RESET,YELLOW,RESET,"","",BLUE,RED,RESET))
    print("{} + restore {}<path/'all'>{}   Restore {}<path>{} or {}'all'{} from current dir.         {}{}EX: {}rcb restore {}./data/abc{}".format(BLUE,RED,RESET,RED,RESET,RED,RESET,"","",BLUE,RED,RESET))
    print("{} + clean   {}[path|./]   {}   Remove all data from [path] in recycle bin.       {}{}{}{}{}{}EX: {}rcb clean   {}./data/abc{}".format(BLUE,GRAY,RESET,"","","","","","",BLUE,GRAY,RESET))
    print("{} + empty   {}               {}Empty entire recycle bin.                         {}{}{}{}{}{}EX: {}rcb empty{}".format(BLUE,RESET,"","","","","","","",BLUE,RESET))
    print("{} === [3] Info/Help   === {}   ".format(GREEN_BG, RESET))
    print("{} + info                  {} {}Show information about the recycle bin.           {}{}{}{}{}{}EX: {}rcb info{}".format(GREEN,RESET,"","","","","","","",GREEN,RESET))
    print("{} + help, -h,--help       {} {}Show this help message.                           {}{}{}{}{}{}EX: {}rcb -h{}".format(GREEN,RESET,"","","","","","","",GREEN,RESET))
    print("")

if __name__ == '__main__':
    ############################################
    #1. Nhận đối số đầu vào: Commmand và path
    ############################################
    command  = sys.argv[1] if len(sys.argv) >= 2 else "help"
    firstArg = sys.argv[2] if len(sys.argv) >= 3 else "./"
    if firstArg.startswith("-"): #firstArg is option. Ex: rm -rdf ./file.txt
        path = sys.argv[3] if len(sys.argv) >= 4 else "./"
    else:
        path = firstArg

    ############################################
    #2. Xử lý các lệnh Command
    ############################################
    ### a. List Group ###
    if command == "ls":
          handle_ls(path)
    elif command == "path" or command == "dir":
        handle_path_dir(path)
    elif command == "tree":
        handle_tree(path)
    ### b. Del/Restore Group ###
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: rcb.py delete <file_path>")
            sys.exit(1)
        move_to_recycle_bin(sys.argv[2:])
    elif command == "restore":
        if len(sys.argv) < 3:
            print("Usage: rcb.py restore <file/dir/all>")
            sys.exit(1)
        handle_restore(sys.argv[2:])
    elif command == "clean":
        handle_clean(path)
    elif command == "empty":
        handle_empty()
    ### c. Info/Help Group ###
    elif command == "info":
        handle_info()
    elif command in ["help", "-h", "--help"]:
        print_help()
    ### d. Other ###
    elif command == "daily_maintenance":
        handle_daily_maintenance()
    else:
        print_help()


# os.system("rm -rdf /root/test/.recycle_bin/*")
# os.system("rm -rdf /root/test/data")
# os.makedirs("/root/test/data")
# os.chdir("/root/test/data")
# ### PREPARE TEST DATA ###
# os.makedirs("🔴🅰️MainA/🟡🅰️SubA")
# os.system("touch 🔴🅰️MainA/🔴🅰️MainA_file.fsdb")
# os.system("touch 🔴🅰️MainA/🟡🅰️SubA/🟡🅰️SubA_file.fsdb")
# with open("root_big_file_15MB.txt", "w") as f:
#     for i in range(1000000):
#         f.write("I'm a big file\n")
# os.system("touch root_file1.fsdb")
# os.system("touch root_file2.vpd")
# os.system("touch root_file3.txt")
# os.makedirs("🟢Ⓜ️MainB/🟡Ⓜ️SubB")
# os.system("touch 🟢Ⓜ️MainB/🟢Ⓜ️MainB_file.vpd")
# os.system("touch 🟢Ⓜ️MainB/🟡Ⓜ️SubB/🟡Ⓜ️SubB_file.vpd")

### DELETE ###
# move_to_recycle_bin("root_file1.fsdb")
# move_to_recycle_bin("root_file2.vpd")
# move_to_recycle_bin("root_file3.txt")
# move_to_recycle_bin("root_big_file_15MB.txt")
# move_to_recycle_bin("🔴🅰️MainA")
# move_to_recycle_bin("🟢Ⓜ️MainB")

### RESTORE ###
# handle_ls()
# handle_tree()
# os.makedirs("🟢Ⓜ️MainB/🟡Ⓜ️SubB")
# os.chdir("/root/test/data/🟢Ⓜ️MainB/🟡Ⓜ️SubB")
# handle_ls()



# handle_restore("./🟢Ⓜ️MainB/🟡Ⓜ️SubB/🟡Ⓜ️SubB_file.vpd")
# handle_restore("all")
# handle_path_dir()




# handle_restore("root_file1.txt")
# handle_restore("root_file2.txt")
# handle_restore("root_file3.txt")
# handle_restore("🔴🅰️MainA")
# handle_restore("🟢Ⓜ️MainB")
# handle_restore("🔴🅰️MainA/🟡🅰️SubA/🟡🅰️SubA_file.txt")
# handle_info()
# keep_recycle_bin_in_max()
# cleanup_old_files()

# 1. rm mà đường đẫn có chứa RECYCLE_BIN_ROOT_DIR thì bỏ qua
# 2. thêm rcb (ls, path/dir, tree)
# 3. file size và type chỉ check 1 lần mỗi ngày.
# 4. Thêm xác nhận khi clean và empty
# 5. Thêm phần xin số ngày RCC Alive

# print_help()
# handle_clean()
# # handle_empty()
# print(f"\033[5mABC\033[0m")
# # time.sleep(5)

# print('\033[0;93m normal yellow\033[m')
# print('\033[1;93m bold yellow\033[m')
# print('\033[4;93m underlined yellow\033[m')
# print('\033[5;93m blinking yellow\033[m')
# print('\033[7;93m reversed yellow\033[m')
# print('\033[8;93m hide yellow\033[m')
# print('\033[1;7;21;93m bold reversed yellow\033[m')
# time.sleep(5)
