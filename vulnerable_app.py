import os
import yaml  
import json

HARDCODED_PASSWORD = "supersecret123"

def run_shell_command(user_input):
    os.system("echo " + user_input)

def dangerous_eval(data):
    result = eval(data)
    return result

def parse_yaml(config_file_path):
    with open(config_file_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def load_progress():
    return {
        "group1": 5,
        "group2": 10
    }

def calculate_treatment_counts(excel_file):
    import pandas as pd  # 假設已安裝
    group_data = load_progress()

    rt_total_count = 0
    tamoxifen_total_count = 0

    for group, count in group_data.items():
        df = pd.read_excel(excel_file, sheet_name=group)
        selected_df = df.head(count)

        rt_count = selected_df[selected_df['treatment'] == 'RT'].shape[0]
        tamoxifen_count = selected_df[selected_df['treatment'] == 'Tamoxifen'].shape[0]

        rt_total_count += rt_count
        tamoxifen_total_count += tamoxifen_count

    return f"RT: {rt_total_count}\nTamoxifen: {tamoxifen_total_count}"

if __name__ == "__main__":
    user_input = input("Enter a shell command: ")
    run_shell_command(user_input)  # 允許注入命令

    expr = input("Enter a Python expression: ")
    print("Eval result:", dangerous_eval(expr))

    print("Password is:", HARDCODED_PASSWORD)

    config = parse_yaml("config.yml")  
    print(json.dumps(config, indent=2))

