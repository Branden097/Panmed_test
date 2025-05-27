from flask import Flask, jsonify, request, abort, render_template
from flask_wtf.csrf import CSRFProtect
import pandas as pd
import os
import yaml
from send_email import send_email  # 匯入 send_email 函式
from csis_data import get_value, add_dpdr, get_datarecord_id, get_mrn, get_valueDesc  # 匯入其他函式
import logging
import json

# 設置 logging 設定
logging.basicConfig(
    filename='app.log',        # 日誌檔案名稱
    level=logging.INFO,         # 記錄的最低等級
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = "your-secret-key"  # 必須設定，不然 CSRF 無法運作

csrf = CSRFProtect(app)

# 定義 Excel 檔案名稱
excel_file = 'random_results.xlsx'
progress_file = 'progress.json'

initial_progress = {"group1": 0, "group2": 0, "group3": 0, "group4": 0}

@app.route('/confirm')
def confirm_page():
    # 獲取查詢參數
    protocolid = request.args.get('protocolid')
    patientid = request.args.get('patientid')

    # 從函數中獲取資料
    mrn = get_mrn(patientid)
    #dcis_value = get_value(protocolid, patientid, 55926)
    #pathology_value = get_value(protocolid, patientid, 55927)
    dcis_value = get_value(protocolid, patientid, 1152)
    pathology_value = get_value(protocolid, patientid, 1153)
    
     # 根據 DCIS 值設置顯示訊息
    if dcis_value == "1":
        dcis_display = "DCIS size: ≤ 10 mm"
    elif dcis_value == "2":
        dcis_display = "DCIS size: > 10 mm"
    else:
        dcis_display = "DCIS size: 未知"

    # 根據 Pathology 值設置顯示訊息
    if pathology_value == "1":
        pathology_display = "Pathology margins: 3 to <10 mm"
    elif pathology_value == "2":
        pathology_display = "Pathology margins: ≥ 10 mm"
    else:
        pathology_display = "Pathology margins: 未知"


    # 將資料傳遞給模板
    return render_template(
        'confirm_treatment.html',
        mrn=mrn,
        protocolid=protocolid,
        patientid=patientid,
        dcis_display=dcis_display,
        pathology_display=pathology_display
    )

def load_progress():
    if os.path.exists(progress_file):
        progress = pd.read_json(progress_file).to_dict(orient="records")[0]
    else:
        progress = initial_progress

    for key in initial_progress:
        if key not in progress:
            progress[key] = initial_progress[key]

    return progress

def save_progress(progress):
    pd.DataFrame([progress]).to_json(progress_file, orient="records")

def get_sheet_name(paraA, paraB):
    if paraA == '1' and paraB == '1':
        return 'group1'
    elif paraA == '1' and paraB == '2':
        return 'group2'
    elif paraA == '2' and paraB == '1':
        return 'group3'
    elif paraA == '2' and paraB == '2':
        return 'group4'
    else:
        raise ValueError("Invalid values for paraA and paraB")

def get_number(paraA, paraB):
    progress = load_progress()
    sheet_name = get_sheet_name(paraA, paraB)
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    index = progress[sheet_name]
    if index >= len(df):
        return None

    treatment = df.iloc[index]['treatment']
    progress[sheet_name] += 1
    save_progress(progress)
    return treatment

with open("email_config.yml", "r") as file:
    config = yaml.safe_load(file)

def send_email_based_on_site(treatment, site):
    # 從 YAML 中取得對應的 to_address 列表
    to_address_list = config["email_settings"]["to_address"].get(site, ["ghchen@panmed.tw"])
    
    # 將 to_address 列表轉為逗號分隔的字串
    to_address = ", ".join(to_address_list)
    cc_address = config["email_settings"]["cc_address"]

    data = request.args.get('data')
    if data:
        params = json.loads(data)
        protocolid = params.get('prid')
        patientid = params.get('ptid')
        mrn = params.get('mrn')
        dcis_display= params.get('dcis').replace("&gt;", ">")
        pathology_display = params.get('path').replace("&lt;", "<")

    with open('progress.json', 'r') as f:
        progress_data = json.load(f)
   
    group_descriptions = {
        "group1": "Size: ≤ 10 mm & Margin width: 3 to < 10 mm",
        "group2": "Size: ≤ 10 mm & Margin width: ≥ 10 mm",
        "group3": "Size: > 10 mm & Margin width: 3 to < 10 mm",
        "group4": "Size: > 10 mm & Margin width: ≥ 10 mm"
    } 
    
    result = "\n".join([f"{group_descriptions[key]} : {value}" for key, value in progress_data[0].items()])

    total_sum = sum(progress_data[0].values())

    treatment_counts = calculate_treatment_counts(excel_file)

    #hospitalDesc = get_valueDesc(protocolid, patientid, 55924)
    hospitalDesc = get_valueDesc(protocolid, patientid, 1150)

    subject = config["email_settings"]["subject"].format(mrn=mrn)
    body = config["email_settings"]["body_template"].format(treatment=treatment,mrn=mrn,dcis_display=dcis_display,
                                                            pathology_display=pathology_display, progress=result, 
                                                            count=total_sum, treatment_counts=treatment_counts,
                                                            hospitalDesc=hospitalDesc)

    logging.error(subject)
    logging.error(body)
    # 發送電子郵件
    send_email(
        to_address=to_address,
        cc_address=cc_address,
        subject=subject,
        body=body
    )

@app.route('/get_treatment', methods=['GET'])
def get_treatment():

    data = request.args.get('data')
    if data:
        params = json.loads(data)
        protocolid = params.get('prid')
        patientid = params.get('ptid')

    # csis tra 55926 55927 是固定的 datapoint 換protocol時再確認
    #dcis = get_value(protocolid, patientid, 55926)
    #pathology= get_value(protocolid, patientid, 55927)
    #random_arm = get_value(protocolid, patientid, 55929)
    dcis = get_value(protocolid, patientid, 1152)
    pathology= get_value(protocolid, patientid, 1153)
    random_arm = get_value(protocolid, patientid, 1155)

    if random_arm is not None:
        return jsonify({"message": "Random Arm already exists"}), 200

    treatment = get_number(dcis, pathology)
    if treatment is None:
        return jsonify({"message": "No more treatments available for this group"}), 404

    #datarecord_id = get_datarecord_id(protocolid, patientid, 55926)
    datarecord_id = get_datarecord_id(protocolid, patientid, 1152)
    #add_dpdr(55929, datarecord_id, treatment, "api")
    add_dpdr(1155, datarecord_id, treatment, "api")

    # 呼叫 send_email 函式來寄送 treatment 資訊
    #site = get_value(protocolid, patientid, 55924)
    site = get_value(protocolid, patientid, 1150)
    send_email_based_on_site(treatment, site)

    return jsonify({"message": "Treatment information sent successfully", "treatment": treatment})

def calculate_treatment_counts(excel_file):
    # 載入 JSON 資料
    group_data = load_progress()  # 假設 load_progress 返回的是 JSON 字典列表
#    group_data = data[0]  # 取得第一個字典，包含 group1, group2 等資料

    # 初始化 RT 和 Tamoxifen 的總和計數
    rt_total_count = 0
    tamoxifen_total_count = 0

    # 迭代每個 group，並計算對應 sheet 中的治療筆數
    for group, count in group_data.items():
        sheet_name = group  # 每個 group 對應的 sheet 名稱，例如 "group1", "group2" 等
        df = pd.read_excel(excel_file, sheet_name=sheet_name)  # 讀取指定的 sheet

        # 選取 sheet 中的前 count 筆資料
        selected_df = df.head(count)

        # 計算 treatment 筆數，篩選 RT 和 Tamoxifen
        rt_count = selected_df[selected_df['treatment'] == 'RT'].shape[0]
        tamoxifen_count = selected_df[selected_df['treatment'] == 'Tamoxifen'].shape[0]

        # 累計每個 group 的計數
        rt_total_count += rt_count
        tamoxifen_total_count += tamoxifen_count

    # 返回結果，並換行顯示
    return f"RT: {rt_total_count}\nTamoxifen: {tamoxifen_total_count}"


@app.route('/')
def hello():
    return "Hello, Docker Compose with Flask!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

