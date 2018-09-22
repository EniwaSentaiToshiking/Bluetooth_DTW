import serial
from timeout_decorator import timeout, TimeoutError
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import glob
from joblib import Parallel, delayed


# *********** Bluetooth イニシャライザ *************#
@timeout(0.1)
def serial_read(robo):
    return robo.readline().decode('ascii')


# ******* マッチング *******#
def get_dtw_distance(train_file, input_data):
    train_data = np.loadtxt(train_file, delimiter=',')
    distance, path = fastdtw(input_data, train_data, dist=euclidean)
    return distance


# ******* クラスタリング *******#
def clustering(distances, train_files):
    dists = np.array(distances)
    dists = dists.argsort()
    print(dists)
    dist1 = dists[0]
    dist2 = dists[1]
    dist3 = dists[2]
    print(dist1, dist2, dist3)
    num1 = int(train_files[dist1][8])
    num2 = int(train_files[dist2][8])
    num3 = int(train_files[dist3][8])
    print(num1, num2, num3)
    return num1, dist1


# *********** main関数 *************#

if __name__ == '__main__':
    fs = open("analog.csv", "w")

    # ******* Bluetooth機器接続 *******#
    print('try to connect')

    try:
        ser = serial.Serial('/dev/tty.MindstormsEV3-SerialPor', 115200)
        # tty.MindstormsEV3-SerialPor,tty.Mindstorms-SerialPortPr
    except:
        ser = ''

    input_buffer = []  # データ取得バッファ

    # #***** データ取得 *****#
    while True:
        line = ''
        # BlueToothでロボットから送られてくるデータの読み込み
        try:
            line = serial_read(ser)
            print('OK')
        except TimeoutError:
            print('None')
        except:
            print('Not Connect')

        if not line:
            continue

        line = line.strip()

        if line == '.':  # 終端文字が送られてきた場合
            fs.close()
            break
        else:
            fs.write(line + "\n")
            input_buffer.append(int(line))

    # ****** 推定 *******#
    print('recognition')
    train_files = sorted(glob.glob("./train/*.csv"))
    input_data = np.array(input_buffer)
    distances = Parallel(n_jobs=-1)([delayed(get_dtw_distance)(train_file, input_data) for train_file in train_files])
    number, distance = clustering(distances, train_files)

    # ****** 送信 *******#
    print('send: ', int(number))
    print('distance:', distance)
    send_data = str(int(number))
    ser.write(send_data.encode('ascii'))
    ser.close()

    print('end')
