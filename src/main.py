import pandas as pd

import os
import configparser

# グローバル変数としてconfigを定義
config = None

def read_properties(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def read_csv(file_path):
    # CSVファイル全体を読み込む
    meeting_info_df = pd.read_csv(file_path, encoding='utf-8', nrows=2)
    
    # ミーティング情報を取得
    meeting_info = meeting_info_df.iloc[0].to_dict()
    
    # 参加者情報を取得
    participant_df = pd.read_csv(file_path, encoding='utf-8', skiprows=3)
    participants_info = participant_df.iloc[4:].dropna(how='all').to_dict(orient='records')
    
    return meeting_info, participants_info

def analyze_participants(participants_info):

    # 参加者の辞書を定義
    participant_map = {}  

    # 1項目目の値を取得
    for participant in participants_info:

        print(participant['名前 (元の名前)'])

        # "_"で分割
        participant_info = participant['名前 (元の名前)'].split("_") 

        # 1項目目をキーにして件数をカウントアップ
        if participant_info[0] in participant_map:
            participant_map[participant_info[0]] += 1
        else:
            participant_map[participant_info[0]] = 1

    # 集計結果をソートして返却
    return dict(sorted(participant_map.items(), key=lambda x: x[0]))

def modify_participant_names(participants_info):
        # 表記の揺れている名前を統一するための辞書を定義
        replace_name_dict = {
            "‗": "_",
            " ": "_",
        }

        # 参加者情報を修正
        for participant in participants_info:
            for key, value in replace_name_dict.items():
                participant['名前 (元の名前)'] = participant['名前 (元の名前)'].replace(key, value)

        return participants_info

if __name__ == "__main__":

    # プロパティファイルのパス
    properties_file = 'config/config.properties'
    
    # プロパティファイルを読み込む
    config = read_properties(properties_file)

    # ファイルパスを指定
    input_file = os.path.join('data', 'input', '202409_zoom_participants_.csv')

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
