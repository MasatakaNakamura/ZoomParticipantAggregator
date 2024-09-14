import pandas as pd

import os
import pandas as pd
import configparser
import sys

# グローバル変数としてconfigを定義
config = None

def read_properties(file_path):
    """プロパティファイルを読み込み、ConfigParserオブジェクトを返す"""
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def read_meeting_info(file_path):
    """CSVファイルからミーティング情報を読み込む"""
    meeting_info_df = pd.read_csv(file_path, encoding='utf-8', nrows=2)
    meeting_info = meeting_info_df.iloc[0].to_dict()
    return meeting_info

def read_participants_info(file_path):
    """CSVファイルから参加者情報を読み込む"""
    participant_df = pd.read_csv(file_path, encoding='utf-8', skiprows=3)
    participants_info = participant_df.iloc[4:].dropna(how='all').to_dict(orient='records')
    return participants_info

def read_csv(file_path):
    """CSVファイル全体を読み込み、ミーティング情報と参加者情報を返す"""
    meeting_info = read_meeting_info(file_path)
    participants_info = read_participants_info(file_path)
    return meeting_info, participants_info

def modify_participant_names(participants_info):
    """参加者情報の名前を統一する"""
    replace_name_dict = {
        "‗": "_",
        " ": "_"
    }
    for participant in participants_info:
        for key, value in replace_name_dict.items():
            participant['名前 (元の名前)'] = participant['名前 (元の名前)'].replace(key, value)
    return participants_info

def analyze_participants(participants_info):
    """参加者情報を集計する"""
    participants = {}
    for participant in participants_info:
        participant_info = participant['名前 (元の名前)'].split("_")
        if participant_info[0] in participants:
            participants[participant_info[0]] += 1
        else:
            participants[participant_info[0]] = 1

    # 部署名をキーにしてソート
    participants = dict(sorted(participants.items(), key=lambda x: x[0]))
    
    return participants

if __name__ == "__main__":

    # プロパティファイルのパス
    properties_file = 'config/config.properties'
    
    # プロパティファイルを読み込む
    config = read_properties(properties_file)

    # ファイルパスを指定
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = config.get('DEFAULT', 'csv_file_path')

    # ファイルが存在するかチェック
    if not os.path.exists(input_file):
        print(f"エラー: 指定されたファイルが存在しません: {input_file}")
        sys.exit(1)
        
    # CSVファイルを読み込む
    meeting_info, participants_info = read_csv(input_file)

    # 表記の揺れている名前を統一
    modifyed_participants_info = modify_participant_names(participants_info)

    # 重複している名前を削除
    modifyed_participants_info = list({participant['名前 (元の名前)']: participant for participant in modifyed_participants_info}.values())
    
    # 重複を排除した名前をファイルに出力
    intermediate_file = config.get('DEFAULT', 'intermediate_file')
    sorted_participants_info = sorted(modifyed_participants_info, key=lambda x: x['名前 (元の名前)'])
    pd.DataFrame(sorted_participants_info).to_csv(intermediate_file, index=False)

    # 集計
    participant_map = analyze_participants(modifyed_participants_info)

    # 集計結果をファイルに出力 
    output_file = config.get('DEFAULT','result_file')
    pd.DataFrame(participant_map.items(), columns=['部署名', '参加人数']).to_csv(output_file, index=False)
    
    # 集計結果を表示
    print("集計結果:")
    for key, value in participant_map.items():
        print(key, value)
