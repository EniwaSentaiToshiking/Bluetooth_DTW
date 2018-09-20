import serial
from timeout_decorator import timeout, TimeoutError
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import glob

#*********** Bluetooth イニシャライザ *************#
@timeout(0.1)
def serial_read(robo):
    return robo.readline().decode('ascii')

#******* マッチング *******#
def get_dtw_distances(input_data):
    train_files = sorted(glob.glob("./train/*.csv"))
    distances = []
    
    for train_file in train_files:
        train_data = np.loadtxt(train_file, delimiter=',')
        distance, path = fastdtw(input_data, train_data, dist=euclidean)
        distances.append(distance)

    return distances

#******* クラスタリング *******#
def clustering(distances):
    return distances.index(min(distances)) / 3, min(distances)

#*********** main関数 *************#

if __name__ == '__main__':

    #******* Bluetooth機器接続 *******#
    print('try to connect')
    
    try:
        ser = serial.Serial('/dev/tty.Mindstorms-SerialPortPr', 115200)
            # tty.MindstormsEV3-SerialPor,tty.Mindstorms-SerialPortPr
    except :
        ser = ''

    input_buffer = [] #データ取得バッファ

    #***** データ取得 *****#
    while True:
        line = ''
        # BlueToothでロボットから送られてくるデータの読み込み
        try:
            line = serial_read(ser)
            print('OK')
        except TimeoutError:
            print('None')
        except :
            print('Not Connect')

        if not line:
            continue

        line = line.strip()

        if line == '.':  # 終端文字が送られてきた場合
            break
        else:
            input_buffer.append(int(line))

    #****** 推定 d*******#
    print('recognition')
    input_data = np.array(input_buffer)
    distances = get_dtw_distances(input_data)
    number, distance = clustering(distances)

    #****** 送信 *******#
    print('send: ', int(number))
    print('distance:', distance)
    send_data = str(int(number))
    ser.write(send_data.encode('ascii'))
    ser.close()

    print('end')
